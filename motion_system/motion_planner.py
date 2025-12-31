"""
Motion Planner - Pass 1: Convert motion commands to keyframe data

Takes high-level motion commands and calculates exact positions, times, and keyframes.
Outputs structured keyframe data ready for Unreal application.
"""
import math
try:
    import unreal
except ImportError:
    import unreal_mock as unreal
from logger import log
from motion_includes import mannequin_setup
from motion_includes import camera_setup
from motion_includes import sequence_setup
from motion_includes import light_setup


def save_planning_debug(pass_name, actor_states, camera_cuts, scene_name="movie"):
    """Save intermediate planning data for debugging"""
    import json
    import os
    
    # Convert actor_states to JSON-serializable format
    debug_data = {
        "pass": pass_name,
        "actors": {},
        "camera_cuts": camera_cuts
    }
    
    log(f"DEBUG save_planning_debug: actor_states keys = {list(actor_states.keys())}")
    
    for actor_name, state in actor_states.items():
        debug_data["actors"][actor_name] = {
            "keyframes": state.get("keyframes", {}),
            "look_at_timeline": state.get("look_at_timeline", []),
            "focus_timeline": state.get("focus_timeline", []),
            "frame_subject_timeline": state.get("frame_subject_timeline", [])
        }
    
    log(f"DEBUG save_planning_debug: Saving {len(debug_data['actors'])} actors to {pass_name}")
    
    # Use absolute path to motion_system/dist folder
    script_dir = r"C:\UnrealProjects\Coding\unreal\motion_system"
    output_path = os.path.join(script_dir, "dist", f"{scene_name}_{pass_name}.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(debug_data, f, indent=2)
    
    log(f"✓ Debug saved: {output_path}")





def calculate_focal_length(camera_pos, subject_pos, subject_height=1.8, coverage=0.7, sensor_height=24.0):
    """
    Calculate required focal length to frame subject at desired coverage.
    
    Args:
        camera_pos: (x, y, z) camera location in cm
        subject_pos: (x, y, z) subject location in cm
        subject_height: Height of subject in meters (default 1.8m for human)
        coverage: 0.0-1.0, how much of frame height subject should fill
        sensor_height: Camera sensor height in mm (default 24mm full frame)
    
    Returns:
        focal_length in mm
    """
    # Calculate distance in meters
    dx = (subject_pos[0] - camera_pos[0]) / 100.0
    dy = (subject_pos[1] - camera_pos[1]) / 100.0
    dz = (subject_pos[2] - camera_pos[2]) / 100.0
    distance = math.sqrt(dx*dx + dy*dy + dz*dz)
    
    # Avoid division by zero
    if distance < 0.1:
        distance = 0.1
    
    # Subject dimensions (human proportions)
    # Width is approximately 1/3 of height for a person
    subject_width = subject_height / 3.0
    
    # Calculate required frame dimensions for desired coverage
    # We want the subject to occupy 'coverage' of the frame
    frame_height_needed = subject_height / coverage if coverage > 0 else subject_height
    
    # For width, we need to account for aspect ratio (16:9 typical)
    # Frame width = frame height * (16/9) for landscape orientation
    sensor_width = sensor_height * (16.0 / 9.0)  # ~42.67mm for 24mm sensor
    frame_width_needed = subject_width / coverage if coverage > 0 else subject_width
    
    # Calculate FOV needed for both dimensions
    fov_height_radians = 2 * math.atan(frame_height_needed / (2 * distance))
    fov_width_radians = 2 * math.atan(frame_width_needed / (2 * distance))
    
    # Calculate focal length for both dimensions
    # focal_length = sensor_size / (2 * tan(fov/2))
    focal_length_height = sensor_height / (2 * math.tan(fov_height_radians / 2))
    focal_length_width = sensor_width / (2 * math.tan(fov_width_radians / 2))
    
    # Use the LARGER focal length (more zoomed in) to ensure subject fits in both dimensions
    focal_length = max(focal_length_height, focal_length_width)
    
    return focal_length


def plan_motion(motion_plan, actors_info, fps, sequence=None, scene_name="movie"):
    """
    Convert motion commands to keyframe data
    
    Args:
        motion_plan: List of command dicts with "actor" and "command" fields
        actors_info: Dict of actor_name -> {"location": Vector, "rotation": Rotator}
        fps: Frames per second
        scene_name: Name of the scene for debug output
        
    Returns:
        Dict of actor_name -> keyframe_data
    """
    log("\n" + "="*60)
    log("MOTION PLANNER - Pass 1: Commands → Keyframes")
    log("="*60)
    
    # Setup file logging for easier debugging
    import os
    log_file_path = os.path.join(r"C:\UnrealProjects\Coding\unreal\motion_system\dist", "motion_planner.log")
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    
    def file_log(message):
        """Log to both console and file"""
        log(message)
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(f"{message}\n")
    
    # Clear previous log
    with open(log_file_path, "w", encoding="utf-8") as f:
        f.write(f"=== Motion Planner Log - {scene_name} ===\n")
    
    file_log(f"Starting motion planning for: {scene_name}")
    file_log(f"Initial actors_info keys: {list(actors_info.keys())}")
    
    # Initialize state for each actor
    actor_states = {}
    for actor_name, info in actors_info.items():
        actor_states[actor_name] = {
            "current_time": 0.0,
            "current_pos": {"x": info["location"].x, "y": info["location"].y, "z": info["location"].z},
            "current_rotation": {"pitch": info["rotation"].pitch, "yaw": info["rotation"].yaw, "roll": info["rotation"].roll},
            "yaw_offset": info.get("yaw_offset", 0.0),
            "current_animation": None,
            "current_speed": info.get("current_speed", 0.0),
            "radius": info.get("radius", 0.35),
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
    
    # Track camera cuts and pending groups
    camera_cuts = []
    pending_groups = {}  # "Group_Name" -> ["Actor1", "Actor2"]
    
    # Process each command sequentially
    for i, cmd in enumerate(motion_plan):
        command_type = cmd["command"]
        
        # Handle creation commands (don't require existing state)
        if command_type == "add_actor":
            process_add_actor(cmd, actors_info, actor_states, sequence, fps)
            continue
        elif command_type == "add_camera":
            process_add_camera(cmd, actors_info, actor_states, sequence, fps, pending_groups)
            continue
        elif command_type == "add_directional_light":
            process_add_directional_light(cmd, actors_info)
            continue
        elif command_type == "add_rect_light":
            process_add_rect_light(cmd, actors_info)
            continue
        elif command_type == "add_floor":
            process_add_floor(cmd, actors_info)
            continue
        elif command_type == "delete_lights":
            process_delete_lights(cmd)
            continue
        elif command_type == "delete_all_skylights":
            process_delete_all_skylights(cmd)
            continue
        elif command_type == "delete_all_floors":
            process_delete_all_floors(cmd)
            continue
        elif command_type == "camera_cut":
            process_camera_cut(cmd, camera_cuts)
            continue
        elif command_type == "camera_wait":
            process_camera_wait(cmd, actor_states, fps)
            continue
        elif command_type == "camera_look_at":
            process_camera_look_at(cmd, actors_info)
            continue
        elif command_type == "camera_settings":
            process_camera_settings(cmd, actors_info)
            continue

        actor_name = cmd.get("actor")
        if not actor_name or actor_name not in actor_states:
            log(f"⚠ Command {i}: Unknown actor '{actor_name}', skipping")
            continue
        
        state = actor_states[actor_name]
        
        log(f"\n[{i}] Actor '{actor_name}': {command_type}")
        
        if command_type == "move":
            process_move(cmd, state, fps)
        elif command_type == "move_by_distance":
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
        elif command_type == "add_actor":
            process_add_actor(cmd, actors_info, actor_states, sequence, fps)
        elif command_type == "add_camera":
            process_add_camera(cmd, actors_info, actor_states, sequence, fps, pending_groups)
        else:
            log(f"  ⚠ Unknown command type: {command_type}")
    
    # Finalize any open animations
    for actor_name, state in actor_states.items():
        if state["current_animation"] and state["current_animation"]["end_frame"] is None:
            final_frame = int(state["current_time"] * fps)
            state["current_animation"]["end_frame"] = final_frame
            log(f"  ✓ Finalized animation '{state['current_animation']['name']}' to frame {final_frame}")
    
    # Generate focal length keyframes for cameras with auto_frame
    for camera_name, camera_info in actors_info.items():
        if "auto_frame" in camera_info and camera_name in actor_states:
            subject_name = camera_info["auto_frame"]["subject"]
            coverage = camera_info["auto_frame"]["coverage"]
            
            if subject_name not in actor_states:
                log(f"  ⚠ Cannot generate focal length for '{camera_name}': subject '{subject_name}' not found")
                continue
            
            # Get camera and subject states
            camera_state = actor_states[camera_name]
            subject_state = actor_states[subject_name]
            
            # Get camera position (static for now)
            camera_pos = camera_state["current_pos"]
            camera_location = (camera_pos["x"], camera_pos["y"], camera_pos["z"])
            
            # Sample subject position at intervals
            subject_location_keys = subject_state["keyframes"]["location"]
            if not subject_location_keys:
                continue
            
            # Adaptive sampling: sample every 2 seconds, add keyframe if change >10%
            sample_interval = 2.0  # seconds
            change_threshold = 0.10  # 10%
            
            focal_keyframes = []
            last_focal_length = None
            
            # Always add keyframe at start
            first_key = subject_location_keys[0]
            subject_pos = (first_key["x"], first_key["y"], first_key["z"])
            focal_length = calculate_focal_length(camera_location, subject_pos, coverage=coverage)
            focal_keyframes.append({"frame": first_key["frame"], "value": focal_length})
            last_focal_length = focal_length
            
            # Sample at intervals
            max_time = subject_state["current_time"]
            current_time = sample_interval
            
            while current_time <= max_time:
                frame = int(current_time * fps)
                
                # Find subject position at this time
                subject_pos = None
                for i, key in enumerate(subject_location_keys):
                    if key["frame"] >= frame:
                        subject_pos = (key["x"], key["y"], key["z"])
                        break
                
                if subject_pos:
                    focal_length = calculate_focal_length(camera_location, subject_pos, coverage=coverage)
                    
                    # Only add keyframe if change exceeds threshold
                    if abs(focal_length - last_focal_length) / last_focal_length > change_threshold:
                        focal_keyframes.append({"frame": frame, "value": focal_length})
                        last_focal_length = focal_length
                
                current_time += sample_interval
            
            # Always add keyframe at end
            last_key = subject_location_keys[-1]
            subject_pos = (last_key["x"], last_key["y"], last_key["z"])
            focal_length = calculate_focal_length(camera_location, subject_pos, coverage=coverage)
            if focal_keyframes[-1]["frame"] != last_key["frame"]:
                focal_keyframes.append({"frame": last_key["frame"], "value": focal_length})
            
            # Add to camera keyframes
            camera_state["keyframes"]["current_focal_length"] = focal_keyframes
            log(f"  ✓ Generated {len(focal_keyframes)} focal length keyframes for '{camera_name}'")
    
    # Convert to output format
    result = {}
    for actor_name, state in actor_states.items():
        result[actor_name] = {
            "keyframes": state["keyframes"],
            "waypoints": state["waypoints"]
        }
        log(f"\n✓ {actor_name}: {len(state['keyframes']['location'])} location keys, {len(state['keyframes']['animations'])} anim sections")
    
    # ============================================================
    # PASS 1: Base Command Processing
    # ============================================================
    save_planning_debug("1_base_command_processing", actor_states, camera_cuts, scene_name)
    
    # ============================================================
    # PASS 2: Camera Movement
    # ============================================================
    # Camera movement is already processed in Pass 1
    # This pass just saves the state for debugging
    save_planning_debug("2_camera_movement", actor_states, camera_cuts, scene_name)
    
    # ============================================================
    # PASS 3: Look-At Rotation
    # ============================================================
    generate_look_at_rotation(actors_info, actor_states, fps)
    save_planning_debug("3_look_at_rotation", actor_states, camera_cuts, scene_name)
    
    # ============================================================
    # PASS 4: Focus Distance
    # ============================================================
    generate_focus_distance(actors_info, actor_states, fps)
    save_planning_debug("4_focus_distance", actor_states, camera_cuts, scene_name)
    
    # ============================================================
    # PASS 5: Focal Length
    # ============================================================
    generate_focal_length(actors_info, actor_states, fps)
    save_planning_debug("5_focal_length", actor_states, camera_cuts, scene_name)
    
    # Legacy: Generate Auto-FOV for cameras (single-subject, non-timeline based)
    generate_auto_zoom_keyframes(actors_info, actor_states, fps)

    return result, camera_cuts


def process_camera_cut(cmd, camera_cuts):
    """Process camera_cut command"""
    camera_name = cmd.get("camera") or cmd.get("actor")
    at_time = cmd.get("at_time", 0.0)
    
    if not camera_name:
        log("  ⚠ No camera specified for camera_cut")
        return
        
    camera_cuts.append({
        "camera": camera_name,
        "time": at_time
    })
    log(f"  ✓ Camera cut to '{camera_name}' at {at_time}s")


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


def process_move(cmd, state, fps):
    """
    Consolidated Movement Handler (from Fluent API)
    Supports: Velocity Ramps, Corridors, Radius, Time/Distance termination
    """
    direction = cmd.get("direction", "forward")
    secs = cmd.get("seconds", 0.0)
    dist = cmd.get("meters", 0.0)
    v0 = cmd.get("start_speed", state["current_speed"] if "current_speed" in state else 0.0)
    v1 = cmd.get("target_speed", cmd.get("speed_mtps", v0))
    radius = cmd.get("radius", state.get("radius", 0.35))
    
    # Corridor Constraints
    left = cmd.get("left_boundary")
    right = cmd.get("right_boundary")
    
    # Kinematic Integration
    # We must generate dense keyframes for ramps or lateral shifts
    steps = int(max(1, secs * fps))
    dt = secs / steps if steps > 0 else 0
    
    start_frame = int(state["current_time"] * fps)
    
    pos = state["current_pos"].copy()
    current_v = v0
    accel = (v1 - v0) / secs if secs > 0 else 0
    
    # Determine local forward/right vectors
    yaw_rad = math.radians(state["current_rotation"]["yaw"])
    fwd = {"x": math.cos(yaw_rad), "y": math.sin(yaw_rad)}
    right_vec = {"x": fwd["y"], "y": -fwd["x"]} # 90 deg right
    
    # Starting Lateral Position (Assume X-aligned for now, but we can generalized)
    # y0 = pos["y"] if we are strafing from current
    y0 = pos["y"]
    target_y = (left + right) / 2.0 * 100.0 if (left is not None and right is not None) else None
    
    for i in range(steps + 1):
        step_t = i * dt
        frame = start_frame + i
        
        # Velocity at this step
        v_step = v0 + accel * step_t
        displacement_m = (v0 * step_t + 0.5 * accel * (step_t**2)) if i > 0 else 0
        
        # Calculate Forward Component (relative to START of this command)
        # We integrate from the specific start position of this leg
        move_x = fwd["x"] * displacement_m * 100.0
        move_y = fwd["y"] * displacement_m * 100.0
        
        temp_pos = {
            "x": state["current_pos"]["x"] + move_x,
            "y": state["current_pos"]["y"] + move_y,
            "z": pos["z"]
        }
        
        # Apply Lateral Correction (Strafing)
        if target_y is not None:
            progress = step_t / secs if secs > 0 else 1.0
            temp_pos["y"] = y0 + (target_y - y0) * progress
            
        add_location_keyframe(state, frame, temp_pos)
        add_rotation_keyframe(state, frame, state["current_rotation"])
        
        if i == steps:
            pos = temp_pos
            current_v = v_step

    # Update state
    state["current_pos"] = pos
    state["current_time"] += secs
    state["current_speed"] = v1
    state["radius"] = radius
    
    log(f"  Move fluent: {secs:.2f}s, {dist:.1f}m. Speed {v0:.1f}->{v1:.1f}")
    if left is not None:
        log(f"  Corridor: {left} - {right} (m)")

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
    """Move camera with location, rotation, or focal length change"""
    location = cmd.get("location")
    rotation = cmd.get("rotation")
    focal_length = cmd.get("focal_length")
    duration_sec = cmd.get("duration", 2.0)
    
    start_frame = int(state["current_time"] * fps)
    end_frame = int((state["current_time"] + duration_sec) * fps)
    
    # 1. Location
    if location:
        # Add start/end location keys
        add_location_keyframe(state, start_frame, state["current_pos"])
        
        target_pos = {"x": location[0], "y": location[1], "z": location[2]}
        state["current_pos"] = target_pos
        add_location_keyframe(state, end_frame, state["current_pos"])
    else:
        # Hold current location
        add_location_keyframe(state, start_frame, state["current_pos"])
        add_location_keyframe(state, end_frame, state["current_pos"])

    # 2. Rotation
    if rotation:
        add_rotation_keyframe(state, start_frame, state["current_rotation"])
        
        target_rot = {"pitch": rotation[0], "yaw": rotation[1], "roll": rotation[2]}
        state["current_rotation"] = target_rot
        add_rotation_keyframe(state, end_frame, state["current_rotation"])
    else:
        # Hold current rotation or continue tracking?
        # If we are tracking (LookAt), rotation keyframes might fight it?
        # The writer usually respects lookat override.
        add_rotation_keyframe(state, start_frame, state["current_rotation"])
        add_rotation_keyframe(state, end_frame, state["current_rotation"])
        
    # 3. Focal Length
    if focal_length:
        current_fl = state.get("current_focal_length", 35.0) # Need to track this in state!
        
        if "current_focal_length" not in state["keyframes"]:
             state["keyframes"]["current_focal_length"] = []
             
        # Start key
        state["keyframes"]["current_focal_length"].append({
            "frame": start_frame,
            "value": current_fl
        })
        
        # End key
        state["keyframes"]["current_focal_length"].append({
            "frame": end_frame,
            "value": focal_length
        })
        state["current_focal_length"] = focal_length

    state["current_time"] += duration_sec
    
    log(f"  Camera move/shot in {duration_sec}s (Loc: {bool(location)}, Rot: {bool(rotation)}, Zoom: {bool(focal_length)})")


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
        
    # If height_pct is specified, calculate offset based on actor height
    if "height_pct" in cmd and target_name in actors_info:
        actor_height = actors_info[target_name].get("height", 1.8)  # Default 1.8m
        height_pct = cmd["height_pct"]
        z_offset_cm = actor_height * height_pct * 100.0  # Convert m to cm
        
        # Merge with existing offset if any (preserve X/Y, override Z)
        if offset:
            offset.z = z_offset_cm
        else:
            offset = unreal.Vector(0, 0, z_offset_cm)
            
        log(f"  ℹ LookAt height_pct={height_pct:.2f} -> Z-offset={z_offset_cm:.1f}cm (Actor height: {actor_height}m)")
        
    interp_speed = cmd.get("interp_speed", 0.0)
    
    # Enable Rotation Tracking only
    camera_setup.enable_lookat_tracking(camera_actor, target_actor, offset, interp_speed)


def process_camera_focus(cmd, actors_info):
    """Enable Auto-Focus tracking (Focus only)"""
    camera_name = cmd.get("actor")
    target_name = cmd.get("target") or cmd.get("focus_actor")
    
    if not target_name:
        log("  ⚠ No target specified for camera_focus")
        return
        
    if camera_name not in actors_info or target_name not in actors_info:
        log(f"  ⚠ Camera '{camera_name}' or Target '{target_name}' not found")
        return
        
    camera_actor = actors_info[camera_name]["actor"]
    target_actor = actors_info[target_name]["actor"]
    
    offset = None
    if "offset" in cmd:
        o = cmd["offset"]
        offset = unreal.Vector(o[0], o[1], o[2])

    # If height_pct is specified, calculate offset based on actor height
    if "height_pct" in cmd and target_name in actors_info:
        # Use same height logic as look_at
        actor_height = actors_info[target_name].get("height", 1.8)
        height_pct = cmd["height_pct"]
        z_offset_cm = actor_height * height_pct * 100.0
        
        if offset:
            offset.z = z_offset_cm
        else:
            offset = unreal.Vector(0, 0, z_offset_cm)
            
        log(f"  ℹ Focus height_pct={height_pct:.2f} -> Z-offset={z_offset_cm:.1f}cm")
        
    camera_setup.enable_focus_tracking(camera_actor, target_actor, offset)


def process_camera_wait(cmd, actor_states, fps):
    """Process camera wait command and build timelines for look_at, focus, and frame_subject"""
    camera_name = cmd.get("actor")
    seconds = cmd.get("seconds", 0.0)
    
    if not camera_name or camera_name not in actor_states:
        log(f"  ⚠ Camera '{camera_name}' not found in actor_states")
        return
    
    state = actor_states[camera_name]
    
    # Build look_at timeline if specified
    if "look_at_actor" in cmd:
        if "look_at_timeline" not in state:
            state["look_at_timeline"] = []
        
        state["look_at_timeline"].append({
            "start_time": state["current_time"],
            "end_time": state["current_time"] + seconds,
            "subject": cmd["look_at_actor"],
            "height_pct": cmd.get("height_pct", 0.7),
            "interp_speed": cmd.get("interp_speed", 0.0) 
        })
        log(f"  > Look-at: {cmd['look_at_actor']} from {state['current_time']:.1f}s to {state['current_time'] + seconds:.1f}s")
    
    # Build focus timeline if specified
    if "focus_actor" in cmd:
        if "focus_timeline" not in state:
            state["focus_timeline"] = []
        
        state["focus_timeline"].append({
            "start_time": state["current_time"],
            "end_time": state["current_time"] + seconds,
            "subject": cmd["focus_actor"],
            "height_pct": cmd.get("focus_height_pct", 0.7)
        })
        log(f"  > Focus: {cmd['focus_actor']} from {state['current_time']:.1f}s to {state['current_time'] + seconds:.1f}s")
    
    # Build frame_subject timeline if specified
    if "frame_subject" in cmd:
        if "frame_subject_timeline" not in state:
            state["frame_subject_timeline"] = []
        
        state["frame_subject_timeline"].append({
            "start_time": state["current_time"],
            "end_time": state["current_time"] + seconds,
            "subject": cmd["frame_subject"],
            "coverage": cmd.get("coverage", 0.7)
        })
        log(f"  > Frame subject: {cmd['frame_subject']} from {state['current_time']:.1f}s to {state['current_time'] + seconds:.1f}s")
    
    state["current_time"] += seconds
    log(f"  Camera wait {seconds}s")



def process_camera_settings(cmd, actors_info):
    """Update camera settings (look_at, focus) mid-sequence"""
    # Just dispatch to specific handlers
    # NOTE: In standard Sequencer without keyframing properties, this changes the setting GLOBALLY for the actor instance.
    # To support timeline-based switching, we'd need to Keyframe the properties (ActorToTrack).
    # For now, we assume user is switching OR we accept the limitation.
    
    if "look_at_actor" in cmd:
        process_camera_look_at(cmd, actors_info)
        
    if "focus_actor" in cmd:
        process_camera_focus(cmd, actors_info)
        
    log(f"  > Camera Settings Updated")


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
        "radius": cmd.get("radius", 0.35),
        "height": cmd.get("height", 1.8),  # Store height for later use
        "actor": actor,
        "binding": binding
    }
    
    # Initialize state
    init_actor_state(actor_name, actors_info[actor_name], actor_states)
    log(f"  ✓ Actor '{actor_name}' added successfully")
    log(f"    Initial State -> Pos: {actors_info[actor_name]['location']}, Rot: {actors_info[actor_name]['rotation']}")


def process_add_camera(cmd, actors_info, actor_states, sequence, fps, pending_groups=None):
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
    
    # Extract FOV, tint, and show_marker if specified
    fov = cmd.get("fov", 90.0)
    tint = cmd.get("tint", None)
    show_marker = cmd.get("show_marker", None)
    
    # Extract location for creation (so marker is placed correctly)
    location = None
    if "location" in cmd:
        loc = cmd["location"]
        location = unreal.Vector(loc[0], loc[1], loc[2])

    camera_actor = camera_setup.create_camera("CineCameraActor", location=location, fov=fov, tint=tint, show_marker=show_marker)
    
    # Rename if possible/needed (camera_setup creates it with default name usually, 
    # but we can try to rename or just track it by our internal name)
    if camera_actor:
        camera_actor.set_actor_label(camera_name)
        
    if "location" in cmd:
        loc = cmd["location"]
        log(f"  > Setting {camera_name} location to: {loc}")
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
        "binding": binding,
        "auto_zoom": cmd.get("auto_zoom"),
        "look_at_actor": cmd.get("look_at_actor"),
        "focus_actor": cmd.get("focus_actor")
    }
    
    # Get initial location for state initialization
    initial_loc = camera_actor.get_actor_location()
    
    # Initialize state for this camera
    camera_state = {
        "current_time": 0.0,
        "current_pos": {"x": initial_loc.x, "y": initial_loc.y, "z": initial_loc.z},
        "current_rotation": {"pitch": camera_actor.get_actor_rotation().pitch, 
                           "yaw": camera_actor.get_actor_rotation().yaw, 
                           "roll": camera_actor.get_actor_rotation().roll},
        "yaw_offset": 0.0,
        "current_animation": None,
        "current_speed": 0.0,
        "radius": 0.35,
        "waypoints": {},
        "keyframes": {
            "location": [],
            "rotation": [],
            "animations": []
        }
    }
    actor_states[camera_name] = camera_state
    
    log(f"  DEBUG: Camera state initialized for '{camera_name}'")
    log(f"  DEBUG: actor_states now has keys: {list(actor_states.keys())}")
    
    # OPTION 1: Ensure all cameras have location keyframes
    # For static cameras, add one keyframe at frame 0 with initial position
    camera_state["keyframes"]["location"].append({
        "frame": 0,
        "x": initial_loc.x,
        "y": initial_loc.y,
        "z": initial_loc.z
    })
    log(f"  ✓ Camera '{camera_name}' added successfully (initial location keyframe at frame 0)")
    log(f"  DEBUG: Camera location keyframes: {camera_state['keyframes']['location']}")
    
    
    # Handle look_at_actor if specified in creation
    if "look_at_actor" in cmd:
        target_name = cmd["look_at_actor"]
        
        # Check for implicit group (comma separated)
        if "," in target_name:
            targets = [t.strip() for t in target_name.split(",") if t.strip()]
            if len(targets) > 1:
                # Create a deterministic group name
                targets.sort()
                group_name = "Target_" + "_".join(targets)
                
                # Update the command to look at the group name
                cmd["look_at_actor"] = group_name
                target_name = group_name
                
                # Register for generation
                if pending_groups is not None and group_name not in pending_groups:
                    pending_groups[group_name] = targets
                    log(f"  ℹ Registered implicit group target: {group_name} -> {targets}")

        process_camera_look_at(cmd, actors_info)
        
    # Handle focus_actor if specified (can be used with or without look_at)
    if "focus_actor" in cmd:
        process_camera_focus(cmd, actors_info)
    
    # Handle auto_frame if specified (adaptive focal length calculation)
    if "auto_frame" in cmd:
        subject_name = cmd["auto_frame"]["subject"]
        coverage = cmd["auto_frame"]["coverage"]
        
        if subject_name not in actors_info:
            log(f"  ⚠ Cannot frame '{subject_name}': actor not found")
        else:
            # Store auto_frame info for keyframe generation
            actors_info[camera_name]["auto_frame"] = {
                "subject": subject_name,
                "coverage": coverage
            }
            log(f"  ℹ Auto-framing enabled: {subject_name} at {coverage*100:.0f}% coverage")



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
        "current_speed": info.get("current_speed", 0.0),
        "radius": info.get("radius", 0.35),
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


