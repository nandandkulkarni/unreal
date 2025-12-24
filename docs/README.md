# Motion Command System for Unreal Engine

A high-level, command-based motion choreography system for Unreal Engine that replaces manual keyframe calculations with intuitive motion commands.

## 🚀 Quick Start

### Run Tests (Recommended First Step)
```python
# In Unreal Python console:
exec(open(r'C:\UnrealProjects\Coding\unreal\tests\run_integrated_test.py').read())
```

This will:
- Run 5 automated tests
- Verify motion accuracy (position, rotation, duration)
- Generate troubleshooting log with detailed diagnostics
- Report pass/fail status

### Run Demo Scene
```python
# Full motion demo with camera tracking:
exec(open(r'C:\UnrealProjects\Coding\unreal\demos\belica_scene_v3_motion_demo.py').read())
```

## 📁 Project Structure

```
unreal/
├── motion_system/          # Core system modules
│   ├── motion_planner.py       # Pass 1: Commands → Keyframes
│   ├── keyframe_applier.py     # Pass 2: Keyframes → Unreal
│   ├── debug_db.py            # SQLite debugging database
│   ├── logger.py              # Logging utilities
│   ├── cleanup.py             # Asset cleanup
│   ├── sequence_setup.py      # Sequence management
│   ├── camera_setup.py        # Camera creation
│   ├── mannequin_setup.py     # Character creation
│   ├── hud_setup.py           # HUD/UI setup
│   └── visual_aids.py         # Visual debugging aids
│
├── tests/                  # Testing framework
│   ├── run_integrated_test.py     # ⭐ All-in-one test runner
│   ├── run_motion_tests.py        # Basic test suite
│   ├── test_motion_system.py      # Test framework core
│   ├── query_debug_db.py          # Database query tools
│   └── test_sqlite_support.py     # SQLite compatibility check
│
├── demos/                  # Example scripts
│   ├── belica_scene_v3_motion_commands.py  # V3 motion demo
│   └── unreal_setup_complete_belica_scene_updated_v2.py  # V2 demo
│
├── tools/                  # Utility scripts
│   └── enumerate_all_api_properties.py  # API documentation generator
│
├── docs/                   # Documentation
│   ├── plan.md                # Development plan & roadmap
│   ├── api_reference.txt      # Unreal API reference
│   └── README.md             # This file
│
└── output/                 # Generated files (gitignored)
    ├── troubleshooting_log_*.txt
    └── motion_debug.db
```

## 🎯 Features

### Command-Based Motion API
```python
motion_plan = [
    {"actor": "character", "command": "animation", "name": "Jog_Fwd"},
    {"actor": "character", "command": "move_by_distance", "direction": "forward", "meters": 5, "speed_mph": 3},
    {"actor": "character", "command": "turn_by_degree", "degrees": 90},
    {"actor": "character", "command": "move_to_location", "x": 500, "y": 500, "z": 0, "speed_mph": 5}
]
```

### Supported Commands
- **Movement**: `move_by_distance`, `move_for_seconds`, `move_to_location`, `move_to_waypoint`, `move_and_turn`
- **Rotation**: `turn_by_direction`, `turn_by_degree`
- **Animation**: `animation` (set active animation)
- **Timing**: `wait` (pause for seconds)

### Two-Pass Architecture
1. **Pass 1 (motion_planner.py)**: Converts motion commands → keyframe data (pure Python)
2. **Pass 2 (keyframe_applier.py)**: Applies keyframe data → Unreal Sequencer

### Testing & Debugging
- **Automated Tests**: 5 test cases validating position, rotation, duration
- **SQLite Database**: Structured logging for deep analysis
- **Troubleshooting Logs**: AI-friendly diagnostic output
- **Query Tools**: Interactive database analysis

## 🧪 Testing

### Run Full Test Suite
```python
exec(open(r'C:\UnrealProjects\Coding\unreal\tests\run_integrated_test.py').read())
```

