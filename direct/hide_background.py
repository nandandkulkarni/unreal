import unreal

# Get all actors in the level
actors = unreal.EditorActorSubsystem().get_all_level_actors()

hidden_count = 0

for actor in actors:
    label = actor.get_actor_label()
    
    # Don't hide our test actors or essential actors
    if "TestMannequin" in label or "TestCamera" in label:
        continue
    
    # Don't hide essential editor actors
    actor_type = type(actor).__name__
    if actor_type in ["WorldSettings", "DefaultPhysicsVolume", "LightmassImportanceVolume"]:
        continue
    
    # Hide the actor
    actor.set_is_temporarily_hidden_in_editor(True)
    hidden_count += 1

print(f"Hidden {hidden_count} background actors")
print("Your mannequin and camera are still visible")
