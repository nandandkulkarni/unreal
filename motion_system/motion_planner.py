"""
Motion Planner - Pass 1: Convert motion commands to keyframe data

Takes high-level motion commands and calculates exact positions, times, and keyframes.
Outputs structured keyframe data ready for Unreal application.
"""
import math
import unreal
from .logger import log
from .motion_includes import mannequin_setup
from .motion_includes import camera_setup
from .motion_includes import sequence_setup
from .motion_includes import light_setup


def plan_motion(motion_plan, actors_info, fps, sequence=None):
    """
    Convert motion commands to keyframe data
    
    Args:
        motion_plan: List of command dicts with "actor" and "command" fields
        actors_info: Dict of actor_name -> {"location": Vector, "rotation": Rotator}
        fps: Frames per second
        
    Returns:
        Dict of actor_name -> keyframe_data
    """
    log("\n" + "="*60)
    log("MOTION PLANNER - Pass 1: Commands → Keyframes")
    log("="*60)
    
    # Initialize state for each actor
    actor_states = {}
    for actor_name, info in actors_info.items():
        actor_states[actor_name] = {
            "current_time": 0.0,
            "current_pos": {"x": info["location"].x, "y": info["location"].y, "z": info["location"].z},
            "current_rotation": {"pitch": info["rotation"].pitch, "yaw": info["rotation"].yaw, "roll": info["rotation"].roll},
            "yaw_offset": info.get("yaw_offset", 0.0),
            "current_animation": None,
            "waypoints": {},
            "keyframes": {
                "location": [],
                "rotation": [],
                "animations": []
            }
        }
    
    # Ensure camera keyframes structure exists if there are camera commands
    if any(c["command"] == "camera_move" for c in motion_plan):
        if "camera" not in actor_states:
            actor_states["camera"] = {
                "current_time": 0.0,
                "keyframes": {
                    "location": [],
                    "animations": []
                }
            }
    
    # Track camera cuts
    camera_cuts = []
    
    # Process each command sequentially
    for i, cmd in enumerate(motion_plan):
        command_type = cmd["command"]
        
        # Handle creation commands (don't require existing state)
        if command_type == "add_actor":
            process_add_actor(cmd, actors_info, actor_states, sequence, fps)
            continue
        elif command_type == "add_camera":
            process_add_camera(cmd, actors_info, actor_states, sequence, fps)
            continue
        elif command_type == "add_directional_light":
            process_add_directional_light(cmd, actors_info)
            continue
        elif command_type == "camera_cut":
            process_camera_cut(cmd, camera_cuts)
            continue

        actor_name = cmd.get("actor")
        if not actor_name or actor_name not in actor_states:
            log(f"⚠ Command {i}: Unknown actor '{actor_name}', skipping")
            continue
        
        state = actor_states[actor_name]
        
        log(f"\n[{i}] Actor '{actor_name}': {command_type}")
        
        if command_type == "move_by_distance":
            process_move_by_distance(cmd, state, fps)
        elif command_type == "move_for_seconds":
            process_move_for_seconds(cmd, state, fps)
        elif command_type == "move_to_location":
            process_move_to_location(cmd, state, fps)
        elif command_type == "move_to_waypoint":
            process_move_to_waypoint(cmd, state, fps)
        elif command_type == "move_and_turn":
            process_move_and_turn(cmd, state, fps)
        elif command_type == "turn_by_direction":
            process_turn_by_direction(cmd, state, fps)
        elif command_type == "turn_by_degree":
            process_turn_by_degree(cmd, state, fps)
        elif command_type == "turn_left":
            process_turn_left(cmd, state, fps)
        elif command_type == "turn_right":
            process_turn_right(cmd, state, fps)
        elif command_type == "face":
            process_face(cmd, state, fps)
        elif command_type == "animation":
            process_animation(cmd, state, fps)
        elif command_type == "wait":
            process_wait(cmd, state, fps)
        elif command_type == "camera_move":
            process_camera_move(cmd, state, fps)
        elif command_type == "camera_look_at":
            process_camera_look_at(cmd, actors_info)
        elif command_type == "add_actor":
            process_add_actor(cmd, actors_info, actor_states, sequence, fps)
        elif command_type == "add_camera":
            process_add_camera(cmd, actors_info, actor_states, sequence, fps)
        else:
            log(f"  ⚠ Unknown command type: {command_type}")
    
    # Finalize any open animations
    for actor_name, state in actor_states.items():
        if state["current_animation"] and state["current_animation"]["end_frame"] is None:
            final_frame = int(state["current_time"] * fps)
            state["current_animation"]["end_frame"] = final_frame
            log(f"  ✓ Finalized animation '{state['current_animation']['name']}' to frame {final_frame}")
    
    # Convert to output format
    result = {}
    for actor_name, state in actor_states.items():
        result[actor_name] = {
            "keyframes": state["keyframes"],
            "waypoints": state["waypoints"]
        }
        log(f"\n✓ {actor_name}: {len(state['keyframes']['location'])} location keys, {len(state['keyframes']['animations'])} anim sections")
    
    return result, camera_cuts


