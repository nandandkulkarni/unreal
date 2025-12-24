"""
Axis Markers - Create visual reference markers at world origin
"""
import unreal
from logger import log


def create_axis_markers():
    """Create a colored plus sign at the world origin using thin static mesh cubes"""
    log("\nCreating axis markers at origin...")
    
    cube_mesh = unreal.load_object(None, "/Engine/BasicShapes/Cube.Cube")
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
            log(f"  ⚠ Failed to spawn segment: {name}")
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
                mid = unreal.MaterialInstanceDynamic.create(base_mat, actor)
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
                    log(f"  ✓ {name}: {color_lin.r:.1f},{color_lin.g:.1f},{color_lin.b:.1f}")
                else:
                    log(f"  ✓ {name} (color parameter not found)")
            except Exception as e:
                log(f"  ✓ {name} (no color support)")
                try:
                    smc.set_material(0, base_mat)
                except Exception:
                    pass

    # Compute per-axis segments (centered at origin, extending in one direction)
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

    # +Y (blue)
    spawn_segment(
        "Axis_PosY",
        unreal.Vector(0.0, length_cm / 2.0, z_loc),
        unreal.Vector(width_cm / 100.0, length_cm / 100.0, thickness_cm / 100.0),
        unreal.LinearColor(0.0, 0.0, 1.0, 1.0)
    )

    # -Y (purple)
    spawn_segment(
        "Axis_NegY",
        unreal.Vector(0.0, -length_cm / 2.0, z_loc),
        unreal.Vector(width_cm / 100.0, length_cm / 100.0, thickness_cm / 100.0),
        unreal.LinearColor(1.0, 0.0, 1.0, 1.0)
    )

    log("✓ Axis markers created (Red: +X, Yellow: -X, Blue: +Y, Purple: -Y)")
