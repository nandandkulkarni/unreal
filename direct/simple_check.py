"""
Simple diagnostic to check mannequin in level.
"""

import unreal

# Find existing mannequin in the level
all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
mannequin = None

for actor in all_actors:
    label = actor.get_actor_label()
    if "TestMannequin" in label:
        mannequin = actor
        break

if not mannequin:
    print("No TestMannequin found in level")
else:
    print(f"Found mannequin: {mannequin.get_actor_label()}")
    print(f"Type: {type(mannequin).__name__}")
    
    # Check skeletal mesh components
    skel_comps = mannequin.get_components_by_class(unreal.SkeletalMeshComponent)
    print(f"\nSkeletalMeshComponents: {len(skel_comps)}")
    
    for comp in skel_comps:
        print(f"  Component: {comp.get_name()}")
        mesh = comp.skeletal_mesh
        if mesh:
            print(f"    Mesh: {mesh.get_name()}")
        else:
            print(f"    Mesh: None (THIS IS THE PROBLEM!)")
