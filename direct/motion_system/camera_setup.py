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
