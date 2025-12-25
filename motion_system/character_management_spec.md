# Character Management Specification

## Overview

Character management system for spawning and configuring skeletal mesh actors in Unreal Engine scenes.

## Commands

### `add_actor`

Spawn a skeletal mesh actor at a specified location with optional rotation and mesh configuration.

**Syntax:**
```json
{
    "command": "add_actor",
    "actor": "CharacterName",
    "location": [x, y, z],
    "rotation": [pitch, yaw, roll],
    "yaw_offset": -90,
    "mesh_path": "/Game/Path/To/Mesh.Mesh",
    "mesh_rotation": [pitch, yaw, roll]
}
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `actor` | string | Yes | - | Unique name for the actor |
| `location` | array[3] | No | [0, 0, 0] | XYZ coordinates in cm |
| `rotation` | array[3] | No | [0, 0, 0] | Pitch, Yaw, Roll in degrees |
| `yaw_offset` | number | No | 0 | Mesh forward direction offset |
| `mesh_path` | string | No | Default mesh | Path to skeletal mesh asset |
| `mesh_rotation` | array[3] | No | [0, yaw_offset, 0] | Mesh component rotation |

## Coordinate System

**Unreal Engine Coordinates:**
- **X-axis**: North (forward)
- **Y-axis**: East (right)
- **Z-axis**: Up
- **Units**: Centimeters

**Rotation:**
- **Pitch**: Up/down tilt
- **Yaw**: Left/right rotation (compass direction)
- **Roll**: Side tilt

## Default Mesh

If no `mesh_path` is specified, the system attempts to load meshes in this order:
1. `/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica`
2. `/Game/Characters/Mannequins/Meshes/SKM_Quinn_Simple.SKM_Quinn_Simple`
3. `/Game/ThirdPerson/Characters/Mannequins/Meshes/SKM_Quinn_Simple.SKM_Quinn_Simple`

## Yaw Offset

The `yaw_offset` parameter corrects for mesh forward direction misalignment:
- **-90°**: Mesh faces right, rotate to face forward
- **0°**: Mesh already faces forward
- **90°**: Mesh faces left, rotate to face forward

## Automatic Features

**Tagging:**
- All spawned actors are tagged with `"MotionSystemActor"`
- Enables automatic cleanup on subsequent runs

**Sequence Integration:**
- Actors are automatically added to the level sequence
- Binding created for animation and transform tracks

**Visual Aids:**
- Colored axis markers spawned at actor origin
- X-axis (North): Red
- Y-axis (East): Green

## Examples

### Basic Character Spawn
```json
{
    "command": "add_actor",
    "actor": "Hero",
    "location": [0, 0, 0]
}
```

### Custom Mesh with Rotation
```json
{
    "command": "add_actor",
    "actor": "Jessica",
    "location": [500, -300, 0],
    "rotation": [0, 45, 0],
    "yaw_offset": -90,
    "mesh_path": "/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica"
}
```

### Multiple Characters (Tandem)
```json
[
    {
        "command": "add_actor",
        "actor": "Jessica",
        "location": [0, 0, 0],
        "yaw_offset": -90
    },
    {
        "command": "add_actor",
        "actor": "Sarah",
        "location": [0, -300, 0],
        "yaw_offset": -90
    }
]
```

## Implementation

**Module:** `motion_includes/mannequin_setup.py`

**Function:** `create_mannequin(name, location, rotation, mesh_path, mesh_rotation)`

**Process:**
1. Load skeletal mesh asset
2. Spawn SkeletalMeshActor at location
3. Set actor label and tags
4. Apply mesh to skeletal component
5. Set mesh rotation if specified
6. Add visual axis markers
7. Return actor reference

## Cleanup

Characters are automatically deleted on subsequent scene runs via the cleanup system, which removes all actors tagged with `"MotionSystemActor"`.

## Limitations

- Only skeletal mesh actors supported (no static meshes)
- Mesh must exist in project content
- Actor names must be unique within a scene
- Maximum actors limited by Unreal Engine performance

## Status

✅ **Production Ready** - Fully implemented and tested