def get_cardinal_angle(direction, offset=None):
    """Get absolute world angle for a cardinal direction string"""
    if offset is None:
        # If no offset is given, compound directions (north_east) default to perfect diagonal (45)
        offset = 45 if "_" in direction else 0
        
    # Absolute Cardinal Mappings (Degrees in Unreal: North=0, East=90, South=180, West=-90)
    cardinal_angles = {
        "north": 0,
        "east": 90,
        "south": 180,
        "west": -90,
        "north_east": 0 + offset,   # Offset from North (0) toward East (+90)
        "north_west": 0 - offset,   # Offset from North (0) toward West (-90)
        "south_east": 180 - offset, # Offset from South (180) toward East (+90)
        "south_west": 180 + offset, # Offset from South (180) toward West (-90)
        "east_north": 90 - offset,  # Offset from East (90) toward North (0)
        "east_south": 90 + offset,  # Offset from East (90) toward South (180)
        "west_north": -90 + offset, # Offset from West (-90) toward North (0)
        "west_south": -90 - offset  # Offset from West (-90) toward South (-180)
    }
    
    return cardinal_angles.get(direction)


def get_shortest_path_yaw(current_yaw, target_yaw):
    """Calculate target yaw that minimizes rotation distance from current_yaw"""
    delta = (target_yaw - current_yaw) % 360
    if delta > 180:
        delta -= 360
    return current_yaw + delta


def get_speed_cm_per_sec(cmd):
    """Convert speed to cm/s"""
    if "speed_mph" in cmd:
        return cmd["speed_mph"] * 44.704  # mph to cm/s
    elif "speed_mtps" in cmd:
        return cmd["speed_mtps"] * 100  # m/s to cm/s
    elif "speed_mps" in cmd:  # Legacy support
        return cmd["speed_mps"] * 100  # m/s to cm/s
    else:
        log("  ⚠ No speed specified, using default 100 cm/s")
        return 100.0


def calculate_direction_vector(direction, yaw_degrees, offset=None):
    """Calculate movement vector from direction and current yaw/offset"""
    cardinal_angle = get_cardinal_angle(direction, offset)
    
    if cardinal_angle is not None:
        angle_rad = math.radians(cardinal_angle)
        return {"x": math.cos(angle_rad), "y": math.sin(angle_rad)}
    
    yaw_rad = math.radians(yaw_degrees)
    forward_x = math.cos(yaw_rad)
    forward_y = math.sin(yaw_rad)
    
    if direction == "forward":
        return {"x": forward_x, "y": forward_y}
    elif direction == "backward":
        return {"x": -forward_x, "y": -forward_y}
    elif direction == "left":
        return {"x": -forward_y, "y": forward_x}  # 90° left
    elif direction == "right":
        return {"x": forward_y, "y": -forward_x}  # 90° right
    else:
        log(f"  ⚠ Unknown direction: {direction}")
        return {"x": forward_x, "y": forward_y}


def add_location_keyframe(state, frame, pos):
    """Add location keyframe"""
    state["keyframes"]["location"].append({
        "frame": frame,
        "x": pos["x"],
        "y": pos["y"],
        "z": pos["z"]
    })


