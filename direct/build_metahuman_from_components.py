"""
Build a MetaHuman character from scratch by reading MetaHumanCharacter data
This is the piece-by-piece approach for learning how MetaHumans work
"""
import unreal

print("\n" + "="*60)
print("BUILDING METAHUMAN FROM SCRATCH")
print("="*60 + "\n")

# For learning, we'll use the generic MetaHuman template which has accessible meshes
# Monica's MetaHumanCharacter asset doesn't expose individual mesh files directly

print("[APPROACH] Using generic MetaHuman template components")
print("(Monica's packaged format doesn't expose individual assets)\n")

# Step 1: Spawn empty actor
print("[STEP 1] Spawning base actor...")
location = unreal.Vector(0, 0, 100)
rotation = unreal.Rotator(0, 0, 0)

actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.Actor,
    location,
    rotation
)
actor.set_actor_label("Custom_MetaHuman")
print(f"✓ Base actor created: {actor.get_actor_label()}\n")

# Step 2: Add body skeletal mesh component
print("[STEP 2] Adding body skeletal mesh component...")
body_comp = actor.add_component_by_class(
    unreal.SkeletalMeshComponent,
    manual_attachment=False,
    relative_transform=unreal.Transform()
)
body_comp.set_editor_property("component_tags", ["Body"])

# Load body mesh
body_mesh_path = "/MetaHumanCharacter/Body/IdentityTemplate/SKM_Body"
body_mesh = unreal.load_asset(body_mesh_path)

if body_mesh:
    body_comp.set_skinned_asset_and_update(body_mesh)
    print(f"✓ Body mesh assigned: {body_mesh.get_name()}")
    
    # Set as root
    actor.set_root_component(body_comp)
    print(f"✓ Body component set as root\n")
else:
    print(f"✗ Failed to load body mesh\n")

# Step 3: Add face skeletal mesh component
print("[STEP 3] Adding face skeletal mesh component...")
face_comp = actor.add_component_by_class(
    unreal.SkeletalMeshComponent,
    manual_attachment=True,
    relative_transform=unreal.Transform()
)
face_comp.set_editor_property("component_tags", ["Face"])

# Attach face to body
face_comp.attach_to_component(body_comp, unreal.AttachmentRule.KEEP_RELATIVE, "")

# Load face mesh
face_mesh_path = "/MetaHumanCharacter/Face/SKM_Face"
face_mesh = unreal.load_asset(face_mesh_path)

if face_mesh:
    face_comp.set_skinned_asset_and_update(face_mesh)
    print(f"✓ Face mesh assigned: {face_mesh.get_name()}\n")
else:
    print(f"✗ Failed to load face mesh\n")

# Step 4: Add animation blueprints
print("[STEP 4] Adding animation blueprints...")

# Body animation
body_anim_path = "/MetaHumanCharacter/Body/ABP_Body_PostProcess"
body_anim = unreal.load_asset(body_anim_path)

if body_anim:
    body_comp.set_animation_mode(unreal.AnimationMode.ANIMATION_BLUEPRINT)
    body_comp.set_anim_instance_class(body_anim.generated_class())
    print(f"✓ Body animation blueprint assigned")
else:
    print(f"⚠ Body animation blueprint not found")

# Face animation (if available)
face_anim_path = "/MetaHuman/IdentityTemplate/Face_PostProcess_AnimBP"
face_anim = unreal.load_asset(face_anim_path)

if face_anim:
    face_comp.set_animation_mode(unreal.AnimationMode.ANIMATION_BLUEPRINT)
    face_comp.set_anim_instance_class(face_anim.generated_class())
    print(f"✓ Face animation blueprint assigned\n")
else:
    print(f"⚠ Face animation blueprint not found\n")

# Summary
print("="*60)
print("METAHUMAN BUILD COMPLETE!")
print("="*60)
print(f"Actor: {actor.get_actor_label()}")
print(f"Location: {location}")
print(f"Components:")
print(f"  - Body: {body_comp.get_name()}")
print(f"  - Face: {face_comp.get_name()}")
print("\nThis is a generic MetaHuman built from components.")
print("You can see the hierarchy in the Details panel.")
print("="*60 + "\n")

print("💡 NOTE: Monica's specific look is packaged in MetaHumanCharacter")
print("   To use Monica, you need to:")
print("   1. Drag her into the level manually (creates instance)")
print("   2. Right-click → Create Blueprint")
print("   3. Then spawn that Blueprint via Python\n")
