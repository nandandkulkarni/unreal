"""
Motion Planner - Pass 1: Convert motion commands to keyframe data

Takes high-level motion commands and calculates exact positions, times, and keyframes.
Outputs structured keyframe data ready for Unreal application.
"""
import math
from logger import log


def plan_motion(motion_plan, actors_info, fps):
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
            "current_animation": None,
            "waypoints": {},
            "keyframes": {
                "location": [],
                "rotation": [],
                "animations": []
            }
        }
    
    # Process each command sequentially
    for i, cmd in enumerate(motion_plan):
        actor_name = cmd.get("actor")
        if not actor_name or actor_name not in actor_states:
            log(f"⚠ Command {i}: Unknown actor '{actor_name}', skipping")
            continue
        
        state = actor_states[actor_name]
        command_type = cmd["command"]
        
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
        elif command_type == "animation":
            process_animation(cmd, state, fps)
        elif command_type == "wait":
            process_wait(cmd, state, fps)
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
    
    return result


def get_speed_cm_per_sec(cmd):
    """Convert speed to cm/s"""
    if "speed_mph" in cmd:
        return cmd["speed_mph"] * 44.704  # mph to cm/s
    elif "speed_mps" in cmd:
        return cmd["speed_mps"] * 100  # m/s to cm/s
    else:
        log("  ⚠ No speed specified, using default 100 cm/s")
        return 100.0


def calculate_direction_vector(direction, yaw_degrees):
    """Calculate movement vector from direction and current yaw"""
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
    """Add rotation keyframe"""
    state["keyframes"]["rotation"].append({
        "frame": frame,
        "pitch": rot["pitch"],
        "yaw": rot["yaw"],
        "roll": rot["roll"]
    })


def process_move_by_distance(cmd, state, fps):
    """Move by distance over calculated time"""
    direction = cmd.get("direction", "forward")
    distance_m = cmd.get("meters", 0)
    distance_cm = distance_m * 100
    speed_cm_s = get_speed_cm_per_sec(cmd)
    
    duration_sec = distance_cm / speed_cm_s
    
    # Calculate new position
    dir_vec = calculate_direction_vector(direction, state["current_rotation"]["yaw"])
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
    
    distance_cm = speed_cm_s * duration_sec
    
    # Calculate new position
    dir_vec = calculate_direction_vector(direction, state["current_rotation"]["yaw"])
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


def process_turn_by_direction(cmd, state, fps):
    """Turn left or right by degrees"""
    direction = cmd.get("direction", "left")
    degrees = cmd.get("degrees", 90)
    
    if direction == "right":
        degrees = -degrees
    
    turn_speed = cmd.get("turn_speed_deg_per_sec", 45)
    duration_sec = abs(degrees) / turn_speed
    
    start_frame = int(state["current_time"] * fps)
    end_frame = int((state["current_time"] + duration_sec) * fps)
    
    add_rotation_keyframe(state, start_frame, state["current_rotation"])
    
    state["current_rotation"]["yaw"] += degrees
    add_rotation_keyframe(state, end_frame, state["current_rotation"])
    add_location_keyframe(state, start_frame, state["current_pos"])
    
    log(f"  Turn {direction} {abs(degrees)}° in {duration_sec:.2f}s → yaw={state['current_rotation']['yaw']:.1f}°")
    
    state["current_time"] += duration_sec


def process_turn_by_degree(cmd, state, fps):
    """Turn by exact degrees (positive=left/CCW, negative=right/CW)"""
    degrees = cmd.get("degrees", 0)
    cmd_modified = {"direction": "left" if degrees >= 0 else "right", "degrees": abs(degrees)}
    cmd_modified.update({k: v for k, v in cmd.items() if k not in ["command", "degrees"]})
    process_turn_by_direction(cmd_modified, state, fps)


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
