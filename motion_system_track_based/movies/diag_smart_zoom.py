# Diagnostic Movie: Long-Range Smart Zoom Test
# Runner starts at [0,0,0] and runs towards camera at [5000, 0, 150].
# This is a 50 meter distance to clearly see the zoom in action.

MOVIE = {
    "name": "Diag_LongRangeZoom",
    "create_new_level": True,
    "fps": 30,
    "plan": [
        # 1. Actors
        {"command": "add_actor", "actor": "Runner", "location": [0, 0, 0], "yaw_offset": -90},
        
        # 2. Camera looking at the runner 
        # Cam is at X=5000 (50m away), looking back towards origin (-X direction)
        {"command": "add_camera", "actor": "DiagCam", "location": [5000, 0, 150], "look_at_actor": "Runner", 
         "auto_zoom": {
             "target_occupancy": 0.35, # 35% height
             "min_focal_length": 18.0, 
             "max_focal_length": 300.0
         }},
        
        {"command": "camera_cut", "camera": "DiagCam", "at_time": 0.0},
        
        # 3. Movement: Runner runs from 0,0 to 4500,0 (Directly at camera)
        {"actor": "Runner", "command": "animation", "name": "Jog_Fwd"},
        {"actor": "Runner", "command": "face", "direction": "north", "duration": 0.1},
        {"actor": "Runner", "command": "move_for_seconds", "direction": "north", "seconds": 15.0, "speed_mps": 3.0},
        
        {"actor": "Runner", "command": "wait", "seconds": 2.0}
    ]
}
