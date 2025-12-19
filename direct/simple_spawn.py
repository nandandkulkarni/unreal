import unreal

# Simple, working MetaHuman spawn using available assets
print("\n" + "="*60)
print("SPAWNING GENERIC METAHUMAN")
print("="*60 + "\n")

# Spawn SkeletalMeshActor
location = unreal.Vector(0, 0, 100)
rotation = unreal.Rotator(0, 0, 0)

character = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.SkeletalMeshActor,
    location,
    rotation
)

print(f"✓ Actor spawned: {character.get_name()}")

# Get component
mesh_comp = character.skeletal_mesh_component

# Load and assign body mesh
body_mesh = unreal.load_asset("/MetaHumanCharacter/Body/IdentityTemplate/SKM_Body")
if body_mesh:
    mesh_comp.set_skinned_asset_and_update(body_mesh)
    print(f"✓ Body mesh assigned")

# Load and assign animation
anim_bp = unreal.load_asset("/MetaHumanCharacter/Body/ABP_Body_PostProcess")
if anim_bp:
    mesh_comp.set_animation_mode(unreal.AnimationMode.ANIMATION_BLUEPRINT)
    mesh_comp.set_anim_instance_class(anim_bp.generated_class())
    print(f"✓ Animation assigned")

print("\n✓ DONE! Check your viewport")
print("="*60 + "\n")
