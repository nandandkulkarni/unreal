"""
Audio Test - Minimal test to verify audio track creation
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from motion_builder import MovieBuilder, TimeSpan

def define_movie():
    with MovieBuilder("Audio Test", fps=60) as movie:
        # Add a simple actor
        movie.add_actor("TestActor", location=(0, 0, 0), yaw_offset=-90)
        
        with movie.for_actor("TestActor") as a:
            # Just stay in place for the whole duration
            a.stay().anim("Idle").till_end()
        
        # Add a test audio track
        # Using the requested specific track
        movie.add_audio(
            asset_path="/Game/MyAudio/Sopranos_-_High_Quality.Sopranos_-_High_Quality", 
            start_time=0.0
            # duration is omitted to test auto-calculation
        )
        
        # Add a simple camera
        movie.add_camera("MainCam", location=(0, -500, 200)).add()
        with movie.for_camera("MainCam") as cam:
            cam.look_at("TestActor")
            cam.wait(10.0)
        
        movie.at_time(0.0).camera_cut("MainCam")
    
    movie.save_to_json("dist/audio_test.json")
    movie.run(to_unreal=True)
    return movie.build()

if __name__ == "__main__":
    define_movie()
