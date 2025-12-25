""" 
Sequence creation and configuration
"""
import unreal
from datetime import datetime
from ..logger import log, log_header


def get_next_sequence_number():
    """Find existing Test* sequences to determine next number"""
    sequences_path = "/Game/Sequences"
    next_num = 1

    if unreal.EditorAssetLibrary.does_directory_exist(sequences_path):
        assets = unreal.EditorAssetLibrary.list_assets(sequences_path, recursive=False)
        existing_nums = []
        for asset_path in assets:
            asset_name = asset_path.split('/')[-1].split('.')[0]
            if asset_name.startswith("TestSequence_"):
                # Extract number from name like TestSequence_25_12_18_02_20_42_001
                parts = asset_name.split('_')
                if len(parts) >= 8:  # Has timestamp and number
                    try:
                        num = int(parts[-1])
                        existing_nums.append(num)
                    except Exception:
                        pass

        if existing_nums:
            next_num = max(existing_nums) + 1

    return next_num


def create_sequence(fps=30, duration_seconds=60, test_name=None):
    """Create a new level sequence with timestamp and optional test name"""
    log_header("STEP 2: Creating new sequence")

    # Get timestamp and find next sequence number
    timestamp = datetime.now().strftime("%y_%m_%d_%H_%M_%S")
    next_num = get_next_sequence_number()

    # Format sequence name with test name if provided
    if test_name:
        # Sanitize test name for use in asset name
        safe_name = test_name.replace(" ", "_").replace("-", "_")
        sequence_name = f"TestSequence_{safe_name}_{timestamp}_{next_num:03d}"
    else:
        sequence_name = f"TestSequence_{timestamp}_{next_num:03d}"
    
    log(f"\nCreating scene #{next_num}")
    log(f"  Sequence: {sequence_name}")

    sequence_path = f"/Game/Sequences/{sequence_name}"
    factory = unreal.LevelSequenceFactoryNew()
    sequence = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        sequence_name,
        "/Game/Sequences",
        unreal.LevelSequence,
        factory
    )

    if sequence:
        log(f"✓ Sequence created: {sequence_name}")

        # Set sequence properties
        duration_frames = int(fps * duration_seconds)

        # Set playback range
        sequence.set_playback_start(0)
        sequence.set_playback_end(duration_frames)
        sequence.set_display_rate(unreal.FrameRate(numerator=int(fps), denominator=1))

        log(f"  FPS: {fps}")
        log(f"  Duration: {duration_seconds}s ({duration_frames} frames)")
        
        return sequence, sequence_name, next_num, fps, duration_frames
    else:
        log("✗ ERROR: Failed to create sequence")
        raise Exception("Sequence creation failed")

def add_actor_to_sequence(sequence, actor, actor_name="Actor"):
    """Add actor to sequence as possessable and return binding"""
    import logger
    
    logger.log(f"Adding {actor_name} to sequence...")
    binding = unreal.MovieSceneSequenceExtensions.add_possessable(sequence, actor)
    logger.log(f"✓ {actor_name} added to sequence")
    
    return binding


def apply_camera_cuts(sequence, camera_cuts, actors_info, fps):
    """Apply camera cuts to sequence
    
    Args:
        sequence: Level sequence
        camera_cuts: List of {"camera": name, "time": seconds} dicts
        actors_info: Dictionary of actor information including bindings
        fps: Frames per second
    """
    from ..logger import log
    
    if not camera_cuts:
        log("  No camera cuts to apply")
        return
    
    log(f"\nApplying {len(camera_cuts)} camera cut(s)...")
    
    # Get or create camera cuts track using the same API as motion_commands.py
    camera_cut_track = sequence.add_track(unreal.MovieSceneCameraCutTrack)
    
    # Sort cuts by time
    sorted_cuts = sorted(camera_cuts, key=lambda x: x["time"])
    
    # Add camera cut sections
    for i, cut in enumerate(sorted_cuts):
        camera_name = cut["camera"]
        start_time = cut["time"]
        start_frame = int(start_time * fps)
        
        # Determine end frame (next cut or sequence end)
        if i + 1 < len(sorted_cuts):
            end_frame = int(sorted_cuts[i + 1]["time"] * fps)
        else:
            # Last cut goes to end of sequence
            end_frame = sequence.get_playback_end()
        
        # Get camera binding
        if camera_name not in actors_info:
            log(f"  ⚠ Camera '{camera_name}' not found, skipping cut")
            continue
        
        camera_binding = actors_info[camera_name].get("binding")
        if not camera_binding:
            log(f"  ⚠ Camera '{camera_name}' has no binding, skipping cut")
            continue
        
        # Create camera cut section
        section = camera_cut_track.add_section()
        section.set_range(start_frame, end_frame)
        
        # Set camera binding
        binding_id = unreal.MovieSceneObjectBindingID()
        binding_id.set_editor_property("guid", camera_binding.get_id())
        section.set_camera_binding_id(binding_id)
        
        log(f"  ✓ Cut {i+1}: {camera_name} from {start_time}s (frame {start_frame}) to frame {end_frame}")
    
    log(f"✓ Applied {len(sorted_cuts)} camera cut(s)")
