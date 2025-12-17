"""
Fix camera binding in Camera Cut track
Run this inside Unreal: Tools -> Execute Python Script

Check logs in: 
1. Window -> Developer Tools -> Output Log (in Unreal)
2. C:/U/CinematicPipeline_Scripts/logs/camera_binding_fix.log (file on disk)

After running check the log with:
    python C:/U/CinematicPipeline_Scripts/view_logs.py
"""

import unreal
import os
from datetime import datetime

# Setup logging
LOG_DIR = "C:/U/CinematicPipeline_Scripts/logs"
LOG_FILE = os.path.join(LOG_DIR, "camera_binding_fix.log")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def log(message):
    """Log to both console and file"""
    print(message)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {message}\n")

def fix_camera_binding():
    """Fix the No Object Binding specified error in Camera Cut track"""
    
    log("\n" + "=" * 70)
    log("CAMERA BINDING FIX SCRIPT - STARTING")
    log("=" * 70)
    log(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"Log file: {LOG_FILE}")
    log("=" * 70 + "\n")
    
    # [1/8] Load the sequence
    sequence_path = '/Game/Sequences/CharacterWalkSequence'
    log(f"[1/8] Loading sequence: {sequence_path}")
    sequence = unreal.load_asset(sequence_path)
    
    if not sequence:
        log(f"FAILED: Could not load sequence: {sequence_path}")
        return False
    
    log(f"SUCCESS: Loaded sequence: {sequence.get_name()}")
    
    # [2/8] Get the camera actor from the level
    log(f"\n[2/8] Looking for CineCameraActor in level...")
    camera = None
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    log(f"   Total actors in level: {len(all_actors)}")
    
    for actor in all_actors:
        if isinstance(actor, unreal.CineCameraActor):
            camera = actor
            log(f"   Found camera type: {type(actor).__name__}")
            break
    
    if not camera:
        log("FAILED: No CineCameraActor found in level")
        return False
    
    log(f"SUCCESS: Found camera: {camera.get_name()}")
    
    # [3/8] Find or create camera binding
    log(f"\n[3/8] Checking camera binding in sequence...")
    camera_binding = None
    possessables = sequence.get_possessables()
    log(f"   Total possessable bindings: {len(possessables)}")
    
    try:
        for binding in possessables:
            binding_name = str(binding.get_display_name())
            log(f"   Checking binding: {binding_name}")
            if camera.get_name() in binding_name:
                camera_binding = binding
                log(f"SUCCESS: Found existing camera binding")
                break
    except Exception as e:
        log(f"   Warning while checking bindings: {e}")
    
    if not camera_binding:
        try:
            log(f"   Creating new camera binding...")
            camera_binding = sequence.add_possessable(camera)
            log(f"SUCCESS: Created new camera binding")
        except Exception as e:
            log(f"FAILED to create binding: {e}")
            return False
    
    # [4/8] Find the Camera Cut track
    log(f"\n[4/8] Finding Camera Cut track...")
    camera_cut_track = None
    
    try:
        movie_scene = sequence.get_movie_scene()
        master_tracks = movie_scene.get_master_tracks()
        log(f"   Total master tracks: {len(master_tracks)}")
        
        for master_track in master_tracks:
            track_type = type(master_track).__name__
            log(f"   Track type: {track_type}")
            if isinstance(master_track, unreal.MovieSceneCameraCutTrack):
                camera_cut_track = master_track
                break
    except Exception as e:
        log(f"FAILED: Error getting master tracks: {e}")
        return False
    
    if not camera_cut_track:
        log("FAILED: No Camera Cut track found in sequence")
        return False
    
    log(f"SUCCESS: Found Camera Cut track")
    
    # [5/8] Get the camera cut section
    log(f"\n[5/8] Getting Camera Cut section...")
    
    try:
        sections = camera_cut_track.get_sections()
        log(f"   Sections in Camera Cut track: {len(sections)}")
        
        if not sections:
            log("FAILED: No sections in Camera Cut track")
            return False
        
        camera_cut_section = sections[0]
        log(f"SUCCESS: Found Camera Cut section")
    except Exception as e:
        log(f"FAILED: Error getting sections: {e}")
        return False
    
    # [6/8] Check current binding state
    log(f"\n[6/8] Checking current binding state...")
    
    try:
        current_binding = camera_cut_section.get_editor_property('camera_binding_id')
        log(f"   Current binding GUID: {current_binding.guid}")
        log(f"   Target camera binding GUID: {camera_binding.get_id()}")
    except Exception as e:
        log(f"   Warning: Could not read current binding: {e}")
    
    # [7/8] Fix the binding
    log(f"\n[7/8] Applying camera binding fix...")
    
    try:
        camera_binding_id = camera_cut_section.get_editor_property('camera_binding_id')
        camera_binding_id.guid = camera_binding.get_id()
        camera_cut_section.set_editor_property('camera_binding_id', camera_binding_id)
        
        new_binding = camera_cut_section.get_editor_property('camera_binding_id')
        log(f"   New binding GUID: {new_binding.guid}")
        log("SUCCESS: Camera binding assigned to Camera Cut track")
    except Exception as e:
        log(f"FAILED to apply binding: {e}")
        return False
    
    # [8/8] Save the sequence
    log(f"\n[8/8] Saving sequence...")
    
    try:
        unreal.EditorAssetLibrary.save_loaded_asset(sequence)
        log("SUCCESS: Sequence saved to disk")
    except Exception as e:
        log(f"Warning: Could not save sequence: {e}")
    
    log("\n" + "=" * 70)
    log("ALL STEPS COMPLETED SUCCESSFULLY")
    log("=" * 70)
    log("Camera binding has been fixed!")
    log("The No Object Binding specified error should be gone.")
    log("\nNEXT STEPS:")
    log("1. Check the Camera Cut track in Sequencer")
    log("2. Run remote playback test:")
    log("   python C:/U/CinematicPipeline_Scripts/external_control/test_sequence_playback.py")
    log("3. View this log file:")
    log("   python C:/U/CinematicPipeline_Scripts/view_logs.py")
    log("=" * 70 + "\n")
    
    return True

if __name__ == "__main__":
    try:
        success = fix_camera_binding()
        if not success:
            log("\nSCRIPT FAILED - Check error messages above\n")
    except Exception as e:
        log("\nEXCEPTION OCCURRED:")
        log(f"Error: {str(e)}")
        log(f"Type: {type(e).__name__}")
        import traceback
        import io
        tb_str = io.StringIO()
        traceback.print_exc(file=tb_str)
        log("\nFull traceback:")
        log(tb_str.getvalue())
