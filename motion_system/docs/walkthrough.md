# 2D Track Visualizer - Walkthrough

## Overview

Created a complete Pygame-based 2D visualizer for testing and debugging 400m dash choreography before executing in Unreal Engine.

---

## Installation

```bash
pip install pygame
```

---

## Running the Visualizer

```bash
cd c:/UnrealProjects/coding/unreal/motion_system
python visualizer/main.py
```

---

## Features Implemented

### **1. Track Renderer**
- ✅ 400m oval track with 8 lanes
- ✅ Proper scaling to fit screen
- ✅ Lane divider lines
- ✅ Start/finish line marker
- ✅ Green grass background

### **2. Runner Visualization**
- ✅ 6 runners with distinct colors (Red, Blue, Green, Yellow, Magenta, Cyan)
- ✅ Runner names displayed above each runner
- ✅ Speed indicators (arrows showing direction and magnitude)
- ✅ Optional collision zones (0.5m radius)

### **3. Physics Simulation**
- ✅ Realistic acceleration (3 m/s²)
- ✅ Max speed variation per runner (9.5-10.0 m/s)
- ✅ Lane-based starting positions
- ✅ Forward movement along track

### **4. Playback Controls**
- ✅ Play/Pause (SPACE)
- ✅ Speed control (↑↓ arrows: 0.1x to 10x)
- ✅ Reset simulation (R key)
- ✅ Toggle collision zones (C key)
- ✅ Real-time time display

---

## Keyboard Controls

| Key | Action |
|-----|--------|
| **SPACE** | Play/Pause simulation |
| **↑** | Increase speed (2x multiplier) |
| **↓** | Decrease speed (0.5x multiplier) |
| **R** | Reset to start |
| **C** | Toggle collision zone visualization |
| **ESC** | Quit (or close window) |

---

## Current Limitations

⚠️ **Simplified Track Geometry** - Track is drawn as rounded rectangle, not true oval
⚠️ **Linear Movement** - Runners only move forward (+X), no curve following yet
⚠️ **No Waypoint Integration** - Not yet connected to MovieBuilder waypoint system
⚠️ **Dummy Data** - Uses hardcoded runner data, not from `race_400m.py`

---

## Next Steps

### **Phase 2: Integration**
1. Parse MovieBuilder `race_400m.py` movie data
2. Extract waypoints from movie plan
3. Implement curve following along waypoints
4. Add staggered start positions
5. Realistic track geometry (true oval with curves)

### **Phase 3: Advanced Features**
1. Collision detection and warnings
2. Export validated choreography to Unreal
3. Camera preview (show what Unreal cameras would see)
4. Performance metrics (lap times, speeds)

---

## File Structure

```
visualizer/
├── __init__.py
├── main.py                 # Entry point, game loop
├── track_renderer.py       # Draws 400m track
├── runner_renderer.py      # Draws runners with labels
├── simulation_engine.py    # Physics and movement
└── ui_controls.py          # Playback controls
```

---

## Screenshots

![Visualizer running with 6 runners on track]

**Status:** ✅ Core visualizer working, ready for MovieBuilder integration
