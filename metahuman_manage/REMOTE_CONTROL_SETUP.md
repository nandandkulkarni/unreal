# Remote Control Setup for Unreal Engine

## Issue
`Object Default__PythonScriptLibrary cannot be accessed remotely`

This means the Remote Control plugin needs to be configured to allow Python execution.

## Quick Fix

### Step 1: Enable Remote Control Plugin
1. Open Unreal Engine
2. Go to: **Edit → Plugins**
3. Search for: **Remote Control**
4. Check the box to enable it
5. **Restart Unreal Engine**

### Step 2: Start WebControl Server
1. Open **Output Log**: `Window → Developer Tools → Output Log`
2. In the console at the bottom, type:
   ```
   WebControl.StartServer
   ```
3. Press Enter
4. You should see: `WebControl server started on port 30010`

### Step 3: Configure Python Remote Execution

**Option A: Manual Configuration (Recommended)**

1. Close Unreal Engine
2. Navigate to your project folder
3. Open: `Config\DefaultEngine.ini`
4. Add these lines at the end:

```ini
; Remote Control API Configuration
[RemoteControl]
bDeveloperMode=True
bRemoteExecution=True
bEnableRemotePythonExecution=True
+RemoteControlWebInterfaceAllowedObjects=/Script/PythonScriptPlugin.PythonScriptLibrary
```

5. Save the file
6. Restart Unreal Engine
7. Run `WebControl.StartServer` again

**Option B: Automated Configuration**

Run this script (from the parent directory):
```bash
py setup_remote_control.py
```

### Step 4: Verify Connection

Test the connection:
```bash
py unreal_connection.py
```

You should see:
```
✓ Connected to Unreal Engine!
✓ Python code executed successfully!
```

## After Setup is Complete

Run the MetaHuman setup:
```bash
py trigger_metahuman_setup.py --metahuman Pia
```

## Alternative: Run Directly in Unreal

If Remote Control setup is too complex, you can run the script directly in Unreal:

1. Open Unreal Engine
2. Go to: **Tools → Python → Execute Python Script**
3. Paste this command:
   ```python
   exec(open(r"c:\UnrealProjects\Coding\unreal\metahuman_manage\metahuman_animation_setup_auto.py").read())
   ```
4. Press Enter

## Troubleshooting

### "WebControl server already running"
- This is fine, it means the server is already started

### "Cannot connect to Unreal Engine"
- Make sure Unreal is running
- Make sure WebControl server is started
- Check firewall isn't blocking port 30010

### "Remote Control plugin not found"
- Update to Unreal Engine 5.0 or later
- The plugin is built-in for UE5+

### Still having issues?
Run the script directly in Unreal's Python console instead of using Remote Control.
