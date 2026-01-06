# Test Plugin First - Recommended Workflow

## 🎯 **Why Test First?**

Great idea! Testing with a simple plugin first:
- ✅ Verifies the C++ → Python workflow works
- ✅ Confirms build process is correct
- ✅ Tests plugin enable/disable
- ✅ Much faster to compile (~2 min vs ~7 min)
- ✅ Easier to debug if something goes wrong

---

## 📝 **Simple Test Plugin Created**

I've created a minimal test plugin with 3 simple functions:

### **Location:**
```
C:\UnrealProjects\ThirdPerson\Plugins\TestPythonPlugin\
```

### **Functions:**
```python
lib = unreal.TestPythonLibrary()

# Test 1: Returns a greeting
greeting = lib.say_hello("Python")  
# Returns: "Hello from C++, Python!"

# Test 2: Adds two numbers
result = lib.add_numbers(42, 58)    
# Returns: 100

# Test 3: Gets current time
time = lib.get_current_time()       
# Returns: "2026-01-04 19:02:45"
```

---

## 🚀 **Test Workflow (10 minutes total):**

### **Step 1: Convert Project to C++** (2 min)
1. Open Unreal Editor
2. Open ThirdPerson project
3. Tools → New C++ Class
4. Select "Actor", name "MyActor"
5. Click "Create Class"
6. Wait for Visual Studio to open

### **Step 2: Build Solution** (2 min - faster!)
1. Configuration: "Development Editor"
2. Build → Build Solution (Ctrl+Shift+B)
3. Wait ~2 minutes (simple plugin compiles fast!)
4. Look for "Build succeeded"

### **Step 3: Enable Test Plugin** (1 min)
1. Close Visual Studio
2. Open Unreal Editor
3. Edit → Plugins
4. Search "Test Python"
5. Enable + Restart

### **Step 4: Test It** (1 min)
```bash
cd C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc
python run_remote.py test_simple_plugin.py
```

**Expected output:**
```
============================================================
Testing Simple C++ Plugin
============================================================
✓ Plugin library loaded successfully!

Test 1 - SayHello:
  Result: Hello from C++, Python!
  ✓ PASS

Test 2 - AddNumbers:
  42 + 58 = 100
  ✓ PASS (expected 100)

Test 3 - GetCurrentTime:
  Current time: 2026-01-04 19:02:45
  ✓ PASS

============================================================
✓ ALL TESTS PASSED!
============================================================

C++ to Python workflow is working!
You can now proceed with the PoseSearch plugin.
```

---

## ✅ **If Test Plugin Works:**

Then you know:
- ✓ C++ compilation works
- ✓ Plugin system works
- ✓ Python can call C++ functions
- ✓ Build configuration is correct

**Then proceed with PoseSearch plugin** - just enable it and rebuild!

---

## ❌ **If Test Plugin Fails:**

You can debug the simple plugin first:
- Easier to understand errors
- Faster iteration (2 min builds vs 7 min)
- Less complex code to troubleshoot

---

## 🎯 **Recommendation:**

**YES, do the test plugin first!** It's smart to:
1. Test with simple plugin (10 min)
2. Verify everything works
3. Then enable PoseSearch plugin
4. Rebuild (adds ~5 more minutes)

**Total time is the same**, but you have a checkpoint in the middle!

---

## 📂 **Files Created:**

```
C:\UnrealProjects\ThirdPerson\Plugins\TestPythonPlugin\
├── TestPythonPlugin.uplugin
└── Source\TestPythonPlugin\
    ├── TestPythonPlugin.Build.cs
    ├── Public\
    │   ├── TestPythonPlugin.h
    │   └── TestPythonLibrary.h
    └── Private\
        ├── TestPythonPlugin.cpp
        └── TestPythonLibrary.cpp

Test script:
C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\
└── test_simple_plugin.py
```

---

**Ready to start?** Follow the 4 steps above with the test plugin first! 🚀
