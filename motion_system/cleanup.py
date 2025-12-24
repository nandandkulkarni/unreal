""" 
Cleanup utilities - Delete old test assets and actors
"""
import unreal
from logger import log, log_header


def close_open_sequences():
    """Close any currently open sequences"""
    logger.log("\nClosing any open sequences...")
    try:
        current_seq = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
        if current_seq:
            logger.log(f"  Closing: {current_seq.get_name()}")
            unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
            logger.log("✓ Closed open sequence")
        else:
            logger.log("  No sequence currently open")
    except Exception as e:
        logger.log(f"  Could not close sequence: {e}")


def delete_old_sequences():
    """Delete old Test* sequences"""
    logger.log("\nDeleting old Test* sequences...")
    sequences_path = "/Game/Sequences"
    deleted_sequences = 0

    if unreal.EditorAssetLibrary.does_directory_exist(sequences_path):
        assets = unreal.EditorAssetLibrary.list_assets(sequences_path, recursive=False)
        for asset_path in assets:
            asset_name = asset_path.split('/')[-1].split('.')[0]
            if asset_name.startswith("Test"):
                try:
                    unreal.EditorAssetLibrary.delete_asset(asset_path)
                    logger.log(f"  Deleted sequence: {asset_name}")
                    deleted_sequences += 1
                except Exception as e:
                    logger.log(f"  Failed to delete {asset_name}: {e}")

    if deleted_sequences > 0:
        logger.log(f"✓ Deleted {deleted_sequences} old sequence(s)")
    else:
        logger.log("  No old sequences found")


def delete_old_actors():
    """Delete old Test* actors and HUD text actors (but preserve Axis markers)"""
    logger.log("\nDeleting old Test* actors and HUD text actors...")
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    all_actors = editor_actor_subsystem.get_all_level_actors()
    deleted_actors = 0

    for actor in all_actors:
        actor_label = actor.get_actor_label()
        # Delete Test* actors and TextRenderActor, but keep Axis_ and Origin_ markers
        if (actor_label.startswith("TestCamera") or
            actor_label.startswith("TestMannequin") or
            actor_label.startswith("Test_") or
                actor.get_class().get_name() == "TextRenderActor"):
            unreal.EditorLevelLibrary.destroy_actor(actor)
            logger.log(f"  Deleted actor: {actor_label}")
            deleted_actors += 1

    if deleted_actors > 0:
        logger.log(f"✓ Deleted {deleted_actors} old actor(s)")
    else:
        logger.log("  No old actors found")


def cleanup_old_assets(keep_sequence=False):
    """Main cleanup function - removes all old test assets
    
    Args:
        keep_sequence: If True, skip deleting sequences (to preserve test results)
    """
    logger.log_header("STEP 1: Cleaning up old Test* assets")
    close_open_sequences()
    if not keep_sequence:
        delete_old_sequences()
    else:
        logger.log("\nSkipping sequence deletion (keep_sequence=True)")
    delete_old_actors()