def add_rotation_keyframe(state, frame, rot):
    """Add rotation keyframe with character yaw offset applied"""
    yaw_offset = state.get("yaw_offset", 0.0)
    
    state["keyframes"]["rotation"].append({
        "frame": frame,
        "pitch": rot["pitch"],
        "yaw": rot["yaw"] + yaw_offset,
        "roll": rot["roll"]
    })


def process_move_by_distance(cmd, state, fps):
    """Move by distance over calculated time"""
    direction = cmd.get("direction", "forward")
    distance_m = cmd.get("meters", 0)
    distance_cm = distance_m * 100
    speed_cm_s = get_speed_cm_per_sec(cmd)
    
    offset = cmd.get("offset")
    duration_sec = distance_cm / speed_cm_s
    
    # Calculate new position
    dir_vec = calculate_direction_vector(direction, state["current_rotation"]["yaw"], offset)
    new_pos = {
        "x": state["current_pos"]["x"] + dir_vec["x"] * distance_cm,
        "y": state["current_pos"]["y"] + dir_vec["y"] * distance_cm,
        "z": cmd.get("z", state["current_pos"]["z"])
    }
    
    # Add keyframes
    start_frame = int(state["current_time"] * fps)
    end_frame = int((state["current_time"] + duration_sec) * fps)
    
    add_location_keyframe(state, start_frame, state["current_pos"])
    add_location_keyframe(state, end_frame, new_pos)
    add_rotation_keyframe(state, start_frame, state["current_rotation"])
    
    log(f"  {direction} {distance_m}m @ {speed_cm_s/100:.1f}m/s = {duration_sec:.2f}s ({start_frame}-{end_frame})")
    log(f"  Position: ({new_pos['x']:.1f}, {new_pos['y']:.1f}, {new_pos['z']:.1f})")
    
    # Update state
    state["current_pos"] = new_pos
    state["current_time"] += duration_sec
    
    # Waypoint
    if "waypoint_name" in cmd:
        state["waypoints"][cmd["waypoint_name"]] = new_pos.copy()
        log(f"  ✓ Waypoint '{cmd['waypoint_name']}' created")


def process_move_for_seconds(cmd, state, fps):
    """Move for specified seconds"""
    direction = cmd.get("direction", "forward")
    duration_sec = cmd.get("seconds", 1)
    speed_cm_s = get_speed_cm_per_sec(cmd)
    
    offset = cmd.get("offset")
    distance_cm = speed_cm_s * duration_sec
    
    # Calculate new position
    dir_vec = calculate_direction_vector(direction, state["current_rotation"]["yaw"], offset)
    new_pos = {
        "x": state["current_pos"]["x"] + dir_vec["x"] * distance_cm,
        "y": state["current_pos"]["y"] + dir_vec["y"] * distance_cm,
        "z": cmd.get("z", state["current_pos"]["z"])
    }
    
    # Add keyframes
    start_frame = int(state["current_time"] * fps)
    end_frame = int((state["current_time"] + duration_sec) * fps)
    
    add_location_keyframe(state, start_frame, state["current_pos"])
    add_location_keyframe(state, end_frame, new_pos)
    add_rotation_keyframe(state, start_frame, state["current_rotation"])
    
    log(f"  {direction} for {duration_sec}s @ {speed_cm_s/100:.1f}m/s = {distance_cm/100:.1f}m")
    
    state["current_pos"] = new_pos
    state["current_time"] += duration_sec
    
    if "waypoint_name" in cmd:
        state["waypoints"][cmd["waypoint_name"]] = new_pos.copy()


