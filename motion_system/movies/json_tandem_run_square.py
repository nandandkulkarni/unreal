from ..motion_builder import MovieBuilder

# Movie Definition: Tandem Square Run with Camera Cuts
# Updated to use Context Manager Syntax (v2)

def define_movie():
    with MovieBuilder("Tandem Square Run with Camera Cuts", create_new_level=True, fps=30) as movie:
        
        # Setup Environment
        movie.delete_all_skylights()
        movie.delete_all_floors()
        movie.add_floor("MainFloor", location=(0,0,-0.5), scale=1000)
        movie.add_directional_light("SunLight", direction_from="west", angle="low", intensity="bright", color="golden", atmosphere_sun=True)
        movie.add_rect_light("FaceFill", location=(0,0,0), rotation=(0,-90,0), width=30, height=100, intensity="bright", cast_shadows=False)

        # Create Actors (Initial State)
        movie.add_actor("Jessica", location=(0,0,0), yaw_offset=-90, mesh_path="/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica")
        movie.add_actor("Sarah", location=(0,-300,0), yaw_offset=-90, mesh_path="/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica")
        
        # Create Cameras
        movie.add_camera("Corner1Cam", location=(-100,-150,100), rotation=(0,0,0), fov=55, tint=(0.5,0.5,1.0), show_marker="blue", look_at_actor="Jessica, Sarah", offset=(0,0,150), interp_speed=5.0)
        movie.add_camera("Corner3Cam", location=(4700,5500,100), look_at_actor="Jessica, Sarah", auto_zoom={"target_occupancy":0.35,"min_focal_length":18.0,"max_focal_length":200.0})
        movie.add_camera("Side3Cam", location=(2500,4000,100), rotation=(0,0,0), fov=40, tint=(1.0,0.5,0.5), show_marker="red", look_at_actor="Jessica, Sarah", offset=(0,0,100))

        # --- Timeline ---
        
        # Initial Camera
        movie.at_time(0.0).camera_cut("Corner1Cam")

        # Simultaneous Movement Pattern
        # Using Sim-Context to coordinate Jessica and Sarah
        with movie.simultaneous() as group:
            
            with group.for_actor("Jessica") as jessica:
                jessica.animation("Jog_Fwd")
                jessica.face("north", duration=0.5)
                # North Leg (5s)
                jessica.move_for_seconds(5, "north", speed_mtps=10)
                # East Leg (5s)
                jessica.face("east")
                jessica.move_for_seconds(5, "east", speed_mtps=10)
                # South Leg (5s)
                jessica.face("south")
                jessica.move_for_seconds(5, "south", speed_mtps=10)
                # West Leg (5s)
                jessica.face("west")
                jessica.move_for_seconds(5, "west", speed_mtps=10)

            with group.for_actor("Sarah") as sarah:
                sarah.animation("Jog_Fwd")
                sarah.face("north", duration=0.5)
                # Matches Jessica leg for leg
                sarah.move_for_seconds(5, "north", speed_mtps=10)
                sarah.face("east")
                sarah.move_for_seconds(5, "east", speed_mtps=10)
                sarah.face("south")
                sarah.move_for_seconds(5, "south", speed_mtps=10)
                sarah.face("west")
                sarah.move_for_seconds(5, "west", speed_mtps=10)

        # Camera Cuts (Scheduled on timeline)
        movie.at_time(5.0).camera_cut("Corner3Cam")
        movie.at_time(10.0).camera_cut("Side3Cam")
        movie.at_time(15.0).camera_cut("Corner1Cam")
        
    return movie.build()

MOVIE = define_movie()
