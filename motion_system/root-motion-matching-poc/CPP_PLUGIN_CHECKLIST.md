# C++ Plugin Installation Checklist

**Follow these steps in order. Check each box as you complete it.**

---

## ☑️ Pre-Installation

- [ ] **Close Unreal Editor** (must be closed!)
- [ ] **Visual Studio 2022 installed** with "Game development with C++"
- [ ] **Project location**: `C:\UnrealProjects\ThirdPerson`
- [ ] **Plugin files ready**: `C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\plugin_files\`

---

## ☑️ Step 1: Create Plugin Folder (2 minutes)

- [ ] Create folder: `C:\UnrealProjects\ThirdPerson\Plugins\`
- [ ] Create folder: `C:\UnrealProjects\ThirdPerson\Plugins\PoseSearchPythonExtensions\`
- [ ] Create folder: `C:\UnrealProjects\ThirdPerson\Plugins\PoseSearchPythonExtensions\Source\`
- [ ] Create folder: `C:\UnrealProjects\ThirdPerson\Plugins\PoseSearchPythonExtensions\Source\PoseSearchPythonExtensions\`
- [ ] Create folder: `C:\UnrealProjects\ThirdPerson\Plugins\PoseSearchPythonExtensions\Source\PoseSearchPythonExtensions\Public\`
- [ ] Create folder: `C:\UnrealProjects\ThirdPerson\Plugins\PoseSearchPythonExtensions\Source\PoseSearchPythonExtensions\Private\`

---

## ☑️ Step 2: Copy Files (3 minutes)

### Root Files:
- [ ] Copy `PoseSearchPythonExtensions.uplugin` to:
  ```
  C:\UnrealProjects\ThirdPerson\Plugins\PoseSearchPythonExtensions\
  ```

### Source Files:
- [ ] Copy `PoseSearchPythonExtensions.Build.cs` to:
  ```
  C:\UnrealProjects\ThirdPerson\Plugins\PoseSearchPythonExtensions\Source\PoseSearchPythonExtensions\
  ```

### Public Headers:
- [ ] Copy `PoseSearchPythonExtensions.h` to:
  ```
  C:\UnrealProjects\ThirdPerson\Plugins\PoseSearchPythonExtensions\Source\PoseSearchPythonExtensions\Public\
  ```

- [ ] Copy `PoseSearchPythonExtensionsLibrary.h` to:
  ```
  C:\UnrealProjects\ThirdPerson\Plugins\PoseSearchPythonExtensions\Source\PoseSearchPythonExtensions\Public\
  ```

### Private Implementation:
- [ ] Copy `PoseSearchPythonExtensions.cpp` to:
  ```
  C:\UnrealProjects\ThirdPerson\Plugins\PoseSearchPythonExtensions\Source\PoseSearchPythonExtensions\Private\
  ```

- [ ] Copy `PoseSearchPythonExtensionsLibrary.cpp` to:
  ```
  C:\UnrealProjects\ThirdPerson\Plugins\PoseSearchPythonExtensions\Source\PoseSearchPythonExtensions\Private\
  ```

---

## ☑️ Step 3: Generate Project Files (2 minutes)

- [ ] **Verify Unreal Editor is closed**
- [ ] Navigate to: `C:\UnrealProjects\ThirdPerson\`
- [ ] Right-click on `ThirdPerson.uproject`
- [ ] Select **"Generate Visual Studio project files"**
- [ ] Wait for completion (green checkmark appears)
- [ ] Verify `ThirdPerson.sln` was updated (check timestamp)

---

## ☑️ Step 4: Compile Plugin (5-10 minutes)

### Open Solution:
- [ ] Double-click `C:\UnrealProjects\ThirdPerson\ThirdPerson.sln`
- [ ] Wait for Visual Studio to load

### Configure Build:
- [ ] Set configuration dropdown to **"Development Editor"**
- [ ] Set platform dropdown to **"Win64"**

### Build:
- [ ] Menu: **Build → Build Solution** (or press Ctrl+Shift+B)
- [ ] Wait for compilation (watch Output window)
- [ ] **Verify**: Output shows "Build succeeded" (no errors)
- [ ] **Check**: Look for "PoseSearchPythonExtensions" in build output

### If Errors Occur:
- [ ] Read error messages in Error List window
- [ ] Common fixes:
  - Clean solution (Build → Clean Solution)
  - Rebuild (Build → Rebuild Solution)
  - Check file paths are correct
  - Verify all files were copied

---

## ☑️ Step 5: Enable Plugin (3 minutes)

### Open Editor:
- [ ] Launch Unreal Editor
- [ ] Open `ThirdPerson` project
- [ ] Wait for project to load

### Enable Plugin:
- [ ] Menu: **Edit → Plugins**
- [ ] In search box, type: **"PoseSearch Python"**
- [ ] Find **"PoseSearch Python Extensions"** in results
- [ ] **Check the checkbox** to enable it
- [ ] Click **"Restart Now"** button
- [ ] Wait for editor to restart

### Verify Plugin Loaded:
- [ ] After restart, check Output Log
- [ ] Look for: `"PoseSearchPythonExtensions module has started"`
- [ ] If found, plugin is loaded! ✓

---

## ☑️ Step 6: Test Plugin (5 minutes)

### Run Test Script:
- [ ] Open terminal/PowerShell
- [ ] Navigate to: `C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\`
- [ ] Run: `python run_remote.py test_cpp_plugin.py`
- [ ] Wait for execution

### Expected Output:
- [ ] See: `"✓ Plugin library loaded"`
- [ ] See: `"✓ Database loaded"`
- [ ] See: `"✓ Add animation: True"`
- [ ] See: `"✓ Animation count (after): 1"` (or higher)
- [ ] See: `"✓ Build database: True"`
- [ ] See: `"✓ C++ PLUGIN TEST COMPLETE!"`

### If Test Fails:
- [ ] Check Unreal Output Log for errors
- [ ] Verify plugin is enabled (Edit → Plugins)
- [ ] Verify editor was restarted after enabling
- [ ] Check Python script path is correct

---

## ☑️ Step 7: Integration (5 minutes)

### Create Automation Script:
- [ ] Test adding all 123 animations
- [ ] Verify database builds successfully
- [ ] Check animation count matches expected

### Update Documentation:
- [ ] Note any issues encountered
- [ ] Document successful configuration
- [ ] Share with team if applicable

---

## 🎉 Success Criteria

You're done when ALL of these are true:

- ✅ Plugin compiles without errors
- ✅ Plugin appears in Edit → Plugins
- ✅ Test script runs successfully
- ✅ Can add animations from Python
- ✅ Can build database from Python
- ✅ Animation count increases correctly

---

## 🐛 Troubleshooting

### Compilation Fails
**Error**: "Cannot find PoseSearch module"
- **Fix**: Enable PoseSearch plugin in project settings

**Error**: "Unresolved external symbol"
- **Fix**: Clean and rebuild solution

### Plugin Not Found
**Error**: "Plugin not in list"
- **Fix**: Check .uplugin file is in correct location
- **Fix**: Regenerate project files

### Python Can't Find Library
**Error**: "PoseSearchPythonExtensionsLibrary not found"
- **Fix**: Ensure plugin is enabled
- **Fix**: Restart editor after enabling
- **Fix**: Check Output Log for module startup message

### Functions Don't Work
**Error**: "Function failed"
- **Fix**: Check Unreal Output Log for C++ errors
- **Fix**: Verify database and animations are valid
- **Fix**: Check UE version matches (5.7)

---

## 📞 Need Help?

If stuck:
1. Check Output Log in Unreal Editor
2. Check Error List in Visual Studio
3. Review `CPP_PLUGIN_GUIDE.md` for details
4. Check `plugin_files/README.md` for usage

---

**Current Step**: _____ of 7

**Estimated Time Remaining**: _____ minutes

**Notes**:
```
(Add any notes or issues here)
```