def process_move_to_location(cmd, state, fps):
    """Move to absolute location"""
    target = cmd.get("target")
    if not target:
        log("  ⚠ No target specified")
        return
    
    target_pos = {"x": target[0], "y": target[1], "z": target[2]}
    
    # Calculate distance
    dx = target_pos["x"] - state["current_pos"]["x"]
    dy = target_pos["y"] - state["current_pos"]["y"]
    dz = target_pos["z"] - state["current_pos"]["z"]
    distance_cm = math.sqrt(dx*dx + dy*dy + dz*dz)
    
    speed_cm_s = get_speed_cm_per_sec(cmd)
    duration_sec = distance_cm / speed_cm_s
    
    start_frame = int(state["current_time"] * fps)
    end_frame = int((state["current_time"] + duration_sec) * fps)
    
    add_location_keyframe(state, start_frame, state["current_pos"])
    add_location_keyframe(state, end_frame, target_pos)
    add_rotation_keyframe(state, start_frame, state["current_rotation"])
    
    log(f"  To ({target_pos['x']:.1f}, {target_pos['y']:.1f}, {target_pos['z']:.1f}) = {distance_cm/100:.1f}m in {duration_sec:.2f}s")
    
    state["current_pos"] = target_pos
    state["current_time"] += duration_sec
    
    if "waypoint_name" in cmd:
        state["waypoints"][cmd["waypoint_name"]] = target_pos.copy()


def process_move_to_waypoint(cmd, state, fps):
    """Move to named waypoint"""
    waypoint_name = cmd.get("waypoint")
    if waypoint_name not in state["waypoints"]:
        log(f"  ⚠ Waypoint '{waypoint_name}' not found")
        return
    
    target_pos = state["waypoints"][waypoint_name]
    cmd_modified = cmd.copy()
    cmd_modified["target"] = (target_pos["x"], target_pos["y"], target_pos["z"])
    process_move_to_location(cmd_modified, state, fps)


def process_move_and_turn(cmd, state, fps):
    """Simultaneous move and turn"""
    # Process movement
    process_move_by_distance(cmd, state, fps)
    
    # Add turn on same timeframe
    turn_degrees = cmd.get("turn_degrees", 0)
    new_yaw = state["current_rotation"]["yaw"] + turn_degrees
    
    end_frame = int(state["current_time"] * fps)
    state["current_rotation"]["yaw"] = new_yaw
    add_rotation_keyframe(state, end_frame, state["current_rotation"])
    
    log(f"  + Turn {turn_degrees}° → yaw={new_yaw:.1f}°")


def process_turn_by_degree(cmd, state, fps):
    """Turn relative to current yaw"""
    degrees = cmd.get("degrees", 0)
    duration_sec = cmd.get("duration", 2.0)
    
    start_frame = int(state["current_time"] * fps)
    end_frame = int((state["current_time"] + duration_sec) * fps)
    
    old_yaw = state["current_rotation"]["yaw"]
    new_yaw = old_yaw + degrees
    
    new_rot = state["current_rotation"].copy()
    new_rot["yaw"] = new_yaw
    
    add_rotation_keyframe(state, start_frame, state["current_rotation"])
    add_rotation_keyframe(state, end_frame, new_rot)
    
    log(f"  Turn {degrees}° in {duration_sec:.2f}s   yaw={new_yaw:.1f}°")
    
    state["current_rotation"] = new_rot
    state["current_time"] += duration_sec


def process_turn_left(cmd, state, fps):
    """Shorthand for turning left (minus yaw)"""
    degrees = cmd.get("degrees", 90)
    cmd["degrees"] = -degrees  # Left is negative yaw in our standard coord
    process_turn_by_degree(cmd, state, fps)


def process_turn_right(cmd, state, fps):
    """Shorthand for turning right (plus yaw)"""
    degrees = cmd.get("degrees", 90)
    cmd["degrees"] = degrees  # Right is positive yaw
    process_turn_by_degree(cmd, state, fps)


def process_animation(cmd, state, fps):
    """Change animation"""
    anim_name = cmd.get("name")
    if not anim_name:
        log("  ⚠ No animation name specified")
        return
    
    current_frame = int(state["current_time"] * fps)
    
    # End previous animation if exists
    if state["current_animation"]:
        state["current_animation"]["end_frame"] = current_frame
    
    # Start new animation
    new_anim = {
        "name": anim_name,
        "start_frame": current_frame,
        "end_frame": None  # Will be set when next animation starts or at end
    }
    state["keyframes"]["animations"].append(new_anim)
    state["current_animation"] = new_anim
    
    log(f"  Animation: {anim_name} from frame {current_frame}")


