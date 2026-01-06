# Testing AAANKPose Plugin - Quick Guide

## 🚀 Quick Test

Run this command from the `root-motion-matching-poc` folder:

```bash
python run_remote.py test_aaankpose_plugin.py
```

## 📋 What to Look For

### ✅ Success Indicators:
- `✓ Found library class: ...` - Your plugin class is accessible
- `✓ Plugin manager accessible` - Plugin system working
- No Python errors

### ⚠️ If Plugin Not Found:

1. **Check Plugin is Enabled:**
   - Open Unreal Editor
   - Edit → Plugins
   - Search for "AAANKPose"
   - Ensure checkbox is checked
   - Click "Restart Now" if you just enabled it

2. **Check Plugin Compiled:**
   - Open Visual Studio
   - Build → Build Solution
   - Look for "Build succeeded"

3. **Check Plugin Structure:**
   Your plugin should have this structure:
   ```
   C:\UnrealProjects\ThirdPerson5\Plugins\AAANKPose\
   ├── AAANKPose.uplugin
   └── Source\AAANKPose\
       ├── AAANKPose.Build.cs
       ├── Public\
       │   ├── AAANKPose.h
       │   └── AAANKPoseLibrary.h  ← Your functions here
       └── Private\
           ├── AAANKPose.cpp
           └── AAANKPoseLibrary.cpp
   ```

## 🔍 Finding Your Function Names

To find what functions your plugin exposes, check your `.h` file:

Look for lines like:
```cpp
UFUNCTION(BlueprintCallable, Category = "...")
static FString YourFunctionName();
```

The function name after `static` is what you'll call from Python.

## 🧪 Testing Your "Hello World" Function

Once you know your function name, test it like this:

```python
import unreal

# If your library class is called UAAANKPoseLibrary
lib = unreal.AAANKPoseLibrary()

# Call your hello world function (replace with actual name)
result = lib.your_hello_world_function()
print(f"Result: {result}")
```

## 📝 Next Steps After Basic Test Works

1. **Add PoseSearch Functions** - Add the 6 PoseSearch functions to your library
2. **Update Build.cs** - Add PoseSearch dependency
3. **Recompile** - Build solution in Visual Studio
4. **Test PoseSearch** - Use the motion matching database

## 🔗 Reference Files

- **PoseSearch Library Header**: `plugin_files/PoseSearchPythonExtensionsLibrary.h`
- **PoseSearch Library Implementation**: `plugin_files/PoseSearchPythonExtensionsLibrary.cpp`
- **Build Configuration**: `plugin_files/PoseSearchPythonExtensions.Build.cs`

## 💡 Common Issues

**Issue**: "Module not found"
- **Fix**: Restart Unreal Editor after enabling plugin

**Issue**: "Class not found in Python"
- **Fix**: Ensure UFUNCTION has `BlueprintCallable` macro

**Issue**: "Compilation errors"
- **Fix**: Check all dependencies in .Build.cs file

---

**Need help?** Check `CPP_PLUGIN_GUIDE.md` for detailed C++ plugin development guide.
