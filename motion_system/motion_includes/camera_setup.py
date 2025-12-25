"""
Camera creation and configuration
"""
import unreal
from ..logger import log, log_header


def create_camera_marker(location, color_name="red"):
    """Create a visual marker (pillar) for the camera location
    
    Args:
        location: vector location
        color_name: 'red', 'blue', 'green', etc.
    """
    # Create static mesh actor (Cube)
    marker = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,
        location,
        unreal.Rotator(0,0,0)
    )
    
    if not marker:
        log(f"  ⚠ Failed to spawn camera marker at {location}")
        return

    marker.set_actor_label(f"CameraMarker_{color_name}")
    marker.tags.append("MotionSystemDebug") # Tag for easier cleanup
    
    # Disable collision
    marker.set_actor_enable_collision(False)

    # Set mesh to Cube
    mesh_path = "/Engine/BasicShapes/Cube.Cube"
    mesh_asset = unreal.EditorAssetLibrary.load_asset(mesh_path)
    if mesh_asset:
        marker.static_mesh_component.set_static_mesh(mesh_asset)
    
    # Scale: 60cm x 60cm x 182.88cm (6 ft) - Wider
    marker.set_actor_scale3d(unreal.Vector(0.6, 0.6, 1.8288))
    
    # Adjust location so bottom is FLUSH ON GROUND (Z=0).
    # Pivot is center. Center Z must be half height = 91.44.
    # Ignore input location.z, force ground.
    ground_loc = unreal.Vector(location.x, location.y, 91.44)
    marker.set_actor_location(ground_loc, False, True)
    
    # Material/Color
    # User requested to use existing materials (MyRed, MyBlue, etc.)
    color_map = {
        "red": "/Game/MyMaterial/MyRed",
        "blue": "/Game/MyMaterial/MyBlue",
        "green": "/Game/MyMaterial/MyGreen",
        "yellow": "/Game/MyMaterial/MyYellow"
    }
    
    mat_path = color_map.get(color_name.lower(), "/Game/MyMaterial/MyRed")
    existing_mat = unreal.EditorAssetLibrary.load_asset(mat_path)
    
    if existing_mat:
        marker.static_mesh_component.set_material(0, existing_mat)
        log(f"  + Set marker material to {mat_path}")
    else:
        # Fallback to dynamic if specific asset missing
        try:
            # Create dynamic material
            mat = marker.static_mesh_component.create_dynamic_material_instance(0)
            
            # Colors - Solid Opaque for maximum visibility
            color = unreal.LinearColor(1, 0, 0, 1.0) # Red default
            if color_name.lower() == "blue":
                color = unreal.LinearColor(0, 0, 1, 1.0)
            elif color_name.lower() == "green":
                color = unreal.LinearColor(0, 1, 0, 1.0)
            elif color_name.lower() == "yellow":
                color = unreal.LinearColor(1, 1, 0, 1.0)
                
            mat.set_vector_parameter_value("Color", color)
            mat.set_vector_parameter_value("BaseColor", color)
        except Exception as e:
            log(f"  ⚠ Could not set marker color: {e}")

    log(f"  + Marker ({color_name}) created at {location}")


