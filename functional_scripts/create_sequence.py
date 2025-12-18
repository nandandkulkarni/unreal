"""
Create a Level Sequence in Unreal Engine

This script creates a new Level Sequence in the current Unreal project.
Run from PowerShell - it will execute the code inside Unreal Engine.

Usage:
    python create_sequence.py
"""

from unreal_connection import UnrealRemote


def create_sequence(sequence_name="MySequence", duration_seconds=10.0, fps=30):
    """
    Create a new Level Sequence in Unreal
    
    Args:
        sequence_name: Name for the sequence
        duration_seconds: Length of sequence in seconds
        fps: Frames per second
    """
    
    # Python code to execute inside Unreal
    code = f"""
import unreal

print("=" * 60)
print("Creating Level Sequence: {sequence_name}")
print("=" * 60)

# Delete all sequences starting with "TestSequence"
print("\\nCleaning up old test sequences...")
sequence_path = "/Game/Sequences"
if unreal.EditorAssetLibrary.does_directory_exist(sequence_path):
    assets = unreal.EditorAssetLibrary.list_assets(sequence_path, recursive=False)
    deleted_count = 0
    for asset_path in assets:
        asset_name = asset_path.split('/')[-1].split('.')[0]
        if asset_name.startswith("TestSequence"):
            print(f"  Deleting: {{asset_name}}")
            unreal.EditorAssetLibrary.delete_asset(asset_path)
            deleted_count += 1
    
    if deleted_count > 0:
        print(f"✓ Deleted {{deleted_count}} old test sequence(s)")
    else:
        print("  No old test sequences found")

# Close any currently open sequence
current_seq = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
if current_seq:
    print(f"Closing currently open sequence: {{current_seq.get_name()}}")
    unreal.LevelSequenceEditorBlueprintLibrary.close()

# Define sequence path
sequence_path = "/Game/Sequences"
sequence_full_path = f"{{sequence_path}}/{sequence_name}"

# Create Sequences directory if it doesn't exist
if not unreal.EditorAssetLibrary.does_directory_exist(sequence_path):
    print(f"Creating directory: {{sequence_path}}")
    unreal.EditorAssetLibrary.make_directory(sequence_path)
    print("✓ Directory created")

# Delete existing sequence if it exists
if unreal.EditorAssetLibrary.does_asset_exist(sequence_full_path):
    print(f"Deleting existing sequence: {{sequence_full_path}}")
    unreal.EditorAssetLibrary.delete_asset(sequence_full_path)
    print("✓ Old sequence deleted")

# Create new Level Sequence
print("Creating new Level Sequence...")
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
sequence = asset_tools.create_asset(
    "{sequence_name}",
    sequence_path,
    unreal.LevelSequence,
    unreal.LevelSequenceFactoryNew()
)

if not sequence:
    print("✗ Failed to create sequence")
else:
    print(f"✓ Sequence created: {{sequence.get_name()}}")
    
    # Set sequence properties
    unreal.MovieSceneSequenceExtensions.set_playback_end_seconds(sequence, {duration_seconds})
    unreal.MovieSceneSequenceExtensions.set_display_rate(sequence, unreal.FrameRate({fps}, 1))
    print(f"✓ Set duration: {duration_seconds} seconds at {fps}fps")
    
    # Save the sequence
    saved = unreal.EditorAssetLibrary.save_loaded_asset(sequence)
    if saved:
        print("✓ Sequence saved to disk")
    else:
        print("⚠ Warning: Failed to save sequence")
    
    # Open the sequence in Sequencer
    unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(sequence)
    print("✓ Sequence opened in Sequencer")
    
    print("=" * 60)
    print("✓ Sequence creation complete!")
    print(f"  Name: {{sequence.get_name()}}")
    print(f"  Path: {{sequence.get_path_name()}}")
    print("=" * 60)
"""
    
    # Connect to Unreal and execute
    unreal = UnrealRemote()
    
    if not unreal.is_connected():
        print("✗ Cannot connect to Unreal Engine!")
        print("Make sure Unreal is running and WebControl.StartServer has been executed.")
        return False
    
    print(f"Creating sequence '{sequence_name}' ({duration_seconds}s @ {fps}fps)...")
    success, result = unreal.execute_python(code)
    
    if success:
        print("\n✓ Sequence created successfully!")
        print("Check Unreal Engine's Sequencer window.")
        return True
    else:
        print(f"\n✗ Failed to create sequence: {result}")
        return False


def main():
    """Main entry point"""
    import sys
    
    # Get sequence name from command line or use default
    sequence_name = sys.argv[1] if len(sys.argv) > 1 else "MySequence"
    duration = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0
    fps = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    
    create_sequence(sequence_name, duration, fps)


if __name__ == "__main__":
    main()
