# C++ Plugin - Quick Start

## 🚀 Installation Steps

### 1. Create Plugin Folder
```
C:\UnrealProjects\ThirdPerson\Plugins\PoseSearchPythonExtensions\
```

### 2. Copy Files

Copy from `plugin_files/` to the plugin folder:

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

### 3. Generate Project Files
1. Close Unreal Editor
2. Right-click `ThirdPerson.uproject`
3. Select "Generate Visual Studio project files"

### 4. Compile
1. Open `ThirdPerson.sln`
2. Build configuration: "Development Editor"
3. Build the solution

### 5. Enable Plugin
1. Open Unreal Editor
2. Edit → Plugins
3. Search "PoseSearch Python"
4. Enable and restart

### 6. Test
```bash
python run_remote.py test_cpp_plugin.py
```

---

**See `CPP_PLUGIN_GUIDE.md` for detailed instructions**
