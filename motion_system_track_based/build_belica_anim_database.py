"""
Build Belica Animation Database for Motion Matching

This script scans Belica's animation folder in Unreal Engine and creates a database
of animations with their properties (speed, type, etc.) for motion matching.

Usage:
    Run this script inside Unreal Engine's Python console or via Remote Control
"""

import unreal
import json
import os

def analyze_animation(anim_sequence):
    """
    Analyze an animation sequence to extract metadata.
    
    Args:
        anim_sequence: unreal.AnimSequence object
        
    Returns:
        dict with animation metadata
    """
    anim_name = anim_sequence.get_name()
    
    # Get animation length and frame rate
    sequence_length = anim_sequence.get_editor_property('sequence_length')
    frame_rate = anim_sequence.get_editor_property('target_frame_rate')
    num_frames = anim_sequence.get_number_of_frames()
    
    # Try to extract root motion distance (if available)
    # This requires the animation to have root motion enabled
    root_motion_distance = 0.0
    natural_speed = 0.0
    
    try:
        # Get root motion transform
        # Note: This is an approximation - actual root motion extraction is complex
        # For now, we'll estimate based on animation name patterns
        pass
    except:
        pass
    
    # Classify animation based on name patterns
    anim_type = "unknown"
    estimated_speed = 0.0
    
    name_lower = anim_name.lower()
    
    # Walking animations
    if "walk" in name_lower:
        anim_type = "walk"
        estimated_speed = 1.5  # m/s
    
    # Jogging animations
    elif "jog" in name_lower:
        anim_type = "jog"
        estimated_speed = 3.5  # m/s
    
    # Running animations
    elif "run" in name_lower or "sprint" in name_lower:
        anim_type = "run"
        estimated_speed = 5.5  # m/s
    
    # Idle/standing
    elif "idle" in name_lower or "stand" in name_lower:
        anim_type = "idle"
        estimated_speed = 0.0
    
    # Crouching
    elif "crouch" in name_lower:
        anim_type = "crouch"
        estimated_speed = 1.0
    
    # Jumping
    elif "jump" in name_lower:
        anim_type = "jump"
        estimated_speed = 0.0
    
    # Determine direction
    direction = "forward"
    if "bwd" in name_lower or "back" in name_lower:
        direction = "backward"
    elif "left" in name_lower:
        direction = "left"
    elif "right" in name_lower:
        direction = "right"
    
    return {
        "name": anim_name,
        "type": anim_type,
        "direction": direction,
        "duration": sequence_length,
        "frames": num_frames,
        "fps": frame_rate,
        "estimated_speed_mps": estimated_speed,
        "path": anim_sequence.get_path_name()
    }

def build_belica_animation_database():
    """
    Scan Belica's animation folder and build a database.
    
    Returns:
        dict with categorized animations
    """
    # Belica animation folder path
    belica_anim_folder = "/Game/ParagonLtBelica/Characters/Heroes/Belica/Animations"
    
    print(f"Scanning animations in: {belica_anim_folder}")
    
    # Get asset registry
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    
    # Find all AnimSequence assets in the folder
    filter = unreal.ARFilter(
        class_names=["AnimSequence"],
        package_paths=[belica_anim_folder],
        recursive_paths=True
    )
    
    assets = asset_registry.get_assets(filter)
    
    print(f"Found {len(assets)} animation assets")
    
    # Build database
    database = {
        "character": "Belica",
        "base_path": belica_anim_folder,
        "animations": [],
        "by_type": {
            "idle": [],
            "walk": [],
            "jog": [],
            "run": [],
            "crouch": [],
            "jump": [],
            "unknown": []
        }
    }
    
    for asset_data in assets:
        # Load the animation
        anim_path = asset_data.object_path
        anim = unreal.load_object(None, str(anim_path))
        
        if anim and isinstance(anim, unreal.AnimSequence):
            # Analyze the animation
            anim_info = analyze_animation(anim)
            
            # Add to database
            database["animations"].append(anim_info)
            
            # Categorize by type
            anim_type = anim_info["type"]
            if anim_type in database["by_type"]:
                database["by_type"][anim_type].append(anim_info)
            else:
                database["by_type"]["unknown"].append(anim_info)
            
            print(f"  [{anim_type:8s}] {anim_info['name']:40s} ({anim_info['estimated_speed_mps']:.1f} m/s)")
    
    return database

def save_database_to_json(database, output_path):
    """Save database to JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2)
    print(f"\nDatabase saved to: {output_path}")

def print_summary(database):
    """Print a summary of the database."""
    print("\n" + "="*60)
    print("ANIMATION DATABASE SUMMARY")
    print("="*60)
    print(f"Character: {database['character']}")
    print(f"Total Animations: {len(database['animations'])}")
    print("\nBy Type:")
    for anim_type, anims in database["by_type"].items():
        if anims:
            print(f"  {anim_type:10s}: {len(anims):3d} animations")
    print("="*60)

if __name__ == "__main__":
    # Build the database
    database = build_belica_animation_database()
    
    # Print summary
    print_summary(database)
    
    # Save to JSON
    output_path = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\belica_anim_database.json"
    save_database_to_json(database, output_path)
    
    print("\n✓ Animation database created successfully!")
    print(f"  Use this database in motion_cmds/splines.py for motion matching")
