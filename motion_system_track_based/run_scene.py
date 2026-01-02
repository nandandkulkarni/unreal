"""
Run Scene - Unreal-side execution script

This script is executed inside Unreal Engine via Remote Control.
It orchestrates the motion planning and sequence creation.

Environment:
    MOVIE_FOLDER_PATH: Path to movie folder (set by trigger_movie.py)
"""

import os
import sys

# Add motion_system_track_based to path
sys.path.insert(0, os.path.dirname(__file__))

def run_scene(movie_folder: str):
    """
    Main entry point for Unreal-side execution.
    
    Args:
        movie_folder: Absolute path to movie folder
    
    Process:
        1. Import planner and applier modules
        2. Call plan_motion(movie_folder)
        3. Create/get LevelSequence
        4. Apply keyframes to sequence
        5. Play sequence
    """
    import unreal
    import motion_planner
    from motion_includes import sequence_setup, keyframe_applier
    
    unreal.log(f"=== Running Scene from: {movie_folder} ===")
    
    # TODO: Implement
    # 1. Load meta.json for fps and duration
    # 2. Create level sequence
    # 3. Call motion_planner.plan_motion(movie_folder)
    # 4. For each actor, apply keyframes
    # 5. Add camera cuts
    # 6. Play sequence
    
    raise NotImplementedError()


if __name__ == "__main__":
    # For testing outside Unreal
    import json
    folder = os.environ.get("MOVIE_FOLDER_PATH", "dist/test/")
    print(f"Would run scene from: {folder}")