def process_add_rect_light(cmd, actors_info):
    """Add a rect light to the scene"""
    light_name = cmd.get("actor", "RectLight")
    
    if light_name in actors_info:
        log(f"  ℹ Light '{light_name}' already exists")
        return

    # Extract parameters
    location = unreal.Vector(0,0,0)
    if "location" in cmd:
        loc = cmd["location"]
        location = unreal.Vector(loc[0], loc[1], loc[2])
        
    rotation = unreal.Rotator(0,0,0)
    if "rotation" in cmd:
        rot = cmd["rotation"]
        rotation = unreal.Rotator(rot[0], rot[1], rot[2])
        
    intensity = cmd.get("intensity", "bright")
    color = cmd.get("color", "white")
    width = cmd.get("width", 100)
    height = cmd.get("height", 100)
    cast_shadows = cmd.get("cast_shadows", False)
    
    # Create
    light_actor = light_setup.create_rect_light(
        name=light_name,
        location=location,
        rotation=rotation,
        intensity=intensity,
        color=color,
        width=width,
        height=height,
        cast_shadows=cast_shadows
    )
    
    if light_actor:
        # Attachment support
        if "attach_to" in cmd:
            parent_name = cmd["attach_to"]
            if parent_name in actors_info:
                parent_actor = actors_info[parent_name]["actor"]
                # Attach (KeepRelative)
                light_actor.attach_to_actor(parent_actor, "", unreal.AttachmentRule.KEEP_RELATIVE, unreal.AttachmentRule.KEEP_RELATIVE, unreal.AttachmentRule.KEEP_RELATIVE, False)
                log(f"  > Attached to '{parent_name}'")
            else:
                log(f"  ⚠ Cannot attach to '{parent_name}': Actor not found")

        actors_info[light_name] = {
            "location": location,
            "rotation": rotation,
            "actor": light_actor
        }


