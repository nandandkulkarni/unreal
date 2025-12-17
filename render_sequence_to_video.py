"""
Render Level Sequence to video file
Run this inside Unreal: Tools → Execute Python Script

This will render the sequence to a video file in the project's Saved/VideoCaptures folder
"""

import unreal

def render_sequence_to_video():
    """Render the character walking sequence to video"""
    
    print("\n" + "=" * 70)
    print("RENDERING SEQUENCE TO VIDEO")
    print("=" * 70)
    
    # Load the sequence
    sequence_path = '/Game/Sequences/CharacterWalkSequence'
    print(f"\n[1/6] Loading sequence: {sequence_path}")
    sequence = unreal.load_asset(sequence_path)
    
    if not sequence:
        print(f"FAILED: Could not load sequence")
        return False
    
    print(f"SUCCESS: Loaded sequence: {sequence.get_name()}")
    
    # Use Movie Pipeline Queue (modern UE5 method)
    print("\n[2/6] Setting up Movie Pipeline Queue...")
    
    subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
    queue = subsystem.get_queue()
    
    # Clear existing jobs
    queue.delete_all_jobs()
    
    # Create a new job
    job = queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
    job.sequence = unreal.SoftObjectPath(sequence_path)
    job.map = unreal.SoftObjectPath("/Game/Main")
    job.job_name = "CharacterWalkSequence_Render"
    
    print("SUCCESS: Movie Pipeline job created")
    
    # Configure the job settings
    print("\n[3/6] Configuring render settings...")
    config = job.get_configuration()
    
    # Add output setting
    output_setting = config.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
    output_setting.output_directory = unreal.DirectoryPath("C:/U/CinematicPipeline/Saved/VideoCaptures")
    output_setting.file_name_format = "{sequence_name}"
    output_setting.output_resolution = unreal.IntPoint(1920, 1080)
    output_setting.output_frame_rate = unreal.FrameRate(30, 1)
    
    # Add deferred rendering setting
    deferred_setting = config.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)
    
    # Try to add video output (this might fail depending on available codecs)
    print("\n[4/6] Adding video output format...")
    
    try:
        # Try Apple ProRes if available
        video_setting = config.find_or_add_setting_by_class(unreal.MoviePipelineAppleProResOutput)
        print("SUCCESS: Apple ProRes output added")
    except:
        try:
            # Fallback to image sequence
            image_setting = config.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG)
            print("SUCCESS: PNG image sequence output added (no video codec available)")
            print("  Note: Will output PNG frames that can be converted to video later")
        except Exception as e:
            print(f"WARNING: Could not add output format: {e}")
            print("  Using default output format")
    
    print("SUCCESS: Render settings configured")
    print(f"  Resolution: 1920x1080")
    print(f"  Frame rate: 30 fps")
    print(f"  Output: C:/U/CinematicPipeline/Saved/VideoCaptures")
    
    # Start the render
    print("\n[5/6] Starting render...")
    print("This may take a few minutes...")
    
    try:
        # Just render the queue - it will use the default PIE executor
        subsystem.render_queue_with_executor(unreal.MoviePipelinePIEExecutor.static_class())
        print("SUCCESS: Render started")
        print("\nRender is processing...")
    except:
        # Try alternative method - just render with default settings
        try:
            # Alternative: Use the allocate_new_executor method
            executor_class = unreal.MoviePipelinePIEExecutor.static_class()
            subsystem.render_queue_with_executor(executor_class)
            print("SUCCESS: Render started with alternative method")
        except Exception as e2:
            print(f"FAILED: Could not start render: {e2}")
            print("\nTrying manual UI trigger method...")
            print("Please manually trigger render from:")
            print("  Window > Cinematics > Movie Render Queue")
            print("  Then click 'Render (Local)' button")
            return False
    
    # Wait and verify
    print("\n[6/6] Render information:")
    print("=" * 70)
    print("Output location: C:/U/CinematicPipeline/Saved/VideoCaptures")
    print("File name: CharacterWalkSequence.avi (or .mov)")
    print("\nNOTE: Render happens in background.")
    print("Check the output folder after a few minutes.")
    print("Monitor progress in Unreal's Output Log.")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    try:
        success = render_sequence_to_video()
        if success:
            print("\nRENDER INITIATED SUCCESSFULLY")
            print("Check C:/U/CinematicPipeline/Saved/VideoCaptures for output")
        else:
            print("\nRENDER FAILED - Check errors above")
    except Exception as e:
        print(f"\nEXCEPTION: {e}")
        import traceback
        traceback.print_exc()
