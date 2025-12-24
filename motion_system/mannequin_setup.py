"""
Mannequin/character creation and configuration
"""
import unreal
from logger import log, log_header


def create_mannequin(mannequin_name, location=None, rotation=None, mesh_path=None):
    """Create a skeletal mesh actor (Belica character)"""
    log_header("STEP 4: Creating mannequin")

    if location is None:
        location = unreal.Vector(0, 0, 300)  # Z=300
    if rotation is None:
        # Belica's mesh visual is 90° off - rotate -90° to make her face Red (+X)
        rotation = unreal.Rotator(pitch=0.0, yaw=-90.0, roll=0.0)  # Align visual with Red

    # Load the desired skeletal mesh
    skeletal_mesh = None
    if mesh_path:
        skeletal_mesh = unreal.load_object(None, mesh_path)
    
    if not skeletal_mesh:
        skeletal_mesh = unreal.load_object(None, "/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica")

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
            location,
            rotation
        )

        if mannequin:
            mannequin.set_actor_label(mannequin_name)

            # Set the skeletal mesh on the component
            skel_comp = mannequin.skeletal_mesh_component
            skel_comp.set_skeletal_mesh(skeletal_mesh)

            log(f"✓ Mannequin created: {mannequin_name}")
            log(f"  Location: {location}")
            log(f"  Mesh: {skeletal_mesh.get_name()}")
            log(f"  Rotation: Pitch={rotation.pitch}, Yaw={rotation.yaw}, Roll={rotation.roll}")

            # Debug: Check mannequin's forward direction
            forward_vec = mannequin.get_actor_forward_vector()
            log(f"  Forward Vector: X={forward_vec.x:.3f}, Y={forward_vec.y:.3f}, Z={forward_vec.z:.3f}")

            return mannequin
        else:
            log("✗ ERROR: Failed to spawn mannequin")
            raise Exception("Mannequin spawn failed")
    else:
        log("✗ ERROR: Could not load skeletal mesh")
        raise Exception("Skeletal mesh not found")