def process_face(cmd, state, fps):
    """Face an absolute world direction or degree"""
    direction = cmd.get("direction")
    offset = cmd.get("offset")
    duration_sec = cmd.get("duration", 1.0) # Faster than move usually
    
    target_yaw = 0
    if direction:
        angle = get_cardinal_angle(direction, offset)
        if angle is not None:
            target_yaw = angle
        else:
            log(f"  ⚠ Unknown direction for face: {direction}")
            return
    elif "degrees" in cmd:
        target_yaw = cmd["degrees"]
    else:
        log("  ⚠ face command missing direction or degrees")
        return

    start_frame = int(state["current_time"] * fps)
    end_frame = int((state["current_time"] + duration_sec) * fps)
    
    # Shortest path!
    target_yaw = get_shortest_path_yaw(state["current_rotation"]["yaw"], target_yaw)
    
    new_rot = state["current_rotation"].copy()
    new_rot["yaw"] = target_yaw
    
    add_rotation_keyframe(state, start_frame, state["current_rotation"])
    add_rotation_keyframe(state, end_frame, new_rot)
    
    log(f"  Face {direction or target_yaw}° in {duration_sec:.2f}s (Adjusted Target: {target_yaw:.1f}°)")
    
    state["current_rotation"] = new_rot
    state["current_time"] += duration_sec


def process_wait(cmd, state, fps):
    """Wait/pause for seconds"""
    duration_sec = cmd.get("seconds", 1)
    
    # Add keyframes to hold position
    start_frame = int(state["current_time"] * fps)
    end_frame = int((state["current_time"] + duration_sec) * fps)
    
    add_location_keyframe(state, start_frame, state["current_pos"])
    add_location_keyframe(state, end_frame, state["current_pos"])
    add_rotation_keyframe(state, start_frame, state["current_rotation"])
    add_rotation_keyframe(state, end_frame, state["current_rotation"])
    
    log(f"  Wait {duration_sec}s ({start_frame}-{end_frame})")
    
    state["current_time"] += duration_sec


def process_camera_move(cmd, state, fps):
    """Move camera with location and rotation"""
    location = cmd.get("location")
    rotation = cmd.get("rotation")
    duration_sec = cmd.get("duration", 2.0)
    
    if not location or not rotation:
        log("  ⚠ Camera move missing location or rotation")
        return
        
    start_frame = int(state["current_time"] * fps)
    end_frame = int((state["current_time"] + duration_sec) * fps)
    
    # Add start keyframes (current position)
    add_location_keyframe(state, start_frame, state["current_pos"])
    add_rotation_keyframe(state, start_frame, state["current_rotation"])
    
    # Update state
    target_pos = {"x": location[0], "y": location[1], "z": location[2]}
    target_rot = {"pitch": rotation[0], "yaw": rotation[1], "roll": rotation[2]}
    
    state["current_pos"] = target_pos
    state["current_rotation"] = target_rot
    state["current_time"] += duration_sec
    
    # Add end keyframes (new position)
    add_location_keyframe(state, end_frame, state["current_pos"])
    add_rotation_keyframe(state, end_frame, state["current_rotation"])
    
    log(f"  Camera move to ({target_pos['x']}, {target_pos['y']}, {target_pos['z']}) in {duration_sec}s")


def process_camera_look_at(cmd, actors_info):
    """Enable LookAt tracking for a camera targeting another actor"""
    camera_name = cmd.get("actor", "test_camera")
    target_name = cmd.get("target") or cmd.get("look_at_actor")
    
    if not target_name:
        log("  ⚠ No target specified for camera_look_at")
        return
        
    if camera_name not in actors_info or target_name not in actors_info:
        log(f"  ⚠ Camera '{camera_name}' or Target '{target_name}' not found")
        return
        
    camera_actor = actors_info[camera_name]["actor"]
    target_actor = actors_info[target_name]["actor"]
    
    # Process optional cinematic settings
    offset = None
    if "offset" in cmd:
        o = cmd["offset"]
        offset = unreal.Vector(o[0], o[1], o[2])
        
    interp_speed = cmd.get("interp_speed", 0.0)
    
    camera_setup.enable_lookat_tracking(camera_actor, target_actor, offset, interp_speed)


