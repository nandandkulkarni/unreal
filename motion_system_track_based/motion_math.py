import math
from typing import List, Tuple, Dict

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

# =============================================================================
# SPLINE MATH (Catmull-Rom)
# =============================================================================

def catmull_rom_spline(p0: Tuple[float, float, float], 
                      p1: Tuple[float, float, float], 
                      p2: Tuple[float, float, float], 
                      p3: Tuple[float, float, float], 
                      t: float, 
                      tension: float = 0.5) -> Tuple[float, float, float]:
    """
    Evaluate a 3D Catmull-Rom spline segment.
    
    Args:
        p0: Control point i-1
        p1: Control point i (Start of segment)
        p2: Control point i+1 (End of segment)
        p3: Control point i+2
        t: Interpolation factor (0.0 to 1.0)
        tension: Tension factor (default 0.5)
        
    Returns:
        Interploated (x, y, z) at t
    """
    # Unpack for clarity
    t2 = t * t
    t3 = t2 * t
    
    # Calculate coefficients
    # Formula: 0.5 * ( (2*P1) + (-P0 + P2)*t + (2*P0 - 5*P1 + 4*P2 - P3)*t^2 + (-P0 + 3*P1 - 3*P2 + P3)*t^3 )
    
    # Pre-calculate basis functions (Standard Catmull-Rom)
    # Using the matrix form:
    # [ 1  t t^2 t^3 ] * 0.5 * [  0  2  0  0 ]
    #                          [ -1  0  1  0 ]
    #                          [  2 -5  4 -1 ]
    #                          [ -1  3 -3  1 ]
    
    # Component-wise calculation for efficiency
    res = []
    for i in range(3): # x, y, z
        v0 = p0[i]
        v1 = p1[i]
        v2 = p2[i]
        v3 = p3[i]
        
        c0 = 2 * v1
        c1 = v2 - v0
        c2 = 2 * v0 - 5 * v1 + 4 * v2 - v3
        c3 = -v0 + 3 * v1 - 3 * v2 + v3
        
        val = 0.5 * (c0 + c1 * t + c2 * t2 + c3 * t3)
        res.append(val)
        
    return tuple(res)

def sample_spline_path(points: List[Tuple[float, float, float]], 
                      distance_total: float,
                      sample_interval: float = 10.0,
                      closed: bool = False,
                      tension: float = 0.5) -> List[Dict]:
    """
    Sample a full spline path at regular distance intervals.
    
    Args:
        points: List of (x, y, z) tuples
        distance_total: Total length of path (approximate or precise)
        sample_interval: Distance between samples in cm
        closed: Loop the path
        tension: Spline tension
        
    Returns:
        List of dicts: {"pos": (x,y,z), "tangent": (tx,ty,tz), "distance": d}
    """
    if len(points) < 2:
        return [{"pos": points[0], "tangent": (1,0,0), "distance": 0}] if points else []

    # 1. Augment points for Catmull-Rom (needs p-1 and p+2)
    # We create a padded list: P_start, P0, P1, ..., Pn, P_end
    padded_points = []
    if closed:
        padded_points = [points[-1]] + points + [points[0], points[1]]
    else:
        # Duplicate start/end points to clamp curvature
        padded_points = [points[0]] + points + [points[-1]]
        
    # 2. Approximate segment lengths to parameterize t by distance
    # This is a bit expensive, so we do a simple chord-length approximation first
    # then iterate through segments.
    
    # We will walk the spline by segments
    samples = []
    num_segments = len(points) if closed else len(points) - 1
    
    current_dist = 0.0
    
    # Logic:
    # Iterate through segments. For each segment, calculate length.
    # While current_sample_dist < current_segment_end_dist:
    #   Calc t within segment
    #   Sample
    #   Increment current_sample_dist
    
    target_dist = 0.0
    
    # Function to get 4 points for segment i
    def get_points(i):
        # i is index in ORIGINAL points list (0 to n-1)
        # mapped to padded list: padded[i+1] is start of segment i
        # p0 = padded[i], p1 = padded[i+1], p2 = padded[i+2], p3 = padded[i+3]
        return padded_points[i], padded_points[i+1], padded_points[i+2], padded_points[i+3]

    for i in range(num_segments):
        p0, p1, p2, p3 = get_points(i)
        
        # Estimate segment length (chord)
        chord_len = math.sqrt(sum((p2[k]-p1[k])**2 for k in range(3)))
        
        # Just use chord length for parameterization (simplification but usually sufficient for visualization)
        # For precision, we'd integrate, but let's assume Uniform
        # Actually, for constant speed motion, we need Arc-Length Parameterization.
        # Minimal approach: Step 't' finely, accumulate distance, emit sample when interval crossed.
        
        substeps = max(10, int(chord_len / 5.0)) # 5cm substeps
        
        prev_pos = p1
        for s in range(1, substeps + 1):
            t = s / substeps
            curr_pos = catmull_rom_spline(p0, p1, p2, p3, t, tension)
            
            # Distance from prev substep
            step_d = math.sqrt(sum((curr_pos[k]-prev_pos[k])**2 for k in range(3)))
            current_dist += step_d
            
            # Emit samples
            while current_dist >= target_dist:
                # Calculate tangent at this point (derivative)
                # Derivative of Catmull: 0.5 * ( c1 + 2*c2*t + 3*c3*t^2 )
                # Re-calc coeffs
                tangent = []
                for k in range(3):
                    v0, v1, v2, v3 = p0[k], p1[k], p2[k], p3[k]
                    c1 = v2 - v0
                    c2 = 2 * v0 - 5 * v1 + 4 * v2 - v3
                    c3 = -v0 + 3 * v1 - 3 * v2 + v3
                    # Deriv at t
                    d = 0.5 * (c1 + 2*c2*t + 3*c3*t*t)
                    tangent.append(d)
                
                # Normalize tangent
                mag = math.sqrt(sum(x*x for x in tangent))
                if mag > 0:
                    tangent = tuple(x/mag for x in tangent)
                else:
                    tangent = (1, 0, 0) # Fallback
                
                samples.append({
                    "pos": curr_pos,
                    "tangent": tangent,
                    "distance": target_dist,
                    "slope": math.degrees(math.atan2(tangent[2], math.sqrt(tangent[0]**2 + tangent[1]**2))) # Pitch
                })
                
                target_dist += sample_interval
                
            prev_pos = curr_pos
            
    return samples
