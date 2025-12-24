import unreal

editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
all_actors = editor_actor_subsystem.get_all_level_actors()

axis_actors = [actor for actor in all_actors if "Axis_" in actor.get_actor_label()]

print("\nAxis Markers Found:")
print("=" * 60)
for actor in axis_actors:
    loc = actor.get_actor_location()
    print(f"  {actor.get_actor_label()}: ({loc.x:.1f}, {loc.y:.1f}, {loc.z:.1f})")
print(f"\nTotal: {len(axis_actors)} axis marker(s)")
print("=" * 60)
