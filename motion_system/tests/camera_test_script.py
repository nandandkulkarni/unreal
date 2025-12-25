import sys
import unreal
import os

# Add motion_system to path
motion_system_dir = 'C:/UnrealProjects/Coding/unreal/motion_system'
if motion_system_dir not in sys.path:
    sys.path.insert(0, motion_system_dir)

import motion_planner
import motion_commands
from motion_includes import sequence_setup
from motion_includes import camera_setup
from motion_includes import cleanup
import logger
import importlib

# Reload modules to ensure latest changes are used
importlib.reload(motion_planner)
importlib.reload(motion_commands)
importlib.reload(sequence_setup)
importlib.reload(camera_setup)
importlib.reload(cleanup)
importlib.reload(logger)

def main():
    try:
        # 1. Cleanup
        cleanup.cleanup_old_assets()

        # 2. Create Sequence
        sequence, sequence_name, _, fps, duration_frames = sequence_setup.create_sequence(fps=30, duration_seconds=5, test_name="CameraTest")

        # 3. Create Camera
        camera = camera_setup.create_camera("CineCameraActor")

        # 4. Define Motion Plan (Camera Move)
        motion_plan = [
            {"actor": "camera", "command": "wait", "seconds": 1.0},
            {"actor": "camera", "command": "camera_move", "location": [200, 200, 150], "rotation": [0, -45, 0], "duration": 2.0},
            {"actor": "camera", "command": "wait", "seconds": 2.0}
        ]

        # 5. Plan Motion
        actors_info = {
            "camera": {"location": camera.get_actor_location(), "rotation": camera.get_actor_rotation()}
        }
        keyframe_data = motion_planner.plan_motion(motion_plan, actors_info, fps, sequence=sequence)

        # 6. Apply to Sequence
        motion_commands.add_camera_with_motion(sequence, camera, fps, duration_frames, keyframe_data["camera"]["keyframes"])

        # 7. Finalize
        motion_commands.finalize_sequence(sequence, sequence_name)

        print("Camera Test Sequence Created Successfully")
        return "SUCCESS"
    except Exception as e:
        import traceback
        # Use simple string concatenation to avoid potential f-string/newline issues in remote execution
        error_header = "ERROR: " + str(e)
        trace = traceback.format_exc()
        print(error_header)
        print(trace)
        return error_header + chr(10) + trace

main()
