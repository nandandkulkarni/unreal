import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from motion_builder import MovieBuilder, Direction, DistanceUnit, SpeedUnit, LightType

def create_movie():
    belica_path = "/Game/Characters/Belica/Mesh/SK_Belica"
    
    with MovieBuilder("Sprint Socket Tracking", fps=60) as movie:
        
        # 1. Setup Environment
        #movie.add_floor("Floor", scale=100.0)
        #movie.add_light_directional("Sun") \
        #     .intensity(4.0) \
        #     .rotation(pitch=-45, yaw=-45, roll=0)
             
        #movie.add_light_sky("Sky").intensity(1.0)
        
        # 2. Add Runners
        # Runner 1 - Lane 1
        movie.add_actor("Runner1", location=(0, 0, 0), yaw_offset=-90, mesh_path=belica_path)
        
        # 3. Add Proxy Target for Head Tracking
        # Spawn at 0,0,0 (will be snapped to head)
        movie.add_target_actor("Runner1_HeadTarget", location=(0, 0, 0))
        
        # Attach Target to Runner1's Head
        with movie.for_actor("Runner1_HeadTarget") as target:
            target.attach_to("Runner1", socket="head", 
                             location_rule="SNAP_TO_TARGET", 
                             rotation_rule="SNAP_TO_TARGET")
        
        # 4. Add Camera tracking the Head Target
        movie.add_camera("HeadCam", location=(11000, 0, 200)) \
             .look_at("Runner1_HeadTarget") \
             .focus_on("Runner1_HeadTarget") \
             .add()
             
        # 5. Motion
        with movie.simultaneous():
            # Runner 1 Sprints North
            with movie.for_actor("Runner1") as r1:
                r1.face(Direction.NORTH)
                r1.move_straight() \
                    .direction(Direction.NORTH) \
                    .anim("Jog_Fwd") \
                    .distance_at_speed((DistanceUnit.Meters, 20), (SpeedUnit.MetersPerSecond, 6))
                r1.stay().till_end().anim("Idle")
            
            # # Camera moves alongside
            # with movie.for_actor("HeadCam") as cam:
            #     # Basic move alongside
            #     cam.move_to_location((300, 2300, 180), speed_mtps=6.0)

        movie.save_to_tracks("dist/")
        
    return movie

if __name__ == "__main__":
    movie = create_movie()
    movie.run(to_unreal=True)
