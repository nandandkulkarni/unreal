"""
Overhead Runners Scene
Two runners moving North, tracked by a high-angle front camera.
Uses Typed Units and Direction Enum.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder, Direction, DistanceUnit, SpeedUnit, TimeUnit

def define_movie():
    with MovieBuilder("Overhead Runners", fps=60) as movie:
        #movie.add_floor("Track", location=(0, 0, -0.5), scale=2000)
        #movie.add_directional_light("Sun", intensity="bright")

        # Two runners starting at origin, slightly offset in Y
        # Facing North (Positive X)
        movie.add_actor("Runner1", location=(0, -150, 0), yaw_offset=-90)
        movie.add_actor("Runner2", location=(0, 150, 0), yaw_offset=-90)

        # Camera 1: Overhead Front (Tracking Runner 1)
        movie.add_camera("OverheadFrontCam", location=(4000, 0, 1500)) \
             .look_at("Runner1") \
             .add()

        # Camera 2: Static Overhead (50m North, 10m High)
        movie.add_camera("StaticOverheadCam", location=(5000, 0, 1000)) \
             .rotation((0, 0, 90)) \
             .add()

        movie.at_time(0).camera_cut("OverheadFrontCam")
        movie.at_time(6).camera_cut("StaticOverheadCam")

        with movie.simultaneous():
            with movie.for_actor("Runner1") as r1:
                # Runner 1: Weave NE -> NW -> NE
                r1.face(Direction.NORTH_EAST, 0.2).move_straight().direction(Direction.NORTH_EAST).anim("Jog_Fwd") \
                  .distance_at_speed((DistanceUnit.Meters, 30), (SpeedUnit.MetersPerSecond, 6))
                r1.face(Direction.NORTH_WEST, 0.2).move_straight().direction(Direction.NORTH_WEST).anim("Jog_Fwd") \
                  .distance_at_speed((DistanceUnit.Meters, 30), (SpeedUnit.MetersPerSecond, 6))
                r1.face(Direction.NORTH_EAST, 0.2).move_straight().direction(Direction.NORTH_EAST).anim("Jog_Fwd") \
                  .distance_at_speed((DistanceUnit.Meters, 30), (SpeedUnit.MetersPerSecond, 6))
                r1.stay().till_end().anim("Idle")

            with movie.for_actor("Runner2") as r2:
                # Runner 2: Weave NW -> NE -> NW
                r2.stay().for_time(2.0).anim("Idle")
                r2.face(Direction.NORTH_WEST, 0.2).move_straight().direction(Direction.NORTH_WEST).anim("Jog_Fwd") \
                  .distance_at_speed((DistanceUnit.Meters, 30), (SpeedUnit.MetersPerSecond, 6))
                r2.face(Direction.NORTH_EAST, 0.2).move_straight().direction(Direction.NORTH_EAST).anim("Jog_Fwd") \
                  .distance_at_speed((DistanceUnit.Meters, 30), (SpeedUnit.MetersPerSecond, 6))
                r2.face(Direction.NORTH_WEST, 0.2).move_straight().direction(Direction.NORTH_WEST).anim("Jog_Fwd") \
                  .distance_at_speed((DistanceUnit.Meters, 30), (SpeedUnit.MetersPerSecond, 6))
                r2.stay().till_end().anim("Idle")

        movie.save_to_tracks("dist/")

    movie.run(to_unreal=True)

if __name__ == "__main__":
    define_movie()
