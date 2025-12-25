"""
HUD text actor setup for displaying character position
"""
import unreal
from ..logger import log


def create_hud(camera, mannequin):
    """Create HUD text actor showing Belica X/Y/Z position"""
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