### Analyze Results
```python
# Interactive query tool
exec(open(r'C:\UnrealProjects\Coding\unreal\tests\query_debug_db.py').read())

# Programmatic queries
from motion_system.debug_db import get_debug_db
db = get_debug_db()
db.get_test_summary()
db.find_error_source(tolerance_cm=1.0)
db.get_command_error_stats()
```

### Test Outputs
- **Console**: Real-time pass/fail results
- **output/troubleshooting_log_*.txt**: Timestamped diagnostics
- **output/motion_debug.db**: SQLite database with all test data

## 📊 Database Analysis

The SQLite database stores:
- Test runs with timestamps
- Individual tests with start position/rotation
- Motion commands with parameters
- Expected keyframes (Pass 1 output)
- Actual keyframes (from Unreal sequence)
- Test assertions (pass/fail with tolerances)
- Waypoints created during tests

### Example Queries
```python
# Find which command introduced error
db.find_error_source(tolerance_cm=1.0)

# Get error statistics by command type
db.get_command_error_stats()

# Compare Pass 1 vs Pass 2 (conversion validation)
db.compare_pass1_pass2(tolerance=0.1)

# Detect regressions vs baseline
db.get_regression_analysis(baseline_run_id=1)
```

## 🛠️ Development

### Adding New Commands
1. Add handler in `motion_system/motion_planner.py`
2. Update `plan_motion()` dispatcher
3. Add test case in `tests/run_integrated_test.py`

### Running Tests During Development
```python
# Test specific feature
exec(open(r'C:\UnrealProjects\Coding\unreal\tests\run_integrated_test.py').read())

# Check database for issues
exec(open(r'C:\UnrealProjects\Coding\unreal\tests\query_debug_db.py').read())
```

## 📖 Documentation

- **plan.md**: Comprehensive development plan, history, and roadmap
- **api_reference.txt**: Generated Unreal Python API documentation
- **troubleshooting_log_*.txt**: Test run diagnostics

## 🎬 Example Usage

### Simple Movement
```python
motion_plan = [
    {"actor": "hero", "command": "animation", "name": "Walk_Fwd"},
    {"actor": "hero", "command": "move_by_distance", "direction": "forward", "meters": 10, "speed_mph": 5}
]
```

### Waypoint System
```python
motion_plan = [
    {"actor": "hero", "command": "move_by_distance", "direction": "forward", "meters": 5, "speed_mph": 3, "waypoint_name": "checkpoint"},
    {"actor": "hero", "command": "turn_by_degree", "degrees": 180},
    {"actor": "hero", "command": "move_to_waypoint", "waypoint": "checkpoint", "speed_mph": 5}
]
```

### Complex Choreography
```python
motion_plan = [
    {"actor": "hero", "command": "animation", "name": "Run_Fwd"},
    {"actor": "hero", "command": "move_and_turn", "direction": "forward", "meters": 5, "turn_degrees": 45, "speed_mph": 8, "turn_speed_deg_per_sec": 90},
    {"actor": "hero", "command": "wait", "seconds": 2},
    {"actor": "hero", "command": "move_for_seconds", "direction": "backward", "seconds": 3, "speed_mph": 4}
]
```

## 🔍 Troubleshooting

### Tests Failing?
1. Check `output/troubleshooting_log_*.txt` for detailed diagnostics
2. Run `query_debug_db.py` for interactive analysis
3. Look for error sources: `db.find_error_source(tolerance_cm=1.0)`

### Common Issues
- **Import errors**: Ensure parent directory is in `sys.path`
- **Position errors**: Check speed conversions and direction vectors
- **Rotation drift**: Validate turn command calculations
- **Pass 1→2 mismatch**: Query `db.compare_pass1_pass2()`

## 📝 Version History

- **V3** (Current): Command-based motion system with SQLite debugging
- **V2**: Modular system with camera look-at tracking
- **V1**: Monolithic script (deprecated)

## 🎯 Next Steps

See `docs/plan.md` for:
- Development roadmap
- Known issues
- Future features
- Success criteria

---

**Status**: Production-ready ✓  
**Last Updated**: December 23, 2025  
**Recommended Entry Point**: `tests/run_integrated_test.py`
