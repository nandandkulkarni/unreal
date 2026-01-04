# C++ Plugin Files - Ready to Install

## 📦 What's Included

All files needed for the PoseSearch Python Extensions plugin:

### Plugin Files:
1. `PoseSearchPythonExtensions.uplugin` - Plugin descriptor
2. `PoseSearchPythonExtensions.Build.cs` - Build configuration
3. `PoseSearchPythonExtensions.h` - Module header
4. `PoseSearchPythonExtensions.cpp` - Module implementation
5. `PoseSearchPythonExtensionsLibrary.h` - Function library header
6. `PoseSearchPythonExtensionsLibrary.cpp` - Function library implementation

### Documentation:
7. `QUICK_START.md` - Installation guide
8. `README.md` - This file

---

## 🚀 Installation (5 Steps)

### Step 1: Create Plugin Folder
```
C:\UnrealProjects\ThirdPerson\Plugins\PoseSearchPythonExtensions\
```

### Step 2: Copy Files

Create this structure:
```
PoseSearchPythonExtensions/
├── PoseSearchPythonExtensions.uplugin
└── Source/
    └── PoseSearchPythonExtensions/
        ├── PoseSearchPythonExtensions.Build.cs
        ├── Private/
        │   ├── PoseSearchPythonExtensions.cpp
        │   └── PoseSearchPythonExtensionsLibrary.cpp
        └── Public/
            ├── PoseSearchPythonExtensions.h
            └── PoseSearchPythonExtensionsLibrary.h
```

Copy files from this folder to match the structure above.

### Step 3: Generate Project Files
1. **Close Unreal Editor** (important!)
2. Right-click `ThirdPerson.uproject`
3. Select "Generate Visual Studio project files"
4. Wait for completion

### Step 4: Compile
1. Open `ThirdPerson.sln` in Visual Studio
2. Set configuration to **"Development Editor"**
3. Build → Build Solution (or Ctrl+Shift+B)
4. Wait for compilation (~2-5 minutes)

### Step 5: Enable Plugin
1. Open Unreal Editor
2. Edit → Plugins
3. Search "PoseSearch Python"
4. Enable checkbox
5. Restart editor

---

## ✅ Verify Installation

Run this Python script:
```python
import unreal
lib = unreal.PoseSearchPythonExtensionsLibrary()
print("✓ Plugin loaded successfully!")
```

---

## 🎯 Usage from Python

```python
import unreal

# Load library
lib = unreal.PoseSearchPythonExtensionsLibrary()

# Load database
database = unreal.load_object(None, "/Game/MotionMatching/MannyMotionDatabase")

# Load animation
anim = unreal.load_object(None, "/Game/Path/To/Animation")

# Add animation
lib.add_animation_to_database(database, anim)

# Build database
lib.build_database(database)

# Get count
count = lib.get_animation_count(database)
print(f"Animations: {count}")
```

---

## 🔧 Functions Available

| Function | Description |
|----------|-------------|
| `add_animation_to_database(db, anim)` | Add single animation |
| `add_animations_to_database(db, anims)` | Add multiple animations |
| `build_database(db)` | Build/rebuild database index |
| `get_animation_count(db)` | Get animation count |
| `clear_database(db)` | Clear all animations |
| `get_database_info(db)` | Get database information |

---

## 📝 Notes

- **UE Version**: Designed for UE 5.7
- **Type**: Editor-only plugin
- **Dependencies**: PoseSearch, PythonScriptPlugin
- **Platform**: Windows (can be adapted for other platforms)

---

## 🐛 Troubleshooting

### "Cannot find PoseSearch module"
- Ensure PoseSearch plugin is enabled in your project

### "Unresolved external symbol"
- Clean solution and rebuild
- Check that all dependencies are listed in .Build.cs

### "Plugin not found in Python"
- Ensure plugin is enabled in Edit → Plugins
- Restart Unreal Editor after enabling

### Compilation errors
- Check UE version matches (5.7)
- Verify Visual Studio is properly configured
- Check Output Log for specific errors

---

## 📚 More Info

See parent directory for:
- `CPP_PLUGIN_GUIDE.md` - Detailed walkthrough
- `test_cpp_plugin.py` - Test script
- Full documentation set

---

**Ready to install? Follow the 5 steps above!**