def create_camera(camera_name, location=None, rotation=None, fov=90.0, tint=None, show_marker=None):
    """Create a cine camera actor
    
    Args:
        camera_name: Name for the camera actor
        location: Camera position (default: [0, 0, 300])
        rotation: Camera rotation (default: facing +Y)
        fov: Field of view in degrees (default: 90.0)
        tint: Optional color tint [R, G, B] values 0-1
        show_marker: Optional color string ('red', 'blue') to show a debug marker at location
    """
    log_header("STEP 3: Creating camera")

    if location is None:
        location = unreal.Vector(0, 0, 300)
    
    if show_marker:
        create_camera_marker(location, show_marker)

    if rotation is None:
        # Face forward (toward +Y) at mannequin - yaw=90
        rotation = unreal.Rotator(pitch=0.0, yaw=90.0, roll=0.0)

    # Check if we should ignore look at (not implemented inside create_camera yet, handled by caller)
    
    camera = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.CineCameraActor,
        location,
        rotation
    )

    if camera:
        camera.set_actor_label(camera_name)
        camera.tags.append("MotionSystemActor")

        # Set camera properties
        camera_component = camera.get_cine_camera_component()
        camera_component.set_editor_property("current_focal_length", 50.0)
        camera_component.set_editor_property("current_aperture", 2.8)
        camera_component.set_editor_property("field_of_view", fov)
        
        # Apply tint if specified
        if tint:
            try:
                # Enable post process settings
                camera_component.set_editor_property("post_process_blend_weight", 1.0)
                
                # Get post process settings
                post_process = camera_component.get_editor_property("post_process_settings")
                
                # Set color grading tint
                post_process.set_editor_property("color_grading_intensity", 1.0)
                post_process.set_editor_property("white_temp", 6500.0)
                
                # Create color tint using scene color tint
                tint_color = unreal.LinearColor(tint[0], tint[1], tint[2], 0.3)  # Alpha = intensity
                post_process.set_editor_property("scene_color_tint", tint_color)
                
                camera_component.set_editor_property("post_process_settings", post_process)
                
                log(f"  Tint: RGB({tint[0]}, {tint[1]}, {tint[2]})")
            except Exception as e:
                log(f"  ⚠ Warning: Could not apply tint: {e}")

        log(f"✓ Camera created: {camera_name}")
        log(f"  Location: {location}")
        log(f"  Rotation: {rotation}")
        log(f"  FOV: {fov}°")
        log("  Focal Length: 50mm")
        log("  Aperture: f/2.8")
        
        return camera
    else:
        log("✗ ERROR: Failed to create camera")
        raise Exception("Camera creation failed")


def enable_lookat_tracking(camera, target_actor, offset=None, interp_speed=0.0):
    """Enable CineCamera LookAt tracking and Focus tracking
    
    Args:
        camera: The CineCameraActor
        target_actor: The actor to track
        offset: unreal.Vector for tracking offset (e.g. tracking the head instead of feet)
        interp_speed: How fast the camera follows (0 = instant/locking)
    """
    if not camera or not target_actor:
        log("  ⚠ Cannot enable LookAt tracking: Camera or Target is missing")
        return

    try:
        # 1. Setup LookAt Tracking on the CineCameraActor (not component!)
        tracking_settings = camera.get_editor_property("lookat_tracking_settings")
        
        if not tracking_settings:
            log("  ⚠ Could not find LookAt tracking property on CineCameraActor")
            return
            
        tracking_settings.set_editor_property("enable_look_at_tracking", True)
        tracking_settings.set_editor_property("actor_to_track", target_actor)
        
        if offset:
            tracking_settings.set_editor_property("relative_offset", offset)
        
        if interp_speed > 0:
            tracking_settings.set_editor_property("look_at_tracking_interp_speed", interp_speed)
        
        camera.set_editor_property("lookat_tracking_settings", tracking_settings)
        
        # 2. Setup Focus Tracking (Auto Focus) on the component
        component = camera.get_cine_camera_component()
        focus_settings = component.focus_settings
        focus_settings.focus_method = unreal.CameraFocusMethod.TRACKING
        
        tracking_focus_settings = focus_settings.tracking_focus_settings
        tracking_focus_settings.actor_to_track = target_actor
        
        # Re-apply modified struct
        component.set_editor_property("focus_settings", focus_settings)
        
        log(f"  ✓ Camera tracking & Auto-Focus enabled for: {target_actor.get_actor_label()}")
        if interp_speed > 0:
            log(f"    - Cinematic Smoothing (Interp Speed): {interp_speed}")
            
    except Exception as e:
        log(f"  ⚠ Failed to enable cinematic tracking: {e}")
        import traceback
        log(traceback.format_exc())


def position_camera_behind_mannequin(camera, mannequin, follow_distance=300.0, follow_height=50.0):
    """Position camera behind mannequin using forward vector"""
    try:
        actor_loc = mannequin.get_actor_location()
        forward = mannequin.get_actor_forward_vector()
        up = mannequin.get_actor_up_vector()

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

    except Exception as e:
        log(f"⚠ Warning: Could not position camera behind mannequin: {e}")
