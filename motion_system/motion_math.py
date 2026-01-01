import math

def get_cardinal_angle(direction: str, offset: float = None) -> float:
    """Get absolute world angle for a cardinal direction string"""
    if not direction:
        return None
        
    direction = direction.lower()
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

def get_shortest_path_yaw(current_yaw: float, target_yaw: float) -> float:
    """Calculate target yaw that minimizes rotation distance from current_yaw"""
    delta = (target_yaw - current_yaw) % 360
    if delta > 180:
        delta -= 360
    return current_yaw + delta

def calculate_direction_vector(direction: str, yaw_degrees: float, offset: float = None) -> dict:
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
        # Default to forward if unknown
        return {"x": forward_x, "y": forward_y}

def calculate_new_position(start_pos: dict, start_yaw: float, direction: str, distance_cm: float, offset: float = None) -> dict:
    """Calculate new position based on motion parameters"""
    vec = calculate_direction_vector(direction, start_yaw, offset)
    return {
        "x": start_pos["x"] + vec["x"] * distance_cm,
        "y": start_pos["y"] + vec["y"] * distance_cm,
        "z": start_pos["z"] # Z typically constant
    }