def process_add_floor(cmd, actors_info):
    """Add a floor plane to the scene"""
    actor_name = cmd.get("actor", "Floor")
    
    if actor_name in actors_info:
        log(f"  ℹ Actor '{actor_name}' already exists")
        return

    log(f"  Creating floor '{actor_name}'...")
    
    location = unreal.Vector(0,0,0)
    if "location" in cmd:
        loc = cmd["location"]
        location = unreal.Vector(loc[0], loc[1], loc[2])
        
    # Spawn StaticMeshActor
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, location, unreal.Rotator(0,0,0))
    actor.set_actor_label(actor_name)
    
    # Set Mesh to Plane
    # Try multiple standard paths just in case
    mesh_paths = ["/Engine/BasicShapes/Plane", "/Engine/BasicShapes/Plane.Plane"]
    mesh_asset = None
    for path in mesh_paths:
        mesh_asset = unreal.load_asset(path)
        if mesh_asset:
            break
            
    if mesh_asset:
        actor.static_mesh_component.set_static_mesh(mesh_asset)
    else:
        log("  ⚠ Could not load Plane mesh, floor might be invisible")
        
    # Scale it up (Plane is usually 100x100 units (1m), so scale 100 = 100m, scale 1000 = 1km)
    scale = cmd.get("scale", 100.0) 
    actor.set_actor_scale3d(unreal.Vector(scale, scale, 1.0))
    
    # Material? Optional. Default is usually a checkerboard or grey.
    if "material" in cmd:
         mat = unreal.load_asset(cmd["material"])
         if mat:
             actor.static_mesh_component.set_material(0, mat)
             
    actors_info[actor_name] = {
        "location": location,
        "rotation": unreal.Rotator(0,0,0),
        "actor": actor
    }
    log(f"  ✓ Floor created at {location} (Scale: {scale})")


