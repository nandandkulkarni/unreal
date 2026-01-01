"""
Motion Plan Validator - Schema-based validation for motion commands

Validates motion plan JSON against a comprehensive schema to catch errors early.
"""

# Command Schema: Define all supported commands and their required/optional fields
COMMAND_SCHEMA = {
    # Actor Management
    "add_actor": {
        "required": ["actor", "location"],
        "optional": ["yaw_offset", "radius", "height", "mesh_path"]
    },
    
    # Movement Commands
    "move": {
        "required": ["actor"],
        "optional": ["direction", "meters", "seconds", "speed_mtps", "target_speed", 
                    "start_speed", "radius", "left_boundary", "right_boundary", "velocity_ramp"]
    },
    "move_by_distance": {
        "required": ["actor", "direction", "meters"],
        "optional": ["speed", "duration"]
    },
    "move_for_seconds": {
        "required": ["actor", "direction", "seconds"],
        "optional": ["speed"]
    },
    "move_to_location": {
        "required": ["actor", "location"],
        "optional": ["speed", "duration"]
    },
    "move_to_waypoint": {
        "required": ["actor", "waypoint"],
        "optional": ["speed", "duration"]
    },
    "move_and_turn": {
        "required": ["actor", "direction", "meters"],
        "optional": ["speed", "duration", "target_yaw"]
    },
    
    # Rotation Commands
    "face": {
        "required": ["actor", "direction"],
        "optional": ["duration"]
    },
    "turn_by_degree": {
        "required": ["actor", "degrees"],
        "optional": ["duration"]
    },
    "turn_by_direction": {
        "required": ["actor", "direction"],
        "optional": ["duration"]
    },
    "turn_left": {
        "required": ["actor"],
        "optional": ["duration"]
    },
    "turn_right": {
        "required": ["actor"],
        "optional": ["duration"]
    },
    
    # Animation Commands
    "animation": {
        "required": ["actor", "name"],
        "optional": ["speed_multiplier"]
    },
    
    # Wait Commands
    "wait": {
        "required": ["actor", "seconds"],
        "optional": []
    },
    
    # Camera Commands
    "add_camera": {
        "required": ["actor", "location"],
        "optional": ["fov", "rotation"]
    },
    "camera_move": {
        "required": ["actor"],
        "optional": ["location", "rotation", "focal_length", "duration"]
    },
    "camera_look_at": {
        "required": ["actor", "target"],
        "optional": ["height_pct", "interp_speed"]
    },
    "camera_focus": {
        "required": ["actor", "target"],
        "optional": ["height_pct"]
    },
    "camera_wait": {
        "required": ["actor", "seconds"],
        "optional": ["look_at_actor", "look_at_height_pct", "interp_speed", 
                    "focus_actor", "focus_height_pct", "frame_subject", "coverage"]
    },
    "camera_settings": {
        "required": ["actor"],
        "optional": ["look_at", "look_at_actor", "focus", "focus_actor", 
                    "height_pct", "interp_speed"]
    },
    "camera_cut": {
        "required": ["camera", "at_time"],
        "optional": []
    },
    
    # Audio Commands
    "add_audio": {
        "required": ["asset_path"],
        "optional": ["start_time", "duration", "volume"]
    },
    
    # Lighting Commands
    "add_directional_light": {
        "required": ["name"],
        "optional": ["intensity", "color", "rotation"]
    },
    "add_skylight": {
        "required": [],
        "optional": ["intensity", "color"]
    },
    "delete_lights": {
        "required": [],
        "optional": []
    },
    "delete_all_skylights": {
        "required": [],
        "optional": []
    },
    
    # Environment Commands
    "add_floor": {
        "required": [],
        "optional": ["size", "location"]
    },
    "delete_all_floors": {
        "required": [],
        "optional": []
    },
}


def validate_motion_plan(plan, strict=True):
    """
    Validate a motion plan against the command schema
    
    Args:
        plan: List of command dictionaries
        strict: If True, treat warnings as errors
        
    Returns:
        tuple: (is_valid, errors, warnings)
    """
    errors = []
    warnings = []
    
    if not isinstance(plan, list):
        errors.append("Motion plan must be a list of commands")
        return False, errors, warnings
    
    for i, cmd in enumerate(plan):
        if not isinstance(cmd, dict):
            errors.append(f"Command {i}: Must be a dictionary, got {type(cmd).__name__}")
            continue
        
        # Check for 'command' field
        if "command" not in cmd:
            errors.append(f"Command {i}: Missing 'command' field")
            continue
        
        cmd_type = cmd["command"]
        
        # Check if command is supported
        if cmd_type not in COMMAND_SCHEMA:
            errors.append(f"Command {i}: Unknown command type '{cmd_type}'")
            continue
        
        schema = COMMAND_SCHEMA[cmd_type]
        
        # Check required fields
        for field in schema["required"]:
            if field not in cmd:
                errors.append(f"Command {i} ({cmd_type}): Missing required field '{field}'")
        
        # Check for unexpected fields (warnings only)
        allowed_fields = set(schema["required"] + schema["optional"] + ["command"])
        for field in cmd.keys():
            if field not in allowed_fields:
                warnings.append(f"Command {i} ({cmd_type}): Unexpected field '{field}' (might be ignored)")
    
    is_valid = len(errors) == 0 and (not strict or len(warnings) == 0)
    return is_valid, errors, warnings


def validate_json_file(json_path, strict=True):
    """
    Validate a motion plan JSON file
    
    Args:
        json_path: Path to the JSON file
        strict: If True, treat warnings as errors
        
    Returns:
        tuple: (is_valid, errors, warnings)
    """
    import json
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        return False, [f"File not found: {json_path}"], []
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"], []
    
    # Extract the plan array
    if "plan" not in data:
        return False, ["JSON must contain a 'plan' array"], []
    
    return validate_motion_plan(data["plan"], strict=strict)


def print_validation_results(is_valid, errors, warnings):
    """Pretty print validation results"""
    if is_valid:
        print("✓ Validation passed!")
        if warnings:
            print(f"\n⚠ {len(warnings)} warning(s):")
            for warning in warnings:
                print(f"  - {warning}")
    else:
        print("❌ Validation failed!")
        if errors:
            print(f"\n{len(errors)} error(s):")
            for error in errors:
                print(f"  - {error}")
        if warnings:
            print(f"\n{len(warnings)} warning(s):")
            for warning in warnings:
                print(f"  - {warning}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python motion_validator.py <json_file> [--strict]")
        sys.exit(1)
    
    json_path = sys.argv[1]
    strict = "--strict" in sys.argv
    
    is_valid, errors, warnings = validate_json_file(json_path, strict=strict)
    print_validation_results(is_valid, errors, warnings)
    
    sys.exit(0 if is_valid else 1)
