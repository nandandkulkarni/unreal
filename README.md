# Unreal Engine Cinematic Pipeline - Python Scripts

Automated cinematic sequence creation for Unreal Engine 5.7 using Python.

## Overview

This project provides Python scripts to create cinematic sequences in Unreal Engine with character animations, camera movements, and professional cinematography settings.

## Features

- ✅ Automated Level Sequence creation
- ✅ Character walking animation with proper skeletal animations
- ✅ Cinematic camera with orbital tracking movement
- ✅ Depth of field and professional camera settings (50mm lens, f/2.8)
- ✅ Remote Control API support for external execution
- ✅ Comprehensive logging system

## Project Structure

```
CinematicPipeline_Scripts/
├── unreal_scripts/              # Scripts to run inside Unreal Editor
│   ├── create_complete_cinematic.py    # Main: Creates everything in one go
│   ├── create_walk_sequence.py         # Character animation only
│   └── add_camera_to_sequence.py       # Add camera to existing sequence
├── external_control/            # Scripts to run from external Python
│   └── run_cinematic_script.py         # Execute scripts via Remote Control API
├── logs/                        # Execution logs with timestamps
├── setup_remote_control.py      # Configure Remote Control API
└── README.md                    # This file
```

## Setup

### 1. Prerequisites

- Unreal Engine 5.7
- Python 3.11+ (embedded in Unreal)

### 2. Project Setup

No additional setup required. Scripts run directly inside Unreal Engine.

## Usage

### Running Scripts Inside Unreal Editor

1. Open Unreal Engine project
2. Go to **Tools → Execute Python Script**
3. Select `unreal_scripts/create_complete_cinematic.py`
4. Click **Execute**

The script will:
- Delete old sequences and cameras
- Create a new Level Sequence
- Add character with walking animation
- Add cinematic camera with orbital movement
- Save and open in Sequencer

### Quick Access to Scripts

Scripts are located at:
- Main: `C:\U\CinematicPipeline_Scripts\unreal_scripts\create_complete_cinematic.py`
- Character only: `create_walk_sequence.py`  
- Camera only: `add_camera_to_sequence.py`

## Scripts

### Main Scripts

#### `create_complete_cinematic.py` ⭐
**All-in-one solution** - Creates complete cinematic from scratch:
- Cleans up old assets
- Creates character walking sequence (10 seconds, square path)
- Adds cinematic camera with orbital tracking
- Configures depth of field and professional settings

**Use this for:** Fresh start, repeatable setup

#### `create_walk_sequence.py`
Creates character animation only:
- Character walking through 5 waypoints
- Skeletal walking animation
- Rotation to face movement direction

**Use this for:** When you only need character animation

#### `add_camera_to_sequence.py`
Adds camera to existing sequence:
- Spawns CineCameraActor
- Adds orbital tracking movement
- Configures cinematic settings (DOF, focal length)

**Use this for:** Adding camera after character sequence is created

### Utility Scripts

#### `setup_remote_control.py`
Configures project for Remote Control API (experimental - not fully functional in UE 5.7):
- Adds Python execution settings to DefaultEngine.ini
- Creates backup of configuration
- Note: Remote Control API blocks PythonScriptLibrary in UE 5.7 for security

#### `run_cinematic_script.py`
Attempts to execute scripts via Remote Control API:
- Not currently functional due to UE 5.7 security restrictions
- Kept for reference and future versions

## Configuration

### Sequence Parameters

Edit in `create_complete_cinematic.py`:

```python
# Sequence duration
start_frame = 0
end_frame = 240  # 10 seconds at 24fps
fps = 24

# Character waypoints (time, x, y, z, yaw)
waypoints = [
    (0.0, 0, 0, 100, 0),       # Start
    (2.5, 300, 0, 100, 90),    # Right
    (5.0, 300, 300, 100, 180), # Up
    (7.5, 0, 300, 100, 270),   # Left
    (10.0, 0, 0, 100, 0)       # Back
]

# Camera path (time, x, y, z, pitch, yaw)
camera_keyframes = [
    (0.0, -200, -300, 250, -15, 30),
    (2.5, 100, -300, 280, -18, 45),
    (5.0, 400, 100, 300, -20, 135),
    (7.5, 200, 500, 280, -18, 225),
    (10.0, -200, 400, 250, -15, 315)
]
```

### Camera Settings

```python
# Filmback (sensor size)
camera_component.filmback.sensor_width = 36.0   # mm
camera_component.filmback.sensor_height = 24.0  # mm

# Lens
camera_component.current_focal_length = 50.0    # mm

# Depth of Field
camera_component.current_aperture = 2.8         # f-stop
camera_component.focus_settings.manual_focus_distance = 400.0  # cm
```

## Troubleshooting

### Script Execution Issues

**Error: "Character not found"**
- Make sure level has a ThirdPersonCharacter
- Check character path in script (searches automatically)

**Error: "Walking animation not found"**
- Verify animation path: `/Game/Characters/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Fwd`
- Check if Mannequin content is installed

**Camera Cut shows "No Object Binding specified"**
- Known issue with UE 5.7 Python API
- Camera still animates correctly
- Workaround: Fix applied in script, may need Unreal restart

### Remote Control API Note

Remote execution via Remote Control API is not currently functional in UE 5.7 due to security restrictions on PythonScriptLibrary access. Use the in-editor execution method (Tools → Execute Python Script) instead.

## Logs

All scripts create detailed logs in `logs/` folder:
- `cinematic_YYYYMMDD_HHMMSS.log` - Complete cinematic creation
- `create_walk_sequence.log` - Character animation logs
- `add_camera_YYYYMMDD_HHMMSS.log` - Camera addition logs

Logs include:
- Timestamps for each operation
- Success/error messages
- Asset paths and parameters
- Keyframe details

## Next Steps for YouTube Video Production

After creating the basic cinematic, consider adding:

1. **Lighting** - Add directional light, spotlights for dramatic effect
2. **Post-processing** - Color grading, bloom, lens flares
3. **Camera shake** - Add subtle shake for realism
4. **Multiple camera angles** - Create shots from different angles
5. **Sound** - Add footstep sounds, ambient audio
6. **Rendering** - Use Movie Render Queue for high-quality output

## Contributing

This is a personal project. Feel free to fork and modify for your needs.

## Repository

https://github.com/nandandkulkarni/unreal

## License

Personal project - use as you wish.
