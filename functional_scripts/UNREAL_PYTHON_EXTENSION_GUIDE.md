# Unreal Engine Python Extension - Usage Guide

## Extension Features

The **Unreal Engine Python** extension (`nilssoderman.ue-python`) provides several powerful features for working with Unreal Engine Python scripts in VS Code.

## Key Features

### 1. Execute Code Directly in Unreal
**Command**: `Unreal Python: Execute`  
**Keyboard Shortcut**: `Ctrl+Enter`

- Select Python code in VS Code and press `Ctrl+Enter` to execute it directly in Unreal Engine
- If nothing is selected, the entire file will be executed
- Much faster than our current `run_add_mannequin.py` approach!

**How to use with our scripts**:
1. Open `unreal_add_mannequin_to_sequence.py` in VS Code
2. Make sure Unreal Engine is running with Remote Control enabled
3. Select all code (Ctrl+A) or specific code block
4. Press `Ctrl+Enter`
5. Code executes directly in Unreal!

### 2. Code Completion (IntelliSense)
**Command**: `Unreal Python: Setup code completion`

- Generates autocomplete stubs for the `unreal` module based on your current Unreal project
- Provides IntelliSense for all Unreal Python APIs
- Shows function signatures, parameters, and documentation

**How to setup**:
1. Open Command Palette (`Ctrl+Shift+P`)
2. Run: `Unreal Python: Setup code completion`
3. Extension generates stubs from your running Unreal instance
4. Now you get autocomplete for `unreal.EditorAssetLibrary`, etc.

### 3. Debugging Support
**Command**: `Unreal Python: Attach`

- Attach VS Code debugger to Unreal Engine
- Set breakpoints in Python code
- Step through code execution
- Inspect variables in real-time
- Full debugging capabilities!

**How to debug**:
1. Open your Python script
2. Set breakpoints (click left margin or press F9)
3. Run: `Unreal Python: Attach`
4. Execute your script in Unreal
5. Debugger stops at breakpoints

### 4. Browse Documentation
**Command**: `Unreal Python: Open Documentation`

- Browse Unreal Engine Python documentation inside VS Code
- Documentation generated on-the-fly from your running Unreal instance
- Always up-to-date with your Unreal version
- Includes custom C++ functions exposed to Python

## Prerequisites

The extension requires **Remote Execution** to be enabled in Unreal Engine. We already have this configured!

Our current setup in `DefaultEngine.ini`:
```ini
[RemoteControl]
bRestrictServerAccess=false
+RemoteControlWebInterfaceAllowedObjects=/Script/PythonScriptPlugin.Default__PythonScriptLibrary
```

## Comparing Approaches

### Current Approach (Manual)
```bash
# Run from PowerShell
python run_add_mannequin.py
```
- Requires separate runner script
- Uses `execute_python_file()` method
- Good for automation/CI

### With Extension (Interactive)
```
1. Open unreal_add_mannequin_to_sequence.py
2. Press Ctrl+Enter
```
- Direct execution
- No runner script needed
- Better for development/testing
- Can execute partial code snippets

## Recommended Workflow

1. **Development Phase**: Use extension's `Ctrl+Enter` for quick iteration
2. **Testing**: Use extension's debugger to troubleshoot
3. **Automation**: Use our `run_add_mannequin.py` for scripts/CI

## Commands Available

Open Command Palette (`Ctrl+Shift+P`) and type "Unreal Python" to see:
- `Unreal Python: Execute` - Execute selected/all code
- `Unreal Python: Setup code completion` - Generate IntelliSense stubs
- `Unreal Python: Attach` - Attach debugger
- `Unreal Python: Open Documentation` - Browse Python API docs
- `Unreal Python: Detach` - Detach debugger
- More commands available...

## Tips

1. **Quick Execution**: Select a code block and `Ctrl+Enter` to test small snippets
2. **Full File**: Press `Ctrl+A` then `Ctrl+Enter` to run entire file
3. **Debugging**: Add `breakpoint()` in code or set breakpoints in VS Code
4. **Documentation**: Hover over Unreal functions after setting up code completion

## Next Steps

1. Try executing `unreal_add_mannequin_to_sequence.py` directly with `Ctrl+Enter`
2. Setup code completion for IntelliSense
3. Try debugging with breakpoints
4. Browse Unreal Python documentation

This extension dramatically improves the development experience compared to our manual approach!