def process_delete_lights(cmd):
    """Delete all lights of specified types"""
    light_types = cmd.get("light_types", [])
    if not light_types:
        log("  ⚠ No light types specified")
        return
    
    # Map string names to Unreal classes
    light_class_map = {
        "DirectionalLight": unreal.DirectionalLight,
        "SkyLight": unreal.SkyLight,
        "PointLight": unreal.PointLight,
        "SpotLight": unreal.SpotLight,
        "RectLight": unreal.RectLight
    }
    
    log(f"  Deleting lights of types: {', '.join(light_types)}")
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    count = 0
    
    for actor in all_actors:
        for light_type_name in light_types:
            light_class = light_class_map.get(light_type_name)
            if light_class and isinstance(actor, light_class):
                log(f"    - Deleting {light_type_name} '{actor.get_actor_label()}'")
                unreal.EditorLevelLibrary.destroy_actor(actor)
                count += 1
                break  # Don't check other types for this actor
    
    if count == 0:
        log(f"    (No lights of specified types found)")

def process_delete_all_skylights(cmd):
    """Delete all SkyLight actors in the level"""
    log("  Deleting all SkyLights...")
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    count = 0
    for actor in all_actors:
        if isinstance(actor, unreal.SkyLight):
            log(f"    - Deleting '{actor.get_actor_label()}'")
            unreal.EditorLevelLibrary.destroy_actor(actor)
            count += 1
    if count == 0:
        log("    (No SkyLights found)")


