# AAANKPose Plugin - Testing Guide

## What Was Added

The AAANKPose plugin now has a simple "Hello World" function that can be called from both C++ and Blueprints.

### Files Modified/Created:

1. **Plugin Core Files:**
   - `Plugins/AAANKPose/Source/AAANKPose/Public/AAANKPose.h` - Added `HelloWorld()` function
   - `Plugins/AAANKPose/Source/AAANKPose/Private/AAANKPose.cpp` - Implemented `HelloWorld()` function
   
2. **Blueprint Support:**
   - `Plugins/AAANKPose/Source/AAANKPose/Public/AAANKPoseBlueprintLibrary.h` - Blueprint callable functions
   - `Plugins/AAANKPose/Source/AAANKPose/Private/AAANKPoseBlueprintLibrary.cpp` - Implementation

3. **Test Implementation:**
   - `Source/ThirdPerson5/ThirdPerson5Character.h` - Added BeginPlay override
   - `Source/ThirdPerson5/ThirdPerson5Character.cpp` - Test code that calls the plugin
   - `Source/ThirdPerson5/ThirdPerson5.Build.cs` - Added plugin dependency
   - `ThirdPerson5.uproject` - Enabled the plugin

## How to Test

### Method 1: Automatic Test (Already Implemented)

1. **Right-click** on `ThirdPerson5.uproject` and select "Generate Visual Studio project files"
2. **Open** the solution in Visual Studio or your IDE
3. **Build** the project (Build > Build Solution)
4. **Launch** the game in Unreal Editor
5. **Play** the game (PIE - Play In Editor)
6. **Look for** the yellow text on screen that says: "AAANKPose Plugin says: Hello World"
7. **Check** the Output Log window for the log message

### Method 2: C++ Manual Call

From any C++ file in your project:

```cpp
#include "AAANKPose.h"

FString message = FAAANKPoseModule::HelloWorld();
UE_LOG(LogTemp, Log, TEXT("Plugin returned: %s"), *message);
```

### Method 3: Blueprint

1. Open any Blueprint (like the Character Blueprint)
2. Right-click in the Event Graph
3. Search for "Get Hello World"
4. You'll find the function under "AAANKPose" category
5. Connect it to an event (like BeginPlay)
6. Use the return value to print to screen or log

Example Blueprint nodes:
```
Event BeginPlay -> Get Hello World -> Print String
```

### Method 4: Console Command Test

You can also create a console command. Add this to your Character C++ file:

```cpp
// In your character's BeginPlay or anywhere
if (GEngine)
{
    FString HelloMsg = FAAANKPoseModule::HelloWorld();
    GEngine->AddOnScreenDebugMessage(-1, 5.0f, FColor::Green, HelloMsg);
}
```

## Expected Output

- **On Screen:** Yellow text displaying "AAANKPose Plugin says: Hello World"
- **In Log:** `LogTemplateCharacter: AAANKPose Plugin says: Hello World`
- **From Blueprint:** String value "Hello World"
- **From C++:** FString containing "Hello World"

## Troubleshooting

### Plugin Not Found Error
- Make sure the plugin is enabled in Project Settings > Plugins
- Rebuild the project from Visual Studio
- Regenerate project files

### Linker Errors
- Verify `AAANKPose` is in the `PublicDependencyModuleNames` in `ThirdPerson5.Build.cs`
- Clean and rebuild the solution

### No Message Appears
- Check that you're using a Character blueprint derived from `ThirdPerson5Character`
- Verify the Output Log is open (Window > Developer Tools > Output Log)
- Make sure you're in Play mode (PIE)

## Next Steps

You can expand the plugin by:
- Adding more functions to the module
- Creating gameplay components
- Adding Blueprint nodes for specific functionality
- Implementing pose-related features (based on your plugin name)