def process_add_actor(cmd, actors_info, actor_states, sequence, fps):
    """Add a new actor to the scene and sequence"""
    actor_name = cmd.get("actor")
    if not actor_name:
        log("  ⚠ Add actor missing name")
        return
        
    if actor_name in actors_info:
        log(f"  ℹ Actor '{actor_name}' already exists, skipping creation")
        
        # Ensure state exists even if actor exists (if referenced first time here)
        if actor_name not in actor_states:
            init_actor_state(actor_name, actors_info[actor_name], actor_states)
        return

    # Check if we have the sequence to add to
    if not sequence:
        log("  ⚠ Cannot add actor: No sequence provided to plan_motion")
        return

    log(f"  Creating actor '{actor_name}'...")
    
    # Extract properties
    location_vec = unreal.Vector(0, 0, 0)
    if "location" in cmd:
        loc = cmd["location"]
        location_vec = unreal.Vector(loc[0], loc[1], loc[2])
        
    rotation_rot = unreal.Rotator(pitch=0, yaw=0, roll=0)
    if "rotation" in cmd:
        rot = cmd["rotation"]
        # Standardize on [Pitch, Yaw, Roll] from JSON
        rotation_rot = unreal.Rotator(pitch=rot[0], yaw=rot[1], roll=rot[2])
        
    mesh_path = cmd.get("mesh_path")
    yaw_offset = cmd.get("yaw_offset", 0.0)
    
    mesh_rotation = None
    if "mesh_rotation" in cmd:
        mr = cmd["mesh_rotation"]
        mesh_rotation = unreal.Rotator(pitch=mr[0], yaw=mr[1], roll=mr[2])
    elif yaw_offset != 0:
        # If yaw_offset is provided but no mesh_rotation, create a rotator for it
        mesh_rotation = unreal.Rotator(pitch=0.0, yaw=yaw_offset, roll=0.0)
    
    # create_mannequin can accept mesh_path and mesh_rotation
    actor = mannequin_setup.create_mannequin(actor_name, location_vec, rotation_rot, mesh_path, mesh_rotation)
    
    if actor:
        # Visual Aid: Add colored axis at the spawn point
        mannequin_setup.add_axis_origin(location_vec)
    
    if not actor:
        log(f"  ✗ Failed to create actor '{actor_name}'")
        return
        
    # Add to sequence
    binding = sequence_setup.add_actor_to_sequence(sequence, actor, actor_name)
    
    if not binding:
        log(f"  ✗ Failed to bind actor '{actor_name}' to sequence")
        return
        
    # Update actors_info
    actors_info[actor_name] = {
        "location": location_vec,
        "rotation": rotation_rot,
        "yaw_offset": yaw_offset,
        "actor": actor,
        "binding": binding
    }
    
    # Initialize state
    init_actor_state(actor_name, actors_info[actor_name], actor_states)
    log(f"  ✓ Actor '{actor_name}' added successfully")
    log(f"    Initial State -> Pos: {actors_info[actor_name]['location']}, Rot: {actors_info[actor_name]['rotation']}")


