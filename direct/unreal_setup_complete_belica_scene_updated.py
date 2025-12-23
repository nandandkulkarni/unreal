"""
Pure Unreal Python Script - Complete Scene Setup

This script runs INSIDE Unreal Engine's Python interpreter.
It creates a complete cinematic scene:
1. Deletes old Test* sequences, cameras, and mannequins
2. Creates a new sequence with timestamp
3. Creates a camera
4. Creates a mannequin
5. Adds both to the sequence

Usage: Open this file in VS Code and press Ctrl+Enter to run
"""
import unreal
from datetime import datetime
import os

# Setup logging
log_dir = r"C:\UnrealProjects\Coding\unreal\direct"
log_file = os.path.join(log_dir, "scene_setup.log")


def log(message):
    """Print and write to log file"""
    print(message)
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"Warning: Could not write to log: {e}")


try:
    log("=" * 60)
    log("Complete Cinematic Scene Setup")
    log("=" * 60)

    # Get timestamp and find next sequence number
    timestamp = datetime.now().strftime("%y_%m_%d_%H_%M_%S")

    # Find existing Test* sequences to determine next number
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

    # Format number with leading zeros
    sequence_name = f"TestSequence_{timestamp}_{next_num:03d}"
    camera_name = f"TestCamera_{timestamp}_{next_num:03d}"
    mannequin_name = f"TestMannequin_{timestamp}_{next_num:03d}"

    log(f"\nCreating scene #{next_num}")
    log(f"  Sequence: {sequence_name}")
    log(f"  Camera: {camera_name}")
    log(f"  Mannequin: {mannequin_name}")

    # ===== STEP 1: Delete old Test* assets =====
    log("\n" + "=" * 60)
    log("STEP 1: Cleaning up old Test* assets")
    log("=" * 60)

    # Close any currently open sequences first
    log("\nClosing any open sequences...")
    try:
        current_seq = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
        if current_seq:
            log(f"  Closing: {current_seq.get_name()}")
            unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
            log("✓ Closed open sequence")
        else:
            log("  No sequence currently open")
    except Exception as e:
        log(f"  Could not close sequence: {e}")

    # Delete old sequences
    log("\nDeleting old Test* sequences...")
    sequences_path = "/Game/Sequences"
    deleted_sequences = 0

    if unreal.EditorAssetLibrary.does_directory_exist(sequences_path):
        assets = unreal.EditorAssetLibrary.list_assets(sequences_path, recursive=False)
        for asset_path in assets:
            asset_name = asset_path.split('/')[-1].split('.')[0]
            if asset_name.startswith("Test"):
                try:
                    unreal.EditorAssetLibrary.delete_asset(asset_path)
                    log(f"  Deleted sequence: {asset_name}")
                    deleted_sequences += 1
                except Exception as e:
                    log(f"  Failed to delete {asset_name}: {e}")

    if deleted_sequences > 0:
        log(f"✓ Deleted {deleted_sequences} old sequence(s)")
    else:
        log("  No old sequences found")

    # Delete old actors
    log("\nDeleting old Test* actors, HUD text actors, axis segments, and debug cubes...")
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    all_actors = editor_actor_subsystem.get_all_level_actors()
    deleted_actors = 0

    for actor in all_actors:
        actor_label = actor.get_actor_label()
        # Delete Test* actors, TextRenderActor, axis segments, and debug cubes
        if (actor_label.startswith("TestCamera") or
            actor_label.startswith("TestMannequin") or
            actor_label.startswith("Axis_") or
            actor_label.startswith("Origin_") or
            actor_label.startswith("Test_") or
                actor.get_class().get_name() == "TextRenderActor"):
            unreal.EditorLevelLibrary.destroy_actor(actor)
            log(f"  Deleted actor: {actor_label}")
            deleted_actors += 1

    if deleted_actors > 0:
        log(f"✓ Deleted {deleted_actors} old actor(s)")
    else:
        log("  No old actors found")

    # ===== STEP 2: Create new sequence =====
    log("\n" + "=" * 60)
    log("STEP 2: Creating new sequence")
    log("=" * 60)

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
        fps = 30
        duration_seconds = 60
        duration_frames = int(fps * duration_seconds)

        # Camera cut duration control: use seconds or frames
        # True => compute from seconds; False => use explicit frames value
        camera_cut_use_seconds = True  # Frames mode (30 fps, 60s => 1800 frames)
        camera_cut_duration_seconds = 60
        camera_cut_duration_frames = int(fps * camera_cut_duration_seconds)

        # Set playback range
        sequence.set_playback_start(0)
        sequence.set_playback_end(duration_frames)
        sequence.set_display_rate(unreal.FrameRate(numerator=int(fps), denominator=1))

        log(f"  FPS: {fps}")
        log(f"  Duration: {duration_seconds}s ({duration_frames} frames)")
    else:
        log("✗ ERROR: Failed to create sequence")
        raise Exception("Sequence creation failed")

    # ===== STEP 3: Create camera =====
    log("\n" + "=" * 60)
    log("STEP 3: Creating camera")
    log("=" * 60)

    camera_location = unreal.Vector(0, 0, 300)
    # Face forward (toward +Y) at mannequin - yaw=90
    camera_rotation = unreal.Rotator(pitch=0.0, yaw=90.0, roll=0.0)

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

        log(f"✓ Camera created: {camera_name}")
        log(f"  Location: {camera_location}")
        log(f"  Rotation: {camera_rotation}")
        log("  Focal Length: 50mm")
        log("  Aperture: f/2.8")
    else:
        log("✗ ERROR: Failed to create camera")
        raise Exception("Camera creation failed")

    # ===== STEP 4: Create mannequin =====
    log("\n" + "=" * 60)
    log("STEP 4: Creating mannequin")
    log("=" * 60)

    mannequin_location = unreal.Vector(0, 0, 300)  # Z=300
    
    # Load the desired Belica skeletal mesh
    skeletal_mesh = unreal.load_object(None, "/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica")
    
    # Character-specific rotation to align visual facing with desired movement direction
    # Belica's mesh visual is 90° off - rotate -90° to make her face Red (+X)
    mannequin_rotation = unreal.Rotator(pitch=0.0, yaw=-90.0, roll=0.0)  # Align visual with Red

    if not skeletal_mesh:
        # Fallback to Quinn if Belica is missing
        skeletal_mesh = unreal.load_object(None, "/Game/Characters/Mannequins/Meshes/SKM_Quinn_Simple.SKM_Quinn_Simple")

    if not skeletal_mesh:
        # Secondary fallback
        skeletal_mesh = unreal.load_object(
            None, "/Game/ThirdPerson/Characters/Mannequins/Meshes/SKM_Quinn_Simple.SKM_Quinn_Simple")

    if skeletal_mesh:
        # Spawn a SkeletalMeshActor
        mannequin = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.SkeletalMeshActor,
            mannequin_location,
            mannequin_rotation
        )

        if mannequin:
            mannequin.set_actor_label(mannequin_name)

            # Set the skeletal mesh on the component
            skel_comp = mannequin.skeletal_mesh_component
            skel_comp.set_skeletal_mesh(skeletal_mesh)

            log(f"✓ Mannequin created: {mannequin_name}")
            log(f"  Location: {mannequin_location}")
            log(f"  Mesh: {skeletal_mesh.get_name()}")
            log(f"  Rotation: Pitch={mannequin_rotation.pitch}, Yaw={mannequin_rotation.yaw}, Roll={mannequin_rotation.roll}")
            
            # Debug: Check mannequin's forward direction
            forward_vec = mannequin.get_actor_forward_vector()
            log(f"  Forward Vector: X={forward_vec.x:.3f}, Y={forward_vec.y:.3f}, Z={forward_vec.z:.3f}")

            # --- HUD showing Belica X/Y/Z (approx 1x1 inch via 2.54 world size) ---
            # Position HUD in front of camera (Y-forward is camera's forward direction)
            hud_location = unreal.Vector(0, 100, 50)  # 100cm forward, 50cm up from camera
            hud_rotation = unreal.Rotator(0, 90, 0)  # Face back toward camera (yaw=90)

            hud_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.TextRenderActor,
                camera.get_actor_location(),
                hud_rotation
            )

            if hud_actor:
                # Attach HUD to camera with relative transform
                hud_actor.attach_to_actor(
                    camera,
                    "",  # No socket name
                    unreal.AttachmentRule.KEEP_RELATIVE,
                    unreal.AttachmentRule.KEEP_RELATIVE,
                    unreal.AttachmentRule.KEEP_RELATIVE,
                    False
                )
                # Set relative location after attachment (location, sweep, teleport)
                hud_actor.set_actor_relative_location(hud_location, False, False)

                text_comp = hud_actor.get_component_by_class(unreal.TextRenderComponent)
                if text_comp:
                    text_comp.set_world_size(10.0)  # Larger size for visibility
                    text_comp.set_text_render_color(unreal.Color(255, 255, 0, 255))  # Yellow (RGBA 0-255)
                    text_comp.set_text(r"HUD initializing...")
                    log("✓ HUD text actor created and attached to camera")

                    def _update_hud(_delta):
                        loc = mannequin.get_actor_location()
                        text_comp.set_text(f"Belica XYZ\nX: {loc.x:.1f}\nY: {loc.y:.1f}\nZ: {loc.z:.1f}")

                    try:
                        unreal.register_slate_post_tick_callback(_update_hud)
                        log("✓ HUD tick registered to update Belica position")
                    except Exception as e:
                        log(f"⚠ Warning: HUD tick registration failed: {e}")
                else:
                    log("⚠ Warning: HUD text component missing")
            else:
                log("⚠ Warning: HUD actor failed to spawn")

            # DISABLED: Create a colored plus sign at the world origin using thin static mesh cubes
            if False:  # Disabled to show only one cube
                cube_mesh = unreal.load_object(None, "/Engine/BasicShapes/Cube.Cube")
                # Use the basic shape material that comes with the cube
                base_mat = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/BasicShapeMaterial")

                length_cm = 200.0   # segment length in cm for visibility
                width_cm = 2.0      # segment width in cm
                thickness_cm = 0.1  # 1 mm height (0.1 cm)

                # Helper to spawn a thin box segment with color
                def spawn_segment(name, loc, scale_vec, color_lin):
                    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
                        unreal.StaticMeshActor,
                        loc,
                        unreal.Rotator(0, 0, 0)
                    )
                    if not actor:
                        log(f"⚠ Warning: Failed to spawn segment: {name}")
                        return
                    actor.set_actor_label(name)
                    smc = actor.static_mesh_component
                    smc.set_static_mesh(cube_mesh)
                    # Ensure visibility in editor and game
                    smc.set_visibility(True, True)
                    smc.set_hidden_in_game(False)
                    actor.set_actor_hidden_in_game(False)
                    actor.set_is_temporarily_hidden_in_editor(False)
                    try:
                        smc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
                    except Exception:
                        pass
                    actor.set_actor_scale3d(scale_vec)

                    # Try to assign a colored material
                    if base_mat:
                        try:
                            mid = unreal.KismetMaterialLibrary.create_dynamic_material_instance(actor, base_mat)
                            # Attempt common parameter names for color
                            ok = False
                            for param in ["Color", "BaseColor", "TintColor"]:
                                try:
                                    mid.set_vector_parameter_value(param, color_lin)
                                    ok = True
                                    break
                                except Exception:
                                    pass
                            smc.set_material(0, mid)
                            if ok:
                                log(f"✓ Segment {name} material colored successfully")
                            else:
                                log(f"⚠ Segment {name} material applied without color parameter support")
                        except Exception as e:
                            log(f"⚠ Warning: Could not create dynamic material for {name}: {e}")
                            try:
                                smc.set_material(0, base_mat)
                            except Exception:
                                pass

                # Compute per-axis segments (centered at origin, extending in one direction)
                # Note: Cube mesh is 100cm, scale values are relative to that.
                # Place at z = thickness/2 so it rests on ground (z=0)
                z_loc = thickness_cm / 2.0

                # +X (red)
                spawn_segment(
                    "Axis_PosX",
                    unreal.Vector(length_cm / 2.0, 0.0, z_loc),
                    unreal.Vector(length_cm / 100.0, width_cm / 100.0, thickness_cm / 100.0),
                    unreal.LinearColor(1.0, 0.0, 0.0, 1.0)
                )

                # -X (yellow)
                spawn_segment(
                    "Axis_NegX",
                    unreal.Vector(-length_cm / 2.0, 0.0, z_loc),
                    unreal.Vector(length_cm / 100.0, width_cm / 100.0, thickness_cm / 100.0),
                    unreal.LinearColor(1.0, 1.0, 0.0, 1.0)
                )

                # +Y (blue) — scale along Y
                spawn_segment(
                    "Axis_PosY",
                    unreal.Vector(0.0, length_cm / 2.0, z_loc),
                    unreal.Vector(width_cm / 100.0, length_cm / 100.0, thickness_cm / 100.0),
                    unreal.LinearColor(0.0, 0.0, 1.0, 1.0)
                )

                # -Y (purple) — scale along Y
                spawn_segment(
                    "Axis_NegY",
                    unreal.Vector(0.0, -length_cm / 2.0, z_loc),
                    unreal.Vector(width_cm / 100.0, length_cm / 100.0, thickness_cm / 100.0),
                    unreal.LinearColor(1.0, 0.0, 1.0, 1.0)
                )

                log("✓ Colored plus sign created at origin (1mm thickness)")

            # DISABLED: Add a clearly visible flattened cube at origin for easier focus
            if False:  # Disabled to show only one cube
                cube_mesh = unreal.load_object(None, "/Engine/BasicShapes/Cube.Cube")
                base_mat = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/BasicShapeMaterial")
                if cube_mesh:
                    focus_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
                        unreal.StaticMeshActor,
                        unreal.Vector(0.0, 0.0, 0.5),  # slightly above ground
                        unreal.Rotator(0, 0, 0)
                    )
                    if focus_actor:
                        focus_actor.set_actor_label("Origin_FlatCube")
                        smc = focus_actor.static_mesh_component
                        smc.set_static_mesh(cube_mesh)
                        # Ensure visibility
                        smc.set_visibility(True, True)
                        smc.set_hidden_in_game(False)
                        focus_actor.set_actor_hidden_in_game(False)
                        focus_actor.set_is_temporarily_hidden_in_editor(False)
                        try:
                            smc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
                        except Exception:
                            pass
                        # 50cm x 50cm x 1cm (flattened)
                        focus_actor.set_actor_scale3d(unreal.Vector(0.5, 0.5, 0.01))
                        if base_mat:
                            try:
                                mid = unreal.KismetMaterialLibrary.create_dynamic_material_instance(
                                    focus_actor, base_mat)
                                mid.set_vector_parameter_value(
                                    "Color", unreal.LinearColor(
                                        1.0, 0.5, 0.0, 1.0))  # orange
                                smc.set_material(0, mid)
                                log("✓ Origin flat cube spawned and colored (orange)")
                            except Exception as e:
                                smc.set_material(0, base_mat)
                                log(f"⚠ Origin flat cube material applied without color param: {e}")
                        else:
                            log("⚠ Origin flat cube: base material not found; using default")
                    else:
                        log("⚠ Warning: Failed to spawn origin flat cube")
                else:
                    log("⚠ Warning: Basic cube mesh not found; cannot spawn focus cube")

            # TEST: Spawn a big blue cube in the center for visibility - DISABLED
            # try:
            #     test_cube_mesh = unreal.load_object(None, "/Engine/BasicShapes/Cube.Cube")
            #     test_base_mat = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/BasicShapeMaterial")
            #     if test_cube_mesh:
            #         # Scale 2.0 => 200cm cube; place center at z=100 so it sits on ground
            #         test_cube = unreal.EditorLevelLibrary.spawn_actor_from_class(
            #             unreal.StaticMeshActor,
            #             unreal.Vector(0.0, 0.0, 100.0),
            #             unreal.Rotator(0, 0, 0)
            #         )
            #         if test_cube:
            #             test_cube.set_actor_label("Test_BigBlueCube")
            #             smc = test_cube.static_mesh_component
            #             smc.set_static_mesh(test_cube_mesh)
            #             # Ensure visibility
            #             smc.set_visibility(True, True)
            #             smc.set_hidden_in_game(False)
            #             test_cube.set_actor_hidden_in_game(False)
            #             test_cube.set_is_temporarily_hidden_in_editor(False)
            #             try:
            #                 smc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
            #             except Exception:
            #                 pass
            #             test_cube.set_actor_scale3d(unreal.Vector(2.0, 2.0, 2.0))
            #             
            #             # Use custom cube color material
            #             cube_color_mat = unreal.EditorAssetLibrary.load_asset("/Game/M_NK_Cube_Color")
            #             if cube_color_mat:
            #                 try:
            #                     mid = unreal.KismetMaterialLibrary.create_dynamic_material_instance(
            #                         test_cube, cube_color_mat)
            #                     mid.set_vector_parameter_value("Color", unreal.LinearColor(0.0, 0.0, 1.0, 1.0))
            #                     smc.set_material(0, mid)
            #                     log("✓ Test big blue cube spawned with M_NK_Cube_Color material")
            #                 except Exception as e:
            #                     log(f"⚠ Test cube M_NK_Cube_Color failed: {e}")
            #                     smc.set_material(0, cube_color_mat)
            #             else:
            #                 log("⚠ Test cube: M_NK_Cube_Color not found; using default material")
            #         else:
            #             log("⚠ Warning: Failed to spawn test big blue cube")
            #     else:
            #         log("⚠ Warning: Basic cube mesh not found; cannot spawn test cube")
            # except Exception as e:
            #     log(f"⚠ Warning: Could not add test big blue cube: {e}")
            
            # Draw a plus sign at origin using four thin cubes (1mm thick, 1m wide, 10m long each side)
            try:
                cube_mesh = unreal.load_object(None, "/Engine/BasicShapes/Cube.Cube")
                
                if cube_mesh:
                    # Each side is 10m long, offset by 0.5m from origin to avoid overlap
                    # Default cube is 100cm, so scale: (100, 10, 0.01) for 10000cm x 1000cm x 1cm
                    
                    # +X axis (Red) - extends from 0 to 10m in X
                    plus_x = unreal.EditorLevelLibrary.spawn_actor_from_class(
                        unreal.StaticMeshActor,
                        unreal.Vector(500.0, 0.0, 0.5),  # Center at +5m X
                        unreal.Rotator(0, 0, 0)
                    )
                    if plus_x:
                        plus_x.set_actor_label("Origin_Plus_PosX_Red")
                        smc = plus_x.static_mesh_component
                        smc.set_static_mesh(cube_mesh)
                        smc.set_visibility(True, True)
                        smc.set_hidden_in_game(False)
                        plus_x.set_actor_hidden_in_game(False)
                        plus_x.set_is_temporarily_hidden_in_editor(False)
                        try:
                            smc.set_editor_property("mobility", unreal.ComponentMobility.STATIONARY)
                        except Exception:
                            pass
                        plus_x.set_actor_scale3d(unreal.Vector(9.5, .25, 0.01))
                        
                        mat = unreal.EditorAssetLibrary.load_asset("/Game/MyMaterial/MyRed")
                        if mat:
                            smc.set_material(0, mat)
                            log("✓ +X axis (Red, 10m)")
                    
                    # -X axis (Yellow) - extends from 0 to -10m in X
                    minus_x = unreal.EditorLevelLibrary.spawn_actor_from_class(
                        unreal.StaticMeshActor,
                        unreal.Vector(-500.0, 0.0, 0.5),  # Center at -5m X
                        unreal.Rotator(0, 0, 0)
                    )
                    if minus_x:
                        minus_x.set_actor_label("Origin_Plus_NegX_Yellow")
                        smc = minus_x.static_mesh_component
                        smc.set_static_mesh(cube_mesh)
                        smc.set_visibility(True, True)
                        smc.set_hidden_in_game(False)
                        minus_x.set_actor_hidden_in_game(False)
                        minus_x.set_is_temporarily_hidden_in_editor(False)
                        try:
                            smc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
                        except Exception:
                            pass
                        minus_x.set_actor_scale3d(unreal.Vector(9.5, 1.0, 0.01))
                        
                        mat = unreal.EditorAssetLibrary.load_asset("/Game/MyMaterial/MyYellow")
                        if mat:
                            smc.set_material(0, mat)
                            log("✓ -X axis (Yellow, 10m)")
                    
                    # +Y axis (Green) - extends from 0 to 10m in Y
                    plus_y = unreal.EditorLevelLibrary.spawn_actor_from_class(
                        unreal.StaticMeshActor,
                        unreal.Vector(0.0, 500.0, 0.5),  # Center at +5m Y
                        unreal.Rotator(0, 0, 0)
                    )
                    if plus_y:
                        plus_y.set_actor_label("Origin_Plus_PosY_Green")
                        smc = plus_y.static_mesh_component
                        smc.set_static_mesh(cube_mesh)
                        smc.set_visibility(True, True)
                        smc.set_hidden_in_game(False)
                        plus_y.set_actor_hidden_in_game(False)
                        plus_y.set_is_temporarily_hidden_in_editor(False)
                        try:
                            smc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
                        except Exception:
                            pass
                        plus_y.set_actor_scale3d(unreal.Vector(1.0, 9.5, 0.01))
                        
                        mat = unreal.EditorAssetLibrary.load_asset("/Game/MyMaterial/MyGreen")
                        if mat:
                            smc.set_material(0, mat)
                            log("✓ +Y axis (Green, 10m)")
                    
                    # -Y axis (Purple) - extends from 0 to -10m in Y
                    minus_y = unreal.EditorLevelLibrary.spawn_actor_from_class(
                        unreal.StaticMeshActor,
                        unreal.Vector(0.0, -500.0, 0.5),  # Center at -5m Y
                        unreal.Rotator(0, 0, 0)
                    )
                    if minus_y:
                        minus_y.set_actor_label("Origin_Plus_NegY_Blue")
                        smc = minus_y.static_mesh_component
                        smc.set_static_mesh(cube_mesh)
                        smc.set_visibility(True, True)
                        smc.set_hidden_in_game(False)
                        minus_y.set_actor_hidden_in_game(False)
                        minus_y.set_is_temporarily_hidden_in_editor(False)
                        try:
                            smc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
                        except Exception:
                            pass
                        minus_y.set_actor_scale3d(unreal.Vector(1.0, 9.5, 0.01))
                        
                        mat = unreal.EditorAssetLibrary.load_asset("/Game/MyMaterial/MyBlue")
                        if mat:
                            smc.set_material(0, mat)
                            log("✓ -Y axis (Purple/Blue, 10m)")
                else:
                    log("⚠ Warning: Could not load cube mesh for plus sign")
            except Exception as e:
                log(f"⚠ Warning: Could not create plus sign: {e}")

            # Position camera behind mannequin using forward vector
            try:
                actor_loc = mannequin.get_actor_location()
                forward = mannequin.get_actor_forward_vector()
                up = mannequin.get_actor_up_vector()

                follow_distance = 300.0  # cm behind
                follow_height = 50.0     # cm up

                cam_loc = unreal.Vector(
                    actor_loc.x - forward.x * follow_distance + up.x * follow_height,
                    actor_loc.y - forward.y * follow_distance + up.y * follow_height,
                    actor_loc.z - forward.z * follow_distance + up.z * follow_height
                )

                cam_rot = unreal.MathLibrary.find_look_at_rotation(cam_loc, actor_loc)

                camera.set_actor_location(cam_loc, False, False)
                camera.set_actor_rotation(cam_rot, False)
                log("✓ Camera positioned behind mannequin and aimed at it")

                # Verify camera coordinates match expected
                actual_loc = camera.get_actor_location()
                delta_cm = unreal.MathLibrary.vector_distance(cam_loc, actual_loc)
                if delta_cm <= 0.5:
                    expected = f"{cam_loc.x:.1f}, {cam_loc.y:.1f}, {cam_loc.z:.1f}"
                    actual = f"{actual_loc.x:.1f}, {actual_loc.y:.1f}, {actual_loc.z:.1f}"
                    log(f"✓ Camera position verified (≤0.5cm): expected=({expected}), actual=({actual})")
                else:
                    expected = f"{cam_loc.x:.1f}, {cam_loc.y:.1f}, {cam_loc.z:.1f}"
                    actual = f"{actual_loc.x:.1f}, {actual_loc.y:.1f}, {actual_loc.z:.1f}"
                    log(f"⚠ Camera position mismatch by {delta_cm:.2f}cm")
                    log(f"   expected=({expected})")
                    log(f"   actual=({actual})")

                # DISABLED: Camera-attached cube removed per user request
            except Exception as e:
                log(f"⚠ Warning: Could not position camera behind mannequin: {e}")
        else:
            log("✗ ERROR: Failed to spawn mannequin")
            raise Exception("Mannequin spawn failed")
    else:
        log("✗ ERROR: Could not load skeletal mesh")
        raise Exception("Skeletal mesh not found")

    # ===== STEP 5: Add camera to sequence =====
    log("\n" + "=" * 60)
    log("STEP 5: Adding camera to sequence")
    log("=" * 60)

    camera_binding = unreal.MovieSceneSequenceExtensions.add_possessable(sequence, camera)

    if camera_binding:
        log(f"✓ Camera added to sequence: {str(camera_binding.get_display_name())}")
        log("  Camera will stay static at spawn position")

        # Add camera cut track
        camera_cut_track = sequence.add_track(unreal.MovieSceneCameraCutTrack)
        camera_cut_section = camera_cut_track.add_section()
        # Determine camera cut end frame based on flag
        if camera_cut_use_seconds:
            camera_cut_end_frame = int(fps * camera_cut_duration_seconds)
            log(f"  Camera cut duration: {camera_cut_duration_seconds}s ({camera_cut_end_frame} frames) [seconds mode]")
        else:
            camera_cut_end_frame = camera_cut_duration_frames
            log(f"  Camera cut duration: {camera_cut_end_frame} frames [frames mode]")
        camera_cut_section.set_range(0, camera_cut_end_frame)

        # Set camera binding - using MovieSceneObjectBindingID with guid as editor property
        try:
            binding_id = unreal.MovieSceneObjectBindingID()
            binding_id.set_editor_property('guid', camera_binding.get_id())
            camera_cut_section.set_camera_binding_id(binding_id)
            log("✓ Camera cut track added with binding")
        except Exception as e:
            log(f"⚠ Warning: Could not set camera binding: {e}")

        # Store camera binding for look at track setup after mannequin is added
        global camera_binding_for_lookat
        camera_binding_for_lookat = camera_binding
    else:
        log("⚠ Warning: Failed to add camera binding")

    # ===== STEP 6: Add mannequin to sequence =====
    log("\n" + "=" * 60)
    log("STEP 6: Adding mannequin to sequence")
    log("=" * 60)

    mannequin_binding = unreal.MovieSceneSequenceExtensions.add_possessable(sequence, mannequin)

    if mannequin_binding:
        log(f"✓ Mannequin added to sequence: {str(mannequin_binding.get_display_name())}")

        # Add transform track
        transform_track = unreal.MovieSceneBindingExtensions.add_track(
            mannequin_binding,
            unreal.MovieScene3DTransformTrack
        )

        if transform_track:
            section = unreal.MovieSceneTrackExtensions.add_section(transform_track)
            unreal.MovieSceneSectionExtensions.set_range(section, 0, duration_frames)
            log("✓ Transform track added")

        # Add skeletal animation track
        anim_track = unreal.MovieSceneBindingExtensions.add_track(
            mannequin_binding,
            unreal.MovieSceneSkeletalAnimationTrack
        )

        if anim_track:
            anim_section = unreal.MovieSceneTrackExtensions.add_section(anim_track)
            unreal.MovieSceneSectionExtensions.set_range(anim_section, 0, duration_frames)
            log("✓ Skeletal animation track added")

        # Add movement keyframes
        log("\nAdding movement keyframes...")
        transform_sections = unreal.MovieSceneTrackExtensions.get_sections(transform_track)
        if transform_sections:
            transform_section = transform_sections[0]

            # Get the transform channels
            channels = transform_section.get_all_channels()
            location_channels = channels[0:3]  # X, Y, Z channels
            rotation_channels = channels[3:6]  # Rotation X (Roll), Y (Pitch), Z (Yaw) channels

            # Use fixed world-space movement vectors (independent of actor rotation)
            # This allows us to rotate the character visually without changing movement direction
            world_x = unreal.Vector(1.0, 0.0, 0.0)  # Red (+X)
            world_y = unreal.Vector(0.0, 1.0, 0.0)  # Green (+Y)
            start = mannequin_location

            # Choose movement direction: 'x' for Red or 'y' for Green
            movement_direction = 'x'  # change to 'y' for Green direction
            move_vec = world_x if movement_direction == 'x' else world_y

            # Distances along chosen direction at each keyframe (cm)
            # Spread keys over 0..300 frames (adjust if using 60s timeline)
            keys = [
                (0, 0.0),
                (100, 166.0),
                (200, 333.0),
                (300, 500.0),
            ]

            distance_scale = 3.0

            for frame, dist in keys:
                dist_scaled = dist * distance_scale
                pos_x = start.x + move_vec.x * dist_scaled
                pos_y = start.y + move_vec.y * dist_scaled
                pos_z = start.z  # grounded
                location_channels[0].add_key(unreal.FrameNumber(frame), float(pos_x))
                location_channels[1].add_key(unreal.FrameNumber(frame), float(pos_y))
                location_channels[2].add_key(unreal.FrameNumber(frame), float(pos_z))
                
                # Set rotation keyframes to maintain spawn rotation
                rotation_channels[0].add_key(unreal.FrameNumber(frame), float(mannequin_rotation.roll))
                rotation_channels[1].add_key(unreal.FrameNumber(frame), float(mannequin_rotation.pitch))
                rotation_channels[2].add_key(unreal.FrameNumber(frame), float(mannequin_rotation.yaw))

            log(f"✓ Movement keyframes added: {movement_direction} direction, Z grounded, distance x{distance_scale}")

            # Resize and align the origin flat cube to match max movement length
            try:
                max_dist_cm = max([d for (_, d) in keys]) * distance_scale
                editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
                focus_actor = None
                for actor in editor_actor_subsystem.get_all_level_actors():
                    if actor.get_actor_label() == "Origin_FlatCube":
                        focus_actor = actor
                        break
                if focus_actor:
                    width_cm = 5.0
                    thickness_cm = 0.1  # 1mm
                    # Align cube along movement direction in XY plane
                    origin = unreal.Vector(0.0, 0.0, thickness_cm / 2.0)
                    target = unreal.Vector(move_vec.x, move_vec.y, 0.0)
                    rot = unreal.MathLibrary.find_look_at_rotation(origin, target)
                    focus_actor.set_actor_rotation(rot, False)
                    focus_actor.set_actor_location(origin, False, False)
                    focus_actor.set_actor_scale3d(
                        unreal.Vector(max_dist_cm / 100.0, width_cm / 100.0, thickness_cm / 100.0)
                    )
                    log(f"✓ Origin flat cube aligned; length set to {max_dist_cm:.1f}cm")
                else:
                    log("⚠ Origin flat cube not found to align")
            except Exception as e:
                log(f"⚠ Warning: Could not align origin flat cube: {e}")

        # TODO: Add Look at Track - need to research correct API
        log("\n⚠ Camera look-at tracking not yet implemented")
    else:
        log("⚠ Warning: Failed to add mannequin binding")

    # ===== STEP 7: Save and open sequence =====
    log("\n" + "=" * 60)
    log("STEP 7: Finalizing")
    log("=" * 60)

    # Save sequence
    saved = unreal.EditorAssetLibrary.save_loaded_asset(sequence)
    if saved:
        log("✓ Sequence saved")

    # Open in Sequencer
    unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(sequence)
    log("✓ Sequence opened in Sequencer")

    # Lock viewport to camera cuts - this makes the viewport show what the camera sees
    unreal.LevelSequenceEditorBlueprintLibrary.set_lock_camera_cut_to_viewport(True)
    log("✓ Viewport locked to sequencer camera")

    # Wait 2 seconds to allow UI to update
    import time
    time.sleep(2)

    # Refresh the current sequence to update UI
    unreal.LevelSequenceEditorBlueprintLibrary.refresh_current_level_sequence()

    # Set playback position to frame 0
    unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(0)

    # Play the sequence
    unreal.LevelSequenceEditorBlueprintLibrary.play()
    log("✓ Sequence playing from frame 0")

    # ===== COMPLETE =====
    log("\n" + "=" * 60)
    log("✓ SCENE SETUP COMPLETE!")
    log("=" * 60)
    log(f"Sequence: {sequence_name}")
    log(f"Camera: {camera_name}")
    log(f"Mannequin: {mannequin_name}")
    log(f"Duration: {duration_seconds}s @ {fps}fps")
    log("=" * 60)
    log("\nCheck Sequencer to see your complete scene!")

except Exception as e:
    log("\n" + "=" * 60)
    log("✗ FATAL ERROR")
    log("=" * 60)
    log("Error type: " + type(e).__name__)
    log("Error message: " + str(e))

    import traceback
    log("\nFull traceback:")
    for line in traceback.format_exc().split('\n'):
        if line:
            log("  " + line)
    log("=" * 60)

print("\nDone!")
