"""
Cleanup utilities - Delete old test assets and actors
"""
import unreal
from logger import log, log_header


def close_open_sequences():
    """Close any currently open sequences"""
    log("\nClosing any open sequences...")
    try:
        current_seq = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
        if current_seq:
            log(f"  Closing: {current_seq.get_name()}")
            unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
            log("✓ Closed open sequence")
        else:
            log("  No sequence currently open")
    except Exception as e:
        log(f"  Could not close sequence: {e}")


def delete_old_sequences():
    """Delete old Test* sequences"""
    log("\nDeleting old Test* sequences...")
    sequences_path = "/Game/Sequences"
    deleted_sequences = 0

    if unreal.EditorAssetLibrary.does_directory_exist(sequences_path):
        assets = unreal.EditorAssetLibrary.list_assets(sequences_path, recursive=False)
        for asset_path in assets:
            asset_name = asset_path.split('/')[-1].split('.')[0]
            if asset_name.startswith("Test"):
                try:
                    unreal.EditorAssetLibrary.delete_asset(asset_path)
                    log(f"  Deleted sequence: {asset_name}")
                    deleted_sequences += 1
                except Exception as e:
                    log(f"  Failed to delete {asset_name}: {e}")

    if deleted_sequences > 0:
        log(f"✓ Deleted {deleted_sequences} old sequence(s)")
    else:
        log("  No old sequences found")


def delete_old_actors():
    """Delete old Test* actors, HUD text actors, axis segments, and debug cubes"""
    log("\nDeleting old Test* actors, HUD text actors, axis segments, and debug cubes...")
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    all_actors = editor_actor_subsystem.get_all_level_actors()
    deleted_actors = 0

    for actor in all_actors:
        actor_label = actor.get_actor_label()
        # Delete Test* actors, TextRenderActor, axis segments, and debug cubes
        if (actor_label.startswith("TestCamera") or
            actor_label.startswith("TestMannequin") or
            actor_label.startswith("Axis_") or
            actor_label.startswith("Origin_") or
            actor_label.startswith("Test_") or
                actor.get_class().get_name() == "TextRenderActor"):
            unreal.EditorLevelLibrary.destroy_actor(actor)
            log(f"  Deleted actor: {actor_label}")
            deleted_actors += 1

    if deleted_actors > 0:
        log(f"✓ Deleted {deleted_actors} old actor(s)")
    else:
        log("  No old actors found")


def cleanup_old_assets():
    """Main cleanup function - removes all old test assets"""
    log_header("STEP 1: Cleaning up old Test* assets")
    close_open_sequences()
    delete_old_sequences()
    delete_old_actors()
