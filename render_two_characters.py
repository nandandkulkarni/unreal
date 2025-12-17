"""
Render Two Character Sequence to Video
Run this INSIDE UNREAL: Tools → Execute Python Script

Renders TwoCharacterSequence to Apple ProRes video file
Output: C:/U/CinematicPipeline/Saved/VideoCaptures
"""

import unreal

def render_two_character_sequence():
    """Render the two character sequence to video"""
    
    print("=" * 60)
    print("Rendering Two Character Sequence to Video")
    print("=" * 60)
    
    # Load the sequence
    sequence_path = "/Game/TwoCharacterSequence"
    print(f"\n1. Loading sequence: {sequence_path}")
    
    sequence_asset = unreal.load_asset(sequence_path)
    if not sequence_asset:
        print(f"   ✗ Could not load sequence: {sequence_path}")
        print("\n   Make sure you've created it first:")
        print("   Tools → Execute Python Script → create_two_characters.py")
        return
    
    print(f"   ✓ Loaded sequence")
    
    # Get Movie Pipeline subsystem
    print("\n2. Setting up Movie Pipeline...")
    subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
    queue = subsystem.get_queue()
    
    # Clear existing jobs
    queue.delete_all_jobs()
    
    # Create new render job
    job = queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
    job.sequence = unreal.SoftObjectPath(sequence_path)
    job.map = unreal.SoftObjectPath("/Game/Main")
    
    print("   ✓ Render job created")
    
    # Configure output settings
    print("\n3. Configuring output settings...")
    config = job.get_configuration()
    
    # Output settings
    output_setting = config.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
    output_setting.output_directory = unreal.DirectoryPath("C:/U/CinematicPipeline/Saved/VideoCaptures")
    output_setting.file_name_format = "TwoCharacters_{sequence_name}"
    output_setting.output_resolution = unreal.IntPoint(1920, 1080)
    output_setting.output_frame_rate = unreal.FrameRate(30, 1)
    
    # Apple ProRes codec
    video_setting = config.find_or_add_setting_by_class(unreal.MoviePipelineAppleProResOutput)
    
    print("   ✓ Settings configured:")
    print("     - Resolution: 1920x1080")
    print("     - Frame rate: 30fps")
    print("     - Format: Apple ProRes")
    
    # Start render
    print("\n4. Starting render...")
    print("   This will open a render preview window")
    print("   Please wait for render to complete...")
    
    subsystem.render_queue_with_executor(unreal.MoviePipelinePIEExecutor.static_class())
    
    print("\n" + "=" * 60)
    print("Render started!")
    print("=" * 60)
    print("\nOutput location:")
    print("  C:\\U\\CinematicPipeline\\Saved\\VideoCaptures")
    print("\nFile name:")
    print("  TwoCharacters_TwoCharacterSequence.mov")
    print("\nWait for render preview window to complete...")
    print("=" * 60)

if __name__ == "__main__":
    render_two_character_sequence()
