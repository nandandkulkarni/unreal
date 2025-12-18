import unreal

actors = unreal.EditorActorSubsystem().get_all_level_actors()
mannequin = [a for a in actors if "TestMannequin" in a.get_actor_label()]

if mannequin:
    m = mannequin[0]
    print(f"Mannequin: {m.get_actor_label()}")
    print(f"Location: {m.get_actor_location()}")
    print(f"Scale: {m.get_actor_scale3d()}")
    print(f"Hidden: {m.is_hidden_ed()}")
    
    skel_comp = m.get_components_by_class(unreal.SkeletalMeshComponent)[0]
    print(f"\nComponent: {skel_comp.get_name()}")
    print(f"Visible: {skel_comp.get_editor_property('visible')}")
    print(f"Hidden in Game: {skel_comp.get_editor_property('hidden_in_game')}")
    
    materials = skel_comp.get_materials()
    print(f"\nMaterials: {len(materials)}")
    for i, mat in enumerate(materials):
        print(f"  [{i}] {mat.get_name() if mat else 'None'}")
else:
    print("No mannequin found")
