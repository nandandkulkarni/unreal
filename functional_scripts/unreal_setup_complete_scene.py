"""
Pure Unreal Python Script - Complete Scene Setup

This script runs INSIDE Unreal Engine's Python interpreter.
It creates a complete cinematic scene:
1. Deletes old Test* sequences, cameras, and mannequins
2. Creates a new sequence with timestamp
3. Creates a camera
4. Creates a mannequin
5. Adds both to the sequence

Usage: Run from PowerShell or press Ctrl+Enter in VS Code
"""
import unreal
from datetime import datetime

try:
    print("=" * 60)
    print("Complete Cinematic Scene Setup")
    print("=" * 60)
    
    # Get timestamp for unique naming
    timestamp = datetime.now().strftime("%y_%m_%d_%H_%M_%S")
    sequence_name = f"TestSequence_{timestamp}"
    camera_name = f"TestCamera_{timestamp}"
    mannequin_name = f"TestMannequin_{timestamp}"
    
    print(f"\nCreating scene with timestamp: {timestamp}")
    print(f"  Sequence: {sequence_name}")
    print(f"  Camera: {camera_name}")
    print(f"  Mannequin: {mannequin_name}")
    
    # ===== STEP 1: Delete old Test* assets =====
    print("\n" + "=" * 60)
    print("STEP 1: Cleaning up old Test* assets")
    print("=" * 60)
    
    # Delete old sequences
    print("\nDeleting old Test* sequences...")
    sequences_path = "/Game/Sequences"
    deleted_sequences = 0
    
    if unreal.EditorAssetLibrary.does_directory_exist(sequences_path):
        assets = unreal.EditorAssetLibrary.list_assets(sequences_path, recursive=False)
        for asset_path in assets:
            asset_name = asset_path.split('/')[-1].split('.')[0]
            if asset_name.startswith("Test"):
                unreal.EditorAssetLibrary.delete_asset(asset_path)
                print(f"  Deleted sequence: {asset_name}")
                deleted_sequences += 1
    
    if deleted_sequences > 0:
        print(f"✓ Deleted {deleted_sequences} old sequence(s)")
    else:
        print("  No old sequences found")
    
    # Delete old actors
    print("\nDeleting old Test* actors...")
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    all_actors = editor_actor_subsystem.get_all_level_actors()
    deleted_actors = 0
    
    for actor in all_actors:
        actor_label = actor.get_actor_label()
        if actor_label.startswith("TestCamera") or actor_label.startswith("TestMannequin"):
            unreal.EditorLevelLibrary.destroy_actor(actor)
            print(f"  Deleted actor: {actor_label}")
            deleted_actors += 1
    
    if deleted_actors > 0:
        print(f"✓ Deleted {deleted_actors} old actor(s)")
    else:
        print("  No old actors found")
    
    # ===== STEP 2: Create new sequence =====
    print("\n" + "=" * 60)
    print("STEP 2: Creating new sequence")
    print("=" * 60)
    
    sequence_path = f"/Game/Sequences/{sequence_name}"
    factory = unreal.LevelSequenceFactoryNew()
    sequence = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        sequence_name,
        "/Game/Sequences",
        unreal.LevelSequence,
        factory
    )
    
    if sequence:
        print(f"✓ Sequence created: {sequence_name}")
        
        # Set sequence properties
        fps = 30
        duration_seconds = 10
        duration_frames = int(fps * duration_seconds)
        
        # Set playback range
        sequence.set_playback_start(0)
        sequence.set_playback_end(duration_frames)
        sequence.set_display_rate(unreal.FrameRate(numerator=int(fps), denominator=1))
        
        print(f"  FPS: {fps}")
        print(f"  Duration: {duration_seconds}s ({duration_frames} frames)")
    else:
        print("✗ ERROR: Failed to create sequence")
        raise Exception("Sequence creation failed")
    
    # ===== STEP 3: Create camera =====
    print("\n" + "=" * 60)
    print("STEP 3: Creating camera")
    print("=" * 60)
    
    camera_location = unreal.Vector(0, -500, 200)
    camera_rotation = unreal.Rotator(0, 0, 0)
    
    camera = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.CineCameraActor,
        camera_location,
        camera_rotation
    )
    
    if camera:
        camera.set_actor_label(camera_name)
        
        # Set camera properties
        camera_component = camera.get_cine_camera_component()
        camera_component.set_editor_property("current_focal_length", 50.0)
        camera_component.set_editor_property("current_aperture", 2.8)
        
        print(f"✓ Camera created: {camera_name}")
        print(f"  Location: {camera_location}")
        print(f"  Focal Length: 50mm")
        print(f"  Aperture: f/2.8")
    else:
        print("✗ ERROR: Failed to create camera")
        raise Exception("Camera creation failed")
    
    # ===== STEP 4: Create mannequin =====
    print("\n" + "=" * 60)
    print("STEP 4: Creating mannequin")
    print("=" * 60)
    
    mannequin_location = unreal.Vector(0, 0, 88)
    mannequin_rotation = unreal.Rotator(0, 0, 0)
    
    # Get the Third Person Character blueprint
    mannequin_class = unreal.load_object(None, "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter.BP_ThirdPersonCharacter_C")
    
    if mannequin_class:
        mannequin = unreal.EditorLevelLibrary.spawn_actor_from_class(
            mannequin_class,
            mannequin_location,
            mannequin_rotation
        )
        
        if mannequin:
            mannequin.set_actor_label(mannequin_name)
            print(f"✓ Mannequin created: {mannequin_name}")
            print(f"  Location: {mannequin_location}")
        else:
            print("✗ ERROR: Failed to spawn mannequin")
            raise Exception("Mannequin spawn failed")
    else:
        print("✗ ERROR: Could not load BP_ThirdPersonCharacter")
        raise Exception("Mannequin class not found")
    
    # ===== STEP 5: Add camera to sequence =====
    print("\n" + "=" * 60)
    print("STEP 5: Adding camera to sequence")
    print("=" * 60)
    
    camera_binding = unreal.MovieSceneSequenceExtensions.add_possessable(sequence, camera)
    
    if camera_binding:
        print(f"✓ Camera added to sequence: {str(camera_binding.get_display_name())}")
        
        # Add camera cut track
        camera_cut_track = sequence.add_track(unreal.MovieSceneCameraCutTrack)
        camera_cut_section = camera_cut_track.add_section()
        unreal.MovieSceneSectionExtensions.set_range(camera_cut_section, 0, duration_frames)
        
        # Set camera binding ID - try both methods
        try:
            camera_binding_id = unreal.MovieSceneObjectBindingID()
            camera_binding_id.set_guid(camera_binding.get_id())
            camera_cut_section.set_camera_binding_id(camera_binding_id)
            print("✓ Camera cut track added")
        except Exception as e:
            print(f"  Trying alternative binding method...")
            try:
                camera_binding_id = camera_cut_section.get_editor_property('camera_binding_id')
                camera_binding_id.guid = camera_binding.get_id()
                camera_cut_section.set_editor_property('camera_binding_id', camera_binding_id)
                print("✓ Camera cut track added (using editor property)")
            except Exception as e2:
                print(f"⚠ Warning: Could not set camera binding: {e2}")
    else:
        print("⚠ Warning: Failed to add camera binding")
    
    # ===== STEP 6: Add mannequin to sequence =====
    print("\n" + "=" * 60)
    print("STEP 6: Adding mannequin to sequence")
    print("=" * 60)
    
    mannequin_binding = unreal.MovieSceneSequenceExtensions.add_possessable(sequence, mannequin)
    
    if mannequin_binding:
        print(f"✓ Mannequin added to sequence: {str(mannequin_binding.get_display_name())}")
        
        # Add transform track
        transform_track = unreal.MovieSceneBindingExtensions.add_track(
            mannequin_binding,
            unreal.MovieScene3DTransformTrack
        )
        
        if transform_track:
            section = unreal.MovieSceneTrackExtensions.add_section(transform_track)
            unreal.MovieSceneSectionExtensions.set_range(section, 0, duration_frames)
            print("✓ Transform track added")
        
        # Add skeletal animation track
        anim_track = unreal.MovieSceneBindingExtensions.add_track(
            mannequin_binding,
            unreal.MovieSceneSkeletalAnimationTrack
        )
        
        if anim_track:
            anim_section = unreal.MovieSceneTrackExtensions.add_section(anim_track)
            unreal.MovieSceneSectionExtensions.set_range(anim_section, 0, duration_frames)
            print("✓ Skeletal animation track added")
    else:
        print("⚠ Warning: Failed to add mannequin binding")
    
    # ===== STEP 7: Save and open sequence =====
    print("\n" + "=" * 60)
    print("STEP 7: Finalizing")
    print("=" * 60)
    
    # Save sequence
    saved = unreal.EditorAssetLibrary.save_loaded_asset(sequence)
    if saved:
        print("✓ Sequence saved")
    
    # Open in Sequencer
    unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(sequence)
    print("✓ Sequence opened in Sequencer")
    
    # ===== COMPLETE =====
    print("\n" + "=" * 60)
    print("✓ SCENE SETUP COMPLETE!")
    print("=" * 60)
    print(f"Sequence: {sequence_name}")
    print(f"Camera: {camera_name}")
    print(f"Mannequin: {mannequin_name}")
    print(f"Duration: {duration_seconds}s @ {fps}fps")
    print("=" * 60)
    print("\nCheck Sequencer to see your complete scene!")
    
except Exception as e:
    print("\n" + "=" * 60)
    print("✗ FATAL ERROR")
    print("=" * 60)
    print("Error type: " + type(e).__name__)
    print("Error message: " + str(e))
    
    import traceback
    print("\nFull traceback:")
    for line in traceback.format_exc().split('\n'):
        if line:
            print("  " + line)
    print("=" * 60)

print("\nDone!")
