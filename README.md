# Unreal Engine Motion Command System

Automated character motion testing and rendering system for Unreal Engine 5.7 using Python.

## 🎯 Overview

This project provides a complete motion command system with automated testing, verification, and video rendering capabilities for Unreal Engine characters. All tests passing with exact accuracy (6/6 ✓).

## ✨ Features

- ✅ **Motion Command System** - move_forward, turn, move_to_location, waypoint navigation
- ✅ **Automated Testing Framework** - 6 comprehensive tests with 1cm/0.5°/100ms tolerance
- ✅ **All Tests Passing** - 100% success rate with exact accuracy
- ✅ **Test Verification** - Position, rotation, and timing validation with detailed reports
- ✅ **Visual Axis Markers** - Permanent world origin reference (4 colored segments)
- ✅ **Sequence Preservation** - Optional keep_sequence flag for specific test results
- ✅ **Video Rendering** - MoviePipelineQueueSubsystem integration for PNG sequence output
- ✅ **Remote Control API** - External script execution via HTTP (localhost:30010)
- ✅ **Named Sequences** - TestSequence_{TestName}_{timestamp}_{number} format

## 📊 Test Results

**Current Status: All Tests Passing (6/6) ✓**

| Test | Final Position | Rotation | Status |
|------|---------------|----------|--------|
| Simple Forward | (0, -500, 6.88) | 180° | ✓ PASS |
| Turn and Move | (0, -300, 6.88) | 90° | ✓ PASS |
| Move to Location | (500, 500, 6.88) | N/A | ✓ PASS |
| Waypoint | (0, 0, 6.88) | 0° | ✓ PASS |
| Complex Path | (300, 0, 6.88) | 0° | ✓ PASS |
| **Square Path Return** | **(0.00, 0.00, 6.88)** | **0°** | **✓ PASS** |

*Square Path Return test demonstrates perfect return to origin after 5m×5m path*

## 📁 Project Structure

```
unreal/
├── tests/
│   ├── run_integrated_test.py          # Main test runner (6 tests)
│   ├── test_database.py                # SQLite database utilities
│   └── axis_markers.py                 # Visual reference markers
├── motion_system/
│   ├── commands.py                     # Motion command implementation
│   ├── sequence_setup.py               # Level sequence creation
│   ├── verification.py                 # Test result validation
│   ├── cleanup.py                      # Asset cleanup
│   └── troubleshooting.py              # Diagnostic logging
```

## 🚀 Quick Start

### Running Motion Tests (Inside Unreal)

1. Open Unreal Engine project
2. Go to **Tools → Execute Python Script**
3. Select `tests/run_integrated_test.py`
4. Click **Execute**

**Results:**
- All 6 tests execute automatically
- Console shows PASS/FAIL for each test
- Sequences created: `TestSequence_{TestName}_{timestamp}_{number}`
- Axis markers created at world origin
- Database updated: `motion_test_results.db`

### Rendering Test Results

**Option 1: Remote Control (Recommended)**
```bash
cd external_control
python render_test_sequence.py
```

**Option 2: Manual**
1. In Unreal: Window → Cinematics → Movie Render Queue
2. Click "Render (Local)"

**Output:** PNG sequence at 1920×1080, 30fps in `output/` folder

## 📋 Available Tests

| # | Test Name | Description | Duration | Accuracy |
|---|-----------|-------------|----------|----------|
| 1 | Simple Forward | 5m straight movement | 5.97s | ✓ Perfect |
| 2 | Turn and Move | 90° turn + 3m forward | 5.97s | ✓ Perfect |
| 3 | Move to Location | Direct to (500,500) | 7.68s | ✓ Perfect |
| 4 | Waypoint | 3-waypoint navigation | 11.94s | ✓ Perfect |
| 5 | Complex Path | Square with 4 turns | 20.91s | ✓ Perfect |
| 6 | **Square Path Return** | **5m×5m square to origin** | **16s** | **✓ 0.00cm error** |

## 🎨 Visual Axis Markers

Automatically created at world origin (0, 0, 6.88):
- **Red** (+X): 200cm forward
- **Yellow** (-X): 200cm backward  
- **Blue** (+Y): 200cm right
- **Purple** (-Y): 200cm left

**Specs:** 2cm width, 1mm thickness, StaticMesh with MaterialInstanceDynamic

## 🔧 Configuration

### Test Definition Format

```python
{
    "name": "Test Name",
    "commands": [
        {"type": "move_forward", "distance": 500.0, "duration": 2.0},
        {"type": "turn", "angle": 90.0, "duration": 1.0},
    ],
    "expected_final_position": {"x": 0.0, "y": -500.0, "z": 6.88},
    "expected_final_rotation": {"yaw": 90.0},
    "keep_sequence": True  # Optional: preserve this sequence
}
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