def process_add_camera(cmd, actors_info, actor_states, sequence, fps):
    """Add a new camera to the scene and sequence"""
    camera_name = cmd.get("actor", "camera")
    
    if camera_name in actors_info:
        log(f"  ℹ Camera '{camera_name}' already exists")
        if camera_name not in actor_states:
            init_actor_state(camera_name, actors_info[camera_name], actor_states)
        return

    if not sequence:
        log("  ⚠ Cannot add camera: No sequence provided")
        return

    log(f"  Creating camera '{camera_name}'...")
    
    # Extract FOV and tint if specified
    fov = cmd.get("fov", 90.0)
    tint = cmd.get("tint", None)
    
    camera_actor = camera_setup.create_camera("CineCameraActor", fov=fov, tint=tint)
    
    # Rename if possible/needed (camera_setup creates it with default name usually, 
    # but we can try to rename or just track it by our internal name)
    if camera_actor:
        camera_actor.set_actor_label(camera_name)
        
    if "location" in cmd:
        loc = cmd["location"]
        camera_actor.set_actor_location(unreal.Vector(loc[0], loc[1], loc[2]), False, True)
        
    if "rotation" in cmd:
        rot = cmd["rotation"]
        camera_actor.set_actor_rotation(unreal.Rotator(pitch=rot[0], yaw=rot[1], roll=rot[2]), False)

    # Add to sequence
    binding = sequence_setup.add_actor_to_sequence(sequence, camera_actor, camera_name)
    
    # Reset to spawnable if needed? camera_setup creates spawnable usually? 
    # ACTUALLY camera_setup.create_camera likely creates a requested actor.
    # sequence_setup.add_actor_to_sequence adds it as possessable usually.
    
    actors_info[camera_name] = {
        "location": camera_actor.get_actor_location(),
        "rotation": camera_actor.get_actor_rotation(),
        "actor": camera_actor,
        "binding": binding
    }
    
    # Initialize state
    init_actor_state(camera_name, actors_info[camera_name], actor_states)
    log(f"  ✓ Camera '{camera_name}' added successfully")
    
    # Handle look_at_actor if specified in creation
    if "look_at_actor" in cmd:
        target_name = cmd["look_at_actor"]
        if target_name in actors_info:
            # Re-use process_camera_look_at logic
            process_camera_look_at(cmd, actors_info)
        else:
            log(f"  ⚠ Cannot track '{target_name}': actor not yet created")


def init_actor_state(actor_name, info, actor_states):
    """Helper to initialize state for dynamically added actors"""
    if actor_name in actor_states:
        return

    # Use default 0 if info missing components (unlikely if we just created it)
    loc = info.get("location", unreal.Vector(0,0,0))
    rot = info.get("rotation", unreal.Rotator(pitch=0, yaw=0, roll=0))
    
    actor_states[actor_name] = {
        "current_time": 0.0,
        "current_pos": {"x": loc.x, "y": loc.y, "z": loc.z},
        "current_rotation": {"pitch": rot.pitch, "yaw": rot.yaw, "roll": rot.roll},
        "yaw_offset": info.get("yaw_offset", 0.0),
        "current_animation": None,
        "waypoints": {},
        "keyframes": {
            "location": [],
            "rotation": [],
            "animations": []
        }
    }


def process_add_directional_light(cmd, actors_info):
    """Add a directional light to the scene"""
    light_name = cmd.get("actor", "DirectionalLight")
    
    if light_name in actors_info:
        log(f"  ℹ Light '{light_name}' already exists, skipping creation")
        return
    
    log(f"  Creating directional light '{light_name}'...")
    
    # Extract parameters
    from_direction = cmd.get("from", "north")
    angle = cmd.get("angle", "medium")
    direction_offset = cmd.get("direction_offset", 0)
    angle_offset = cmd.get("angle_offset", 0)
    intensity = cmd.get("intensity", "normal")
    color = cmd.get("color", "white")
    cast_shadows = cmd.get("cast_shadows", True)
    atmosphere_sun = cmd.get("atmosphere_sun", True)
    
    # Create the light
    light_actor = light_setup.create_directional_light(
        name=light_name,
        from_direction=from_direction,
        angle=angle,
        direction_offset=direction_offset,
        angle_offset=angle_offset,
        intensity=intensity,
        color=color,
        cast_shadows=cast_shadows,
        atmosphere_sun=atmosphere_sun
    )
    
    if light_actor:
        # Store in actors_info for potential future reference
        actors_info[light_name] = {
            "location": light_actor.get_actor_location(),
            "rotation": light_actor.get_actor_rotation(),
            "actor": light_actor
        }
        log(f"  ✓ Light '{light_name}' added successfully")
    else:
        log(f"  ✗ Failed to create light '{light_name}'")


def process_camera_cut(cmd, camera_cuts):
    """Process camera_cut command"""
    camera_name = cmd.get("camera")
    at_time = cmd.get("at_time", 0.0)
    
    if not camera_name:
        log("  ⚠ camera_cut command missing 'camera' parameter")
        return
    
    camera_cuts.append({
        "camera": camera_name,
        "time": at_time
    })
    
    log(f"  ✓ Camera cut: {camera_name} at {at_time}s")