def process_delete_all_floors(cmd):
    """Delete all actors with 'Floor' in their name"""
    log("  Deleting all Floors...")
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    count = 0
    for actor in all_actors:
        if "floor" in actor.get_actor_label().lower():
            log(f"    - Deleting '{actor.get_actor_label()}'")
            unreal.EditorLevelLibrary.destroy_actor(actor)
            count += 1
    if count == 0:
        log("    (No Floor actors found)")




def generate_look_at_rotation(actors_info, actor_states, fps):
    """
    PASS 3: Generate Look-At Target Keyframes (Constraint-based)
    Populates keyframes["look_at_target"] with {frame, value=actor_name}
    """
    log("\n" + "="*60)
    log("PASS 3: Look-At Targets (Auto-Tracking)")
    log("="*60)
    
    for camera_name, state in actor_states.items():
        if "look_at_timeline" not in state:
            continue
            
        timeline = state["look_at_timeline"]
        if not timeline:
            continue
            
        target_keys = []
        
        for segment in timeline:
            if "subject" not in segment:
                continue
                
            subject = segment["subject"]
            start_time = segment.get("start_time", 0.0)
            start_frame = int(start_time * fps)
            
            # Keyframe the new target at the start of the segment
            # Note: In Unreal Sequencer, Object property keys hold a reference to the actor
            key = {
                "frame": start_frame,
                "value": subject,
                "interp_speed": segment.get("interp_speed", 0.0) 
            }
            target_keys.append(key)
            
            log(f"  Target Switch: Frame {start_frame} ({start_time}s) -> {subject} (Speed: {key['interp_speed']})")
            
        state["keyframes"]["look_at_target"] = target_keys
        log(f"  ✓ Generated {len(target_keys)} Look-At target keys for '{camera_name}'")


