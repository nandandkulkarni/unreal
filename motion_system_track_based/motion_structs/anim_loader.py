"""
Animation Database Loader

Loads animation metadata from .jsonx databases for motion matching.
Supports multiple characters (Belica, Manny).
"""

import json
import os

# Cache for loaded animation databases
_ANIM_DB_CACHE = {}

def load_animation_database(character="belica"):
    """
    Load animation database from .jsonx file.
    
    Args:
        character: Character name ("belica" or "manny")
    
    Returns:
        dict with animation database or None if failed
    """
    global _ANIM_DB_CACHE
    
    # Return cached version if available
    cache_key = character.lower()
    if cache_key in _ANIM_DB_CACHE:
        return _ANIM_DB_CACHE[cache_key]
    
    # Path to animation database
    db_filename = f"{cache_key}_anims.jsonx"
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "motion_structs",
        db_filename
    )
    
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            _ANIM_DB_CACHE[cache_key] = json.load(f)
        return _ANIM_DB_CACHE[cache_key]
    except Exception as e:
        print(f"Warning: Could not load {character} animation database: {e}")
        return None

def find_animation_by_type(anim_type, direction="forward", character="belica"):
    """
    Find an animation by type and direction.
    
    Args:
        anim_type: Animation type (idle, walk, jog, run, etc.)
        direction: Direction (forward, backward, left, right)
        character: Character name ("belica" or "manny")
        
    Returns:
        Animation metadata dict or None
    """
    db = load_animation_database(character)
    if not db:
        return None
    
    # Search animations by type
    for anim in db.get("animations", []):
        if anim.get("type") == anim_type and anim.get("direction") == direction:
            return anim
    
    # Fallback: return first animation of type (any direction)
    for anim in db.get("animations", []):
        if anim.get("type") == anim_type:
            return anim
    
    return None

def get_animation_speed(anim_name, character="belica"):
    """
    Get natural speed for an animation by name.
    
    Args:
        anim_name: Animation name
        character: Character name ("belica" or "manny")
        
    Returns:
        Speed in m/s or 0.0 if not found
    """
    db = load_animation_database(character)
    if not db:
        return 0.0
    
    for anim in db.get("animations", []):
        if anim.get("name") == anim_name:
            return anim.get("natural_speed_mps", 0.0)
    
    return 0.0
