"""
Add Mannequin to Sequence in Unreal Engine

This script adds a mannequin to an existing sequence.
Removes any existing test mannequins from the sequence first.
Run from PowerShell - it will execute the code inside Unreal Engine.

Usage:
    python add_mannequin_to_sequence.py [sequence_name] [mannequin_name]
"""

from unreal_connection import UnrealRemote


def add_mannequin_to_sequence(sequence_name="TestSequence1", mannequin_name="TestMannequin1"):
    """
    Add a mannequin to an existing sequence
    
    Args:
        sequence_name: Name of the sequence to add to
        mannequin_name: Name of the mannequin actor to add
    """
    
    # Python code to execute inside Unreal
    # Using triple quotes and .format() to avoid f-string escaping issues
    code = """
import unreal
import os
from datetime import datetime

# Setup logging to file
log_file = r"C:\\RemoteProjects\\functional\\add_mannequin_log.txt"
log_lines = []

def log_to_file(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_line = f"[{{timestamp}}] {{message}}"
    log_lines.append(log_line)
    print(message)  # Also print to Unreal console

log_to_file("=" * 60)
log_to_file("Adding Mannequin to Sequence")
log_to_file("=" * 60)

# Find the most recent sequence starting with "Test"
log_to_file("\\nFinding most recent Test* sequence...")
sequences_path = "/Game/Sequences"

if not unreal.EditorAssetLibrary.does_directory_exist(sequences_path):
    log_to_file(f"✗ ERROR: Sequences directory not found: {{sequences_path}}")
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
            log_to_file(f"✓ Found {{len(test_sequences)}} Test* sequence(s)")
            log_to_file(f"✓ Using most recent: {{sequence.get_name()}}")
            log_to_file(f"  Path: {{sequence_path}}")
        else:
            log_to_file(f"✗ ERROR: Failed to load sequence: {{sequence_path}}")

if not sequence:
    log_to_file(f"✗ ERROR: Sequence not found: {{sequence_path}}")
    log_to_file("  Make sure the sequence exists in /Game/Sequences/")
else:
    log_to_file(f"✓ Sequence loaded: {{sequence.get_name()}}")
    
    # Get all bindings in the sequence
    log_to_file("\nRemoving existing test mannequin bindings...")
    bindings = unreal.MovieSceneSequenceExtensions.get_bindings(sequence)
    removed_count = 0
    
    for binding in bindings:
        binding_name = binding.get_display_name()
        if binding_name.startswith("TestMannequin"):
            log_to_file(f"  Removing: {{binding_name}}")
            unreal.MovieSceneSequenceExtensions.remove_possessable(sequence, binding.get_id())
            removed_count += 1
    
    if removed_count > 0:
        log_to_file(f"✓ Removed {{removed_count}} test mannequin binding(s)")
    else:
        log_to_file("  No test mannequin bindings found")
    
    # Find the mannequin actor in the level
    log_to_file("\nFinding mannequin: {mannequin_name}")
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    all_actors = editor_actor_subsystem.get_all_level_actors()
    
    mannequin_actor = None
    for actor in all_actors:
        if actor.get_actor_label() == "{mannequin_name}":
            mannequin_actor = actor
            log_to_file(f"✓ Found mannequin: {{actor.get_actor_label()}}")
            log_to_file(f"  Class: {{actor.get_class().get_name()}}")
            log_to_file(f"  Location: {{actor.get_actor_location()}}")
            break
    
    if not mannequin_actor:
        log_to_file("✗ ERROR: Mannequin not found: {mannequin_name}")
        log_to_file("  Make sure the mannequin exists in the level")
        log_to_file("  Use create_mannequin.py to create one first")
    else:
        # Add mannequin to sequence as possessable
        log_to_file("\nAdding mannequin to sequence...")
        binding = unreal.MovieSceneSequenceExtensions.add_possessable(sequence, mannequin_actor)
        
        if not binding:
            log_to_file("✗ ERROR: Failed to create binding")
        else:
            log_to_file(f"✓ Mannequin added to sequence!")
            log_to_file(f"  Binding name: {{binding.get_display_name()}}")
            log_to_file(f"  Binding ID: {{binding.get_id()}}")
            
            # Add transform track
            log_to_file("\nAdding transform track...")
            transform_track = unreal.MovieSceneBindingExtensions.add_track(
                binding,
                unreal.MovieScene3DTransformTrack
            )
            
            if transform_track:
                log_to_file(f"✓ Transform track added")
                
                # Add section to the track
                section = unreal.MovieSceneTrackExtensions.add_section(transform_track)
                
                # Set section to cover the entire sequence
                playback_start = unreal.MovieSceneSequenceExtensions.get_playback_start(sequence)
                playback_end = unreal.MovieSceneSequenceExtensions.get_playback_end(sequence)
                unreal.MovieSceneSectionExtensions.set_range(section, playback_start, playback_end)
                
                log_to_file(f"✓ Section added (range: {{playback_start}} to {{playback_end}} frames)")
            else:
                log_to_file("⚠ Warning: Failed to add transform track")
            
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
            log_to_file(f"  Sequence: {{sequence.get_name()}}")
            log_to_file(f"  Mannequin: {{mannequin_actor.get_actor_label()}}")
            log_to_file("=" * 60)
            
            # Verify by checking bindings again
            log_to_file("\nVerifying...")
            bindings_after = unreal.MovieSceneSequenceExtensions.get_bindings(sequence)
            found = False
            for binding in bindings_after:
                if binding.get_display_name() == "{mannequin_name}":
                    found = True
                    log_to_file(f"✓ Verified: '{{binding.get_display_name()}}' is in sequence")
                    
                    # Get tracks
                    tracks = unreal.MovieSceneBindingExtensions.get_tracks(binding)
                    log_to_file(f"  Tracks: {{len(tracks)}}")
                    for track in tracks:
                        log_to_file(f"    - {{track.get_class().get_name()}}")
                    break
            
            if not found:
                log_to_file("✗ ERROR: Could not verify '{mannequin_name}' in sequence bindings!")
            
            # List all members in the sequence
            log_to_file("\n" + "=" * 60)
            log_to_file("All members in sequence:")
            log_to_file("=" * 60)
            all_bindings = unreal.MovieSceneSequenceExtensions.get_bindings(sequence)
            log_to_file(f"Total bindings: {{len(all_bindings)}}")
            for idx, binding in enumerate(all_bindings, 1):
                log_to_file(f"  {{idx}}. {{binding.get_display_name()}}")
                tracks = unreal.MovieSceneBindingExtensions.get_tracks(binding)
                log_to_file(f"     Tracks: {{len(tracks)}}")
                for track in tracks:
                    log_to_file(f"       - {{track.get_class().get_name()}}")
            log_to_file("=" * 60)

# Write all logs to file
try:
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("\\n".join(log_lines))
    print("\\nLog written to: " + log_file)
except Exception as e:
    print("Failed to write log file: " + str(e))
""".format(mannequin_name=mannequin_name)
    
    # Connect to Unreal and execute
    unreal = UnrealRemote()
    
    if not unreal.is_connected():
        print("✗ Cannot connect to Unreal Engine!")
        print("Make sure Unreal is running and WebControl.StartServer has been executed.")
        return False
    
    print(f"Adding '{mannequin_name}' to most recent Test* sequence...")
    success, result = unreal.execute_python(code)
    
    if success:
        print("\\n✓ Operation completed!")
        print("Check Unreal Engine's Sequencer to see the mannequin.")
        return True
    else:
        print(f"\\n✗ Failed: {result}")
        return False


def main():
    """Main entry point"""
    import sys
    
    # Get parameters from command line or use defaults
    sequence_name = sys.argv[1] if len(sys.argv) > 1 else "TestSequence1"
    mannequin_name = sys.argv[2] if len(sys.argv) > 2 else "TestMannequin1"
    
    add_mannequin_to_sequence(sequence_name, mannequin_name)


if __name__ == "__main__":
    main()
