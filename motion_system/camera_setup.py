"""
Camera creation and configuration
"""
import unreal
from logger import log, log_header


def create_camera(camera_name, location=None, rotation=None):
    """Create a cine camera actor"""
    log_header("STEP 3: Creating camera")

    if location is None:
        location = unreal.Vector(0, 0, 300)
    if rotation is None:
        # Face forward (toward +Y) at mannequin - yaw=90
        rotation = unreal.Rotator(pitch=0.0, yaw=90.0, roll=0.0)

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

        log(f"✓ Camera created: {camera_name}")
        log(f"  Location: {location}")
        log(f"  Rotation: {rotation}")
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
        component = camera.get_cine_camera_component()
        
        # 1. Setup LookAt Tracking
        # Try both common property names
        tracking_settings = None
        for prop in ["lookat_tracking_settings", "look_at_tracking_settings"]:
            if hasattr(component, prop):
                tracking_settings = component.get_editor_property(prop)
                break
        
        if not tracking_settings:
            log("  ⚠ Could not find LookAt tracking property on CineCameraComponent")
            return
            
        tracking_settings.set_editor_property("enable_lookat_tracking", True)
        tracking_settings.set_editor_property("actor_to_track", target_actor)
        
        if offset:
            tracking_settings.set_editor_property("relative_offset", offset)
        
        if interp_speed > 0:
            tracking_settings.set_editor_property("lookat_tracking_interp_speed", interp_speed)
        
        component.set_editor_property("lookat_tracking_settings", tracking_settings)
        
        # 2. Setup Focus Tracking (Auto Focus)
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
