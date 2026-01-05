# AAANKPose Plugin

A simple Unreal Engine plugin that provides "Hello World" functionality.

## Features

- C++ function to return "Hello World" message
- Blueprint-callable function library
- Compatible with Unreal Engine 5.7

## Installation

### Method 1: Per-Project Installation (Recommended)

1. Copy the entire `AAANKPose` folder to your project's `Plugins` directory:
   ```
   YourProject/Plugins/AAANKPose/
   ```

2. If your project doesn't have a `Plugins` folder, create one in the root directory.

3. Add the plugin to your project's `.uproject` file (or use the Plugins window in the editor):
   ```json
   "Plugins": [
       {
           "Name": "AAANKPose",
           "Enabled": true
       }
   ]
   ```

4. Add the plugin as a dependency in your module's `.Build.cs` file:
   ```csharp
   PublicDependencyModuleNames.AddRange(new string[] {
       "Core",
       "CoreUObject",
       "Engine",
       "AAANKPose"  // Add this line
   });
   ```

5. Right-click your `.uproject` file and select **"Generate Visual Studio project files"**

6. Open the solution and rebuild your project

### Method 2: Engine-Wide Installation

1. Copy the entire `AAANKPose` folder to your Unreal Engine's plugins directory:
   ```
   C:\Program Files\Epic Games\UE_5.7\Engine\Plugins\AAANKPose\
   ```
   
2. The plugin will now be available to all projects using this engine version

3. Enable it in your project via **Edit ? Plugins** in the Unreal Editor

## Usage

### From C++

```cpp
#include "AAANKPose.h"

// Call the static function
FString message = FAAANKPoseModule::HelloWorld();
UE_LOG(LogTemp, Log, TEXT("Plugin says: %s"), *message);
```

### From Blueprint

1. In any Blueprint, right-click in the Event Graph
2. Search for **"Get Hello World"**
3. You'll find it under the **AAANKPose** category
4. Connect it to your logic (e.g., Print String)

Example:
```
Event BeginPlay ? Get Hello World ? Print String
```

## Requirements

- Unreal Engine 5.7 (may work with other versions)
- Visual Studio 2022 or compatible C++ compiler

## Plugin Structure

```
AAANKPose/
??? AAANKPose.uplugin          # Plugin descriptor
??? Source/
?   ??? AAANKPose/
?       ??? AAANKPose.Build.cs # Build configuration
?       ??? Public/
?       ?   ??? AAANKPose.h    # Main module header
?       ?   ??? AAANKPoseBlueprintLibrary.h  # Blueprint functions
?       ??? Private/
?           ??? AAANKPose.cpp  # Main module implementation
?           ??? AAANKPoseBlueprintLibrary.cpp # Blueprint implementation
??? Resources/
    ??? Icon128.png            # Plugin icon (if present)
```

## API Reference

### C++ API

#### FAAANKPoseModule

**`static FString HelloWorld()`**
- Returns: `FString` containing "Hello World"
- Description: Simple function that returns a hello world message

### Blueprint API

#### UAAANKPoseBlueprintLibrary

**`Get Hello World`**
- Category: AAANKPose
- Returns: String containing "Hello World"
- Description: Blueprint-callable function to get hello world message

## License

[Add your license information here]

## Author

[Add your information here]

## Version History

- **1.0.0** - Initial release with Hello World functionality

## Support

For issues or questions, please [add contact information or repository link]
