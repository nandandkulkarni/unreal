"""
Step 1: Run this in Unreal Python console (Ctrl+Shift+X) to create a test sequence
Then run check_open_existing_sequence.py to test if remote opening works
"""
import unreal

# Create a simple test sequence
print("Creating test sequence...")
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
factory = unreal.LevelSequenceFactoryNew()

sequence = asset_tools.create_asset(
    "TestSequence", 
    "/Game/Sequences", 
    unreal.LevelSequence, 
    factory
)

if sequence:
    sequence.set_display_rate(unreal.FrameRate(30, 1))
    sequence.set_playback_start(0)
    sequence.set_playback_end(300)
    print(f"✓ Created: {sequence.get_path_name()}")
    
    # Save it
    unreal.EditorAssetLibrary.save_loaded_asset(sequence)
    print("✓ Sequence saved")
    
    # Close any open sequences
    unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
    print("✓ Closed editor")
    print("\nNow run: python CinematicPipeline_Scripts/external_control/check_open_existing_sequence.py")
else:
    print("✗ Failed to create sequence")
