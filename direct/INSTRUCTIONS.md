# Unreal Scene Setup - Instructions

## Quick Start

### Method 1: Command Line (Recommended for automation)
```powershell
cd "C:\RemoteProjects\reference\unreal\direct"
python -c "from unreal_connection import UnrealRemote; u = UnrealRemote(); success, _ = u.execute_python_file('unreal_setup_complete_scene.py'); print('Done!')"
```

### Method 2: VS Code Extension (Recommended for interactive development)
1. Open `unreal_setup_complete_scene.py` in VS Code
2. Press **Ctrl+Enter** to execute in Unreal

## Prerequisites

1. **Unreal Engine 5.7** must be running
2. **WebControl Server** started in Unreal console:
   ```
   WebControl.StartServer
   ```
3. **Remote Control configured** in `DefaultEngine.ini`:
   ```ini
   [RemoteControl]
   bRestrictServerAccess=false
   +RemoteControlWebInterfaceAllowedObjects=/Script/PythonScriptPlugin.PythonScriptLibrary
   ```
4. **VS Code Extension** (optional, for Ctrl+Enter method):
   - Install: `nilssoderman.ue-python`

## What the Script Does

Creates a complete cinematic scene:
1. Deletes old Test* sequences, cameras, and mannequins
2. Creates new sequence with timestamp (10s @ 30fps)
3. Creates CineCameraActor at (0, -500, 200)
4. Creates BP_ThirdPersonCharacter at (0, 0, 88)
5. Adds both to sequence with proper tracks
6. Saves and opens in Sequencer

## View Logs

```powershell
cd "C:\RemoteProjects\reference\unreal\direct"
python view_unreal_log.py 50
```

Logs are saved to: `scene_setup.log`

## Files

- **unreal_setup_complete_scene.py** - Main scene creation script (pure Unreal Python)
- **unreal_connection.py** - Remote Control API connection module
- **view_unreal_log.py** - Log viewer utility
- **UNREAL_PYTHON_EXTENSION_GUIDE.md** - Detailed VS Code extension guide
- **scene_setup.log** - Execution log file (created after first run)
