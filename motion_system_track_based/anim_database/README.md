# Animation Database Workflow

## Quick Start

To refresh the Belica animation database:

```bash
# 1. Scan animations from Unreal
python anim_database/run_scan.py

# 2. Copy to motion_structs as .jsonx
copy anim_database\belica_animations.json motion_structs\belica_anims.jsonx
```

## Files

- **`scan_belica.py`** - Scans Belica animations and saves metadata
- **`run_scan.py`** - Trigger script (runs scanner in Unreal)
- **`belica_animations.json`** - Generated database (source)
- **`../motion_structs/belica_anims.jsonx`** - Production database (copy)

## When to Refresh

Run the scanner when:
- Belica animations are updated/added
- Animation properties change
- Starting a new project phase

## Database Format

```json
{
  "character": "Belica",
  "animations": [
    {
      "name": "Jog_Fwd",
      "type": "jog",
      "direction": "forward",
      "estimated_speed_mps": 3.5,
      "duration": 1.33,
      "frames": 40,
      "path": "/Game/ParagonLtBelica/.../Jog_Fwd.Jog_Fwd"
    }
  ],
  "by_type": {
    "jog": [...],
    "run": [...],
    ...
  }
}
```

## Usage in Motion Matching

```python
import json

# Load animation database
with open('motion_structs/belica_anims.jsonx', 'r') as f:
    anim_db = json.load(f)

# Get jog animations
jog_anims = anim_db['by_type']['jog']

# Find specific animation
for anim in anim_db['animations']:
    if anim['name'] == 'Jog_Fwd':
        speed = anim['estimated_speed_mps']
        duration = anim['duration']
```

## Notes

- Scanner uses `EditorAssetLibrary.list_assets()` - proven reliable
- Frame count calculated from duration (30 fps assumption)
- `.jsonx` extension distinguishes it from regular config files
- Database is ~90KB with 150+ animations
