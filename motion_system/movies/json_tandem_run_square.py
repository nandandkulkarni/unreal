# Movie Definition: Tandem Square Run with Camera Cuts
# This is a Python file to prevent VSCode from auto-formatting the JSON

MOVIE = {
    "name": "Tandem Square Run with Camera Cuts",
    "create_new_level": True,
    "fps": 30,
    "plan": [
        # Actors
        {"command":"add_actor","actor":"Jessica","location":[0,0,0],"yaw_offset":-90,"mesh_path":"/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica"},
        {"command":"add_actor","actor":"Sarah","location":[0,-300,0],"yaw_offset":-90,"mesh_path":"/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica"},
        
        # Cameras
        # 1. Corner1Cam (High angle wide) - Tracks Jessica
        {"command":"add_camera","actor":"Corner1Cam","location":[-100,-150,100],"rotation":[0,0,0],"fov":55,"tint":[0.5,0.5,1.0],"show_marker":"blue","look_at_actor":"Jessica","offset":[0,0,150],"interp_speed":5.0},
        
        # 2. Corner3Cam (Green) - Tracks Jessica
        # Runners moving +Y towards Y=2500. Cam at Y=3000 looking back (-Y).
        {"command": "add_camera", "actor": "Corner3Cam", "location": [2200,3000,100], "fov": 30, "look_at_actor": "Jessica, Sarah"},
        
        # 3. Side3Cam (Red) - Tracks Jessica
        # Runners moving -X along Y=2500 line. Cam at side (Y=1800) looking at path (Y=2500).
        {"command":"add_camera","actor":"Side3Cam","location":[1250,2500,50],"rotation":[0,0,0],"fov":40,"tint":[1.0,0.5,0.5],"show_marker":"red","look_at_actor":"Jessica","offset":[0,0,100]},
        
        # Lighting
        {"command":"add_directional_light","actor":"SunLight","from":"west","angle":"low","intensity":"bright","color":"golden","atmosphere_sun":True},
        
        # Camera Cuts (Timeline)
        {"command":"camera_cut","camera":"Corner1Cam","at_time":0.0},      # 0-5s: Wide shot start
        {"command":"camera_cut","camera":"Corner3Cam","at_time":5.0},   # 5-10s: Corner3 action
        {"command":"camera_cut","camera":"Side3Cam","at_time":10.0},     # 10-15s: Side3 profile
        {"command":"camera_cut","camera":"Corner1Cam","at_time":15.0},     # 15-20s: Wide shot finish
        
        # Animation & Action
        {"actor":"Jessica","command":"animation","name":"Jog_Fwd"},
        {"actor":"Sarah","command":"animation","name":"Jog_Fwd"},
        {"actor":"Jessica","command":"face","direction":"north","duration":0.5},
        {"actor":"Sarah","command":"face","direction":"north","duration":0.5},
        {"actor":"Jessica","command":"move_for_seconds","direction":"north","seconds":5,"speed_mtps":5},
        {"actor":"Sarah","command":"move_for_seconds","direction":"north","seconds":5,"speed_mtps":5},
        {"actor":"Jessica","command":"face","direction":"east"},
        {"actor":"Sarah","command":"face","direction":"east"},
        {"actor":"Jessica","command":"move_for_seconds","direction":"east","seconds":5,"speed_mtps":5},
        {"actor":"Sarah","command":"move_for_seconds","direction":"east","seconds":5,"speed_mtps":5},
        {"actor":"Jessica","command":"face","direction":"south"},
        {"actor":"Sarah","command":"face","direction":"south"},
        {"actor":"Jessica","command":"move_for_seconds","direction":"south","seconds":5,"speed_mtps":5},
        {"actor":"Sarah","command":"move_for_seconds","direction":"south","seconds":5,"speed_mtps":5},
        {"actor":"Jessica","command":"face","direction":"west"},
        {"actor":"Sarah","command":"face","direction":"west"},
        {"actor":"Jessica","command":"move_for_seconds","direction":"west","seconds":5,"speed_mtps":5},
        {"actor":"Sarah","command":"move_for_seconds","direction":"west","seconds":5,"speed_mtps":5}
    ]
}
