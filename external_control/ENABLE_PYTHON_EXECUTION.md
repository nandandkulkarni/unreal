# Enable ExecutePythonCommand in Remote Control

The error `"Object Default__PythonScriptLibrary cannot be accessed remotely"` means we need to whitelist it.

## Option 1: Via Remote Control Preset (Recommended)

1. In Unreal Editor, go to **Window** → **Remote Control**
2. Create or open a Remote Control Preset
3. Click **+ Add** → **Expose Actor** or **Expose Function**
4. Add **PythonScriptLibrary** → **ExecutePythonCommand**
5. Save the preset

## Option 2: Via Config File (Faster)

Edit: `CinematicPipeline/Config/DefaultEngine.ini`

Add these lines:

```ini
[RemoteControl]
+RemoteControlAllowListClasses=/Script/PythonScriptPlugin.PythonScriptLibrary
```

Or add to the existing RemoteControl section if it exists.

## Option 3: Enable Unrestricted Access (Development Only!)

In **DefaultEngine.ini**:

```ini
[RemoteControl]
bRestrictServerAccess=false
```

**WARNING**: This disables all security! Only use in development.

## After making changes:

1. Save the config file
2. **Restart Unreal Editor**
3. Run the test script again:
   ```
   python C:\U\CinematicPipeline_Scripts\external_control\test_execute_python_command.py
   ```

## Alternative: Use Remote Control Web App

If configs don't work, expose ExecutePythonCommand through the Web UI:

1. In Unreal, open **Window** → **Remote Control API**
2. The web interface should show at http://localhost:7001
3. Manually expose the PythonScriptLibrary functions

---

**Which method would you like to try first?**