def generate_focus_distance(actors_info, actor_states, fps):
    """
    PASS 4: Generate Focus Target Keyframes (Auto-Focus)
    Populates keyframes["focus_target"] with {frame, value=actor_name}
    """
    log("\n" + "="*60)
    log("PASS 4: Focus Targets (Auto-Focus)")
    log("="*60)
    
    for camera_name, state in actor_states.items():
        if "focus_timeline" not in state:
            continue
            
        timeline = state["focus_timeline"]
        if not timeline:
            continue
            
        target_keys = []
        
        for segment in timeline:
            if "subject" not in segment:
                continue
                
            subject = segment["subject"]
            start_time = segment.get("start_time", 0.0)
            start_frame = int(start_time * fps)
            
            target_keys.append({
                "frame": start_frame,
                "value": subject
            })
        
        state["keyframes"]["focus_target"] = target_keys
        log(f"  ✓ Generated {len(target_keys)} Focus target keys for '{camera_name}'")



def generate_focal_length(actors_info, actor_states, fps):
    """PASS 5: Generate focal length keyframes based on frame_subject timeline (supports dynamic subject switching)"""
    import math
    
    log("\n" + "-"*40)
    log("PASS 5: FOCAL LENGTH GENERATION")
    
    for camera_name, camera_state in actor_states.items():
        # Check if this camera has a frame_subject timeline
        if "frame_subject_timeline" not in camera_state:
            continue
            
        timeline = camera_state["frame_subject_timeline"]
        if not timeline:
            continue
            
        log(f"  Processing {camera_name} with {len(timeline)} subject segment(s)...")
        
        # Get camera location
        camera_info = actors_info.get(camera_name)
        if not camera_info:
            continue
        camera_loc = camera_info["location"]
        
        focal_keyframes = []
        last_focal_length = None
        
        # Process each timeline segment
        for segment in timeline:
            subject_name = segment["subject"]
            coverage = segment["coverage"]
            start_time = segment["start_time"]
            end_time = segment["end_time"]
            start_frame = int(start_time * fps)
            end_frame = int(end_time * fps)
            
            if subject_name not in actor_states:
                log(f"    ⚠ Subject '{subject_name}' not found, skipping segment")
                continue
                
            subject_state = actor_states[subject_name]
            subject_height = actors_info.get(subject_name, {}).get("height", 1.8)
            
            log(f"    {start_time:.1f}s-{end_time:.1f}s: Tracking {subject_name} (coverage={coverage})")
            
            # Always keyframe at segment start (subject switch point)
            camera_pos = get_actor_location_at_frame(camera_state, start_frame)
            subject_pos = get_actor_location_at_frame(subject_state, start_frame)
            focal_length = calculate_focal_length(
                (camera_pos["x"], camera_pos["y"], camera_pos["z"]),
                (subject_pos["x"], subject_pos["y"], subject_pos["z"]),
                subject_height=subject_height,
                coverage=coverage
            )
            focal_keyframes.append({"frame": start_frame, "value": focal_length})
            last_focal_length = focal_length
            
            # Sample within segment (every 2 seconds, adaptive)
            sample_interval_frames = int(2.0 * fps)
            change_threshold = 0.10
            
            for frame in range(start_frame + sample_interval_frames, end_frame, sample_interval_frames):
                camera_pos = get_actor_location_at_frame(camera_state, frame)
                subject_pos = get_actor_location_at_frame(subject_state, frame)
                
                focal_length = calculate_focal_length(
                    (camera_pos["x"], camera_pos["y"], camera_pos["z"]),
                    (subject_pos["x"], subject_pos["y"], subject_pos["z"]),
                    subject_height=subject_height,
                    coverage=coverage
                )
                
                # Only add if changed significantly
                if last_focal_length and abs(focal_length - last_focal_length) / last_focal_length > change_threshold:
                    focal_keyframes.append({"frame": frame, "value": focal_length})
                    last_focal_length = focal_length
            
            # Always keyframe at segment end
            camera_pos = get_actor_location_at_frame(camera_state, end_frame)
            subject_pos = get_actor_location_at_frame(subject_state, end_frame)
            focal_length = calculate_focal_length(
                (camera_pos["x"], camera_pos["y"], camera_pos["z"]),
                (subject_pos["x"], subject_pos["y"], subject_pos["z"]),
                subject_height=subject_height,
                coverage=coverage
            )
            focal_keyframes.append({"frame": end_frame, "value": focal_length})
            last_focal_length = focal_length
        
        # Store keyframes
        camera_state["keyframes"]["current_focal_length"] = focal_keyframes
        log(f"  ✓ Generated {len(focal_keyframes)} focal length keyframes for '{camera_name}'")
    
    log("-"*40)


