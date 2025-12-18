"""
Pure Unreal Python Script - Add Mannequin to Sequence

This script runs INSIDE Unreal Engine's Python interpreter.
It finds the most recent Test* sequence and adds TestMannequin1 to it.
"""
import unreal
import os
from datetime import datetime

# Configuration
MANNEQUIN_NAME = "TestMannequin1"
log_file = r"C:\RemoteProjects\functional\add_mannequin_log.txt"
log_lines = []

def log_to_file(message):
    """Log message to both console and file buffer"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_line = "[" + timestamp + "] " + message
    log_lines.append(log_line)
    print(message)

# Start logging
log_to_file("=" * 60)
log_to_file("Adding Mannequin to Sequence")
log_to_file("=" * 60)

try:
    # Find the most recent sequence starting with "Test"
    log_to_file("\nFinding most recent Test* sequence...")
    sequences_path = "/Game/Sequences"

    if not unreal.EditorAssetLibrary.does_directory_exist(sequences_path):
        log_to_file("✗ ERROR: Sequences directory not found: " + sequences_path)
        sequence = None
    else:
        assets = unreal.EditorAssetLibrary.list_assets(sequences_path, recursive=False)
        
        # Filter for sequences starting with "Test"
        test_sequences = []
        for asset_path in assets:
            asset_name = asset_path.split('/')[-1].split('.')[0]
            if asset_name.startswith("Test"):
                test_sequences.append(asset_path)
        
        if len(test_sequences) == 0:
            log_to_file("✗ ERROR: No sequences starting with 'Test' found")
            log_to_file("  Use create_sequence.py to create one first")
            sequence = None
        else:
            # Use the last one in the list (most recent alphabetically with timestamps)
            sequence_path = test_sequences[-1]
            sequence = unreal.load_asset(sequence_path)
            
            if sequence:
                log_to_file("✓ Found " + str(len(test_sequences)) + " Test* sequence(s)")
                log_to_file("✓ Using most recent: " + sequence.get_name())
                log_to_file("  Path: " + sequence_path)
            else:
                log_to_file("✗ ERROR: Failed to load sequence: " + sequence_path)

    if not sequence:
        log_to_file("✗ ERROR: No valid sequence found")
        log_to_file("  Make sure at least one Test* sequence exists in /Game/Sequences/")
    else:
        log_to_file("✓ Sequence loaded: " + sequence.get_name())
    
    # Get all bindings in the sequence
    log_to_file("\nRemoving existing test mannequin bindings...")
    bindings = unreal.MovieSceneSequenceExtensions.get_bindings(sequence)
    removed_count = 0
    
    for binding in bindings:
        binding_name = str(binding.get_display_name())  # Convert Unreal Text to string
        if binding_name.startswith("TestMannequin"):
            log_to_file("  Removing: " + binding_name)
            sequence.remove_possessable(binding.get_id())
            removed_count += 1
    
    if removed_count > 0:
        log_to_file("✓ Removed " + str(removed_count) + " test mannequin binding(s)")
    else:
        log_to_file("  No test mannequin bindings found")
    
    # Find the mannequin actor in the level
    log_to_file("\nFinding mannequin: " + MANNEQUIN_NAME)
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    all_actors = editor_actor_subsystem.get_all_level_actors()
    
    mannequin_actor = None
    for actor in all_actors:
        if actor.get_actor_label() == MANNEQUIN_NAME:
            mannequin_actor = actor
            log_to_file("✓ Found mannequin: " + actor.get_actor_label())
            log_to_file("  Class: " + actor.get_class().get_name())
            log_to_file("  Location: " + str(actor.get_actor_location()))
            break
    
    if not mannequin_actor:
        log_to_file("✗ ERROR: Mannequin not found: " + MANNEQUIN_NAME)
        log_to_file("  Make sure the mannequin exists in the level")
        log_to_file("  Use create_mannequin.py to create one first")
    else:
        # Add mannequin to sequence as possessable
        log_to_file("\nAdding mannequin to sequence...")
        binding = unreal.MovieSceneSequenceExtensions.add_possessable(sequence, mannequin_actor)
            
        if not binding:
            log_to_file("✗ ERROR: Failed to create binding")
        else:
            log_to_file("✓ Mannequin added to sequence!")
            log_to_file("  Binding name: " + binding.get_display_name())
            log_to_file("  Binding ID: " + str(binding.get_id()))
            
            # Add transform track
            log_to_file("\nAdding transform track...")
            transform_track = unreal.MovieSceneBindingExtensions.add_track(
                binding,
                unreal.MovieScene3DTransformTrack
            )
            
            if transform_track:
                log_to_file("✓ Transform track added")
                
                # Add section to the track
                section = unreal.MovieSceneTrackExtensions.add_section(transform_track)
                
                # Set section to cover the entire sequence
                playback_start = unreal.MovieSceneSequenceExtensions.get_playback_start(sequence)
                playback_end = unreal.MovieSceneSequenceExtensions.get_playback_end(sequence)
                unreal.MovieSceneSectionExtensions.set_range(section, playback_start, playback_end)
                
                log_to_file("✓ Section added (range: " + str(playback_start) + " to " + str(playback_end) + " frames)")
            else:
                log_to_file("⚠ Warning: Failed to add transform track")
            
            # Add skeletal animation track for the mannequin
            log_to_file("\nAdding skeletal animation track...")
            anim_track = unreal.MovieSceneBindingExtensions.add_track(
                binding,
                unreal.MovieSceneSkeletalAnimationTrack
            )
            
            if anim_track:
                log_to_file("✓ Skeletal animation track added")
                
                # Add section to animation track
                anim_section = unreal.MovieSceneTrackExtensions.add_section(anim_track)
                unreal.MovieSceneSectionExtensions.set_range(anim_section, playback_start, playback_end)
                log_to_file("✓ Animation section added")
            else:
                log_to_file("⚠ Warning: Failed to add skeletal animation track")
            
            # Save the sequence
            log_to_file("\nSaving sequence...")
            saved = unreal.EditorAssetLibrary.save_loaded_asset(sequence)
            if saved:
                log_to_file("✓ Sequence saved")
            
            # Open the sequence in Sequencer
            log_to_file("\nOpening sequence in Sequencer...")
            unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(sequence)
            log_to_file("✓ Sequence opened in Sequencer")
            
            log_to_file("=" * 60)
            log_to_file("✓ Mannequin successfully added to sequence!")
            log_to_file("  Sequence: " + sequence.get_name())
            log_to_file("  Mannequin: " + mannequin_actor.get_actor_label())
            log_to_file("=" * 60)
            
            # Verify by checking bindings again
            log_to_file("\nVerifying...")
            bindings_after = unreal.MovieSceneSequenceExtensions.get_bindings(sequence)
            found = False
            for binding in bindings_after:
                if str(binding.get_display_name()) == MANNEQUIN_NAME:
                    found = True
                    log_to_file("✓ Verified: '" + str(binding.get_display_name()) + "' is in sequence")
                    
                    # Get tracks
                    tracks = unreal.MovieSceneBindingExtensions.get_tracks(binding)
                    log_to_file("  Tracks: " + str(len(tracks)))
                    for track in tracks:
                        log_to_file("    - " + track.get_class().get_name())
                    break
            
            if not found:
                log_to_file("✗ ERROR: Could not verify '" + MANNEQUIN_NAME + "' in sequence bindings!")
            
            # List all members in the sequence
            log_to_file("\n" + "=" * 60)
            log_to_file("All members in sequence:")
            log_to_file("=" * 60)
            all_bindings = unreal.MovieSceneSequenceExtensions.get_bindings(sequence)
            log_to_file("Total bindings: " + str(len(all_bindings)))
            for idx, binding in enumerate(all_bindings, 1):
                log_to_file("  " + str(idx) + ". " + str(binding.get_display_name()))
                tracks = unreal.MovieSceneBindingExtensions.get_tracks(binding)
                log_to_file("     Tracks: " + str(len(tracks)))
                for track in tracks:
                    log_to_file("       - " + track.get_class().get_name())
            log_to_file("=" * 60)

except Exception as e:
    log_to_file("\n" + "=" * 60)
    log_to_file("✗ FATAL ERROR")
    log_to_file("=" * 60)
    log_to_file("Error type: " + type(e).__name__)
    log_to_file("Error message: " + str(e))
    
    # Get full traceback
    import traceback
    log_to_file("\nFull traceback:")
    for line in traceback.format_exc().split('\n'):
        if line:
            log_to_file("  " + line)
    log_to_file("=" * 60)

# Write all logs to file
try:
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(log_lines))
    log_to_file("\nLog written to: " + log_file)
except Exception as e:
    log_to_file("Failed to write log file: " + str(e))
