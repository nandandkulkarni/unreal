"""
Visual aids - origin markers, axis indicators, debug cubes
"""
import unreal
from ..logger import log


def create_plus_sign_at_origin():
    """Draw a plus sign at origin using four thin cubes (1mm thick, 1m wide, 10m long each side)"""
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