def generate_auto_zoom_keyframes(actors_info, actor_states, fps):
    """Post-processor to calculate frame-by-frame FOV to maintain target occupancy"""
    import math
    
    log("\n" + "-"*40)
    log("GENERATING AUTO-ZOOM (SMART ZOOM)")
    
    for cam_name, info in actors_info.items():
        config = info.get("auto_zoom")
        if not config:
            continue
            
        target_name = info.get("look_at_actor")
        if not target_name:
            log(f"  ⚠ {cam_name} has auto_zoom but no look_at_actor. Skipping.")
            continue
            
        if target_name not in actor_states:
            log(f"  ⚠ {cam_name} target '{target_name}' state not found. Skipping.")
            continue
            
        log(f"  Calculating Smart Zoom for {cam_name} targeting {target_name}...")
        
        state = actor_states[cam_name]
        target_state = actor_states[target_name]
        
        occupancy = config.get("target_occupancy", 0.3)
        target_height = config.get("target_height_cm", 182.0) # Approx 6ft
        sensor_height = config.get("sensor_height_mm", 24.2) # Default Full Frame height
        
        min_fl = config.get("min_focal_length", 18.0)
        max_fl = config.get("max_focal_length", 300.0)
        
        # We need to know the duration
        max_frame = 0
        if target_state["keyframes"]["location"]:
             max_frame = target_state["keyframes"]["location"][-1]["frame"]
             
        cam_loc = info["location"]
        
        # Performance: Sample every N frames to reduce track density (helps performance/stability)
        step = 10 
        start_frame = 0
        end_frame = max_frame + 1
        for frame in range(start_frame, end_frame, step):
             target_pos = get_actor_location_at_frame(target_state, frame)
             
             # Calculate distance (3D)
             dx = target_pos["x"] - cam_loc.x
             dy = target_pos["y"] - cam_loc.y
             dz = target_pos["z"] - cam_loc.z
             dist = math.sqrt(dx*dx + dy*dy + dz*dz)
             
             if dist < 1.0: dist = 1.0
             
             # Native Formula: FocalLength = (SensorHeight * Distance * Occupancy) / SubjectHeight
             fl = (sensor_height * dist * occupancy) / target_height
             
             # Clamp
             fl = max(min_fl, min(max_fl, fl))
             
             # Add keyframe
             if "current_focal_length" not in state["keyframes"]:
                 state["keyframes"]["current_focal_length"] = []
                 
             state["keyframes"]["current_focal_length"].append({
                 "frame": frame,
                 "value": fl
             })
             
    log("-" * 40)


def generate_group_targets(pending_groups, actor_states, actors_info, sequence, fps):
    """Calculate centroid paths for group targets"""
    log("\n" + "-"*40)
    log("GENERATING GROUP TARGETS")
    
    for group_name, target_names in pending_groups.items():
        if group_name not in actor_states:
            init_actor_state(group_name, {}, actor_states)
            
        group_state = actor_states[group_name]
        source_states = [actor_states[t] for t in target_names if t in actor_states]
        
        if not source_states:
             continue
             
        # Determine max frame duration across all source actors
        max_frame = 0
        for s in source_states:
            if s["keyframes"]["location"]:
                max_frame = max(max_frame, s["keyframes"]["location"][-1]["frame"])
                
        log(f"  Calcuating path for {group_name} (Frames 0-{max_frame})...")
        
        # Frame-by-frame centroid calculation
        # We assume standard 30/60 fps keyframe density. detailed sampling.
        # Ideally we sample every frame.
        
        for frame in range(max_frame + 1):
             # Get position of each actor at this frame
             x_sum, y_sum, z_sum = 0, 0, 0
             count = 0
             
             for s in source_states:
                 pos = get_actor_location_at_frame(s, frame)
                 x_sum += pos["x"]
                 y_sum += pos["y"]
                 z_sum += pos["z"]
                 count += 1
                 
             if count > 0:
                 centroid = {"x": x_sum/count, "y": y_sum/count, "z": z_sum/count}
                 add_location_keyframe(group_state, frame, centroid)
                 
    log("-" * 40)

def get_actor_location_at_frame(state, frame):
    """Simple linear interpolation for actor location at frame"""
    # Optimized: Assume keyframes are sorted. 
    # For now, just find the last key before or at frame.
    # In a real heavy system this would be optimized.
    
    keys = state["keyframes"]["location"]
    if not keys:
        return state["current_pos"] # Default/Start
        
    # Boundary check
    if frame <= keys[0]["frame"]:
        return keys[0]
    if frame >= keys[-1]["frame"]:
        return keys[-1]
        
    # Linear Search (keys are usually sparse-ish? No, they are generated densely for moves)
    # Actually our generator generates keys at Start and End of moves. 
    # So we MUST interpolate.
    
    for i in range(len(keys) - 1):
        k1 = keys[i]
        k2 = keys[i+1]
        
        if k1["frame"] <= frame <= k2["frame"]:
             # Interpolate
             t = (frame - k1["frame"]) / (k2["frame"] - k1["frame"])
             return {
                 "x": k1["x"] + (k2["x"] - k1["x"]) * t,
                 "y": k1["y"] + (k2["y"] - k1["y"]) * t,
                 "z": k1["z"] + (k2["z"] - k1["z"]) * t
             }
             
    return keys[-1]

def create_dummy_actor(name, actors_info, actor_states, sequence):
    """Create a hidden dummy actor for tracking"""
    log(f"  Creating dummy target actor '{name}'...")
    
    # We can perform a trick: Create a CineCameraActor? No, StaticMeshActor? 
    # Or just an Empty Actor. VisualLogger is nice for debug. 
    # Let's use a standard Empty Actor (Note: In Python API, we might default to StaticMesh or similar).
    # simplest is camera_setup.create_camera_marker style? 
    # Or just create a basic actor.
    
    # Using EditorLevelLibrary to spawn an Empty Actor
    location = unreal.Vector(0,0,0)
    rotation = unreal.Rotator(0,0,0)
    
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, location, rotation)
    actor.set_actor_label(name)
    
    # Make it hidden/game hidden?
    # actor.set_actor_hidden_in_game(True) 
    # Actually keeping it visible (default mesh is none for StaticMeshActor usually, or has 'StaticMeshComponent')
    # A StaticMeshActor defaults to None mesh. perfect.
    
    # Bind to sequence
    binding = sequence_setup.add_actor_to_sequence(sequence, actor, name)
    
    actors_info[name] = {
        "location": location,
        "rotation": rotation,
        "actor": actor,
        "binding": binding
    }
    
    init_actor_state(name, actors_info[name], actor_states)

