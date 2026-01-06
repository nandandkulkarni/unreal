# Adding PoseSearch Functions to AAANKPose Plugin

## 📍 Current Status
- ✅ Plugin created: `AAANKPose`
- ✅ Location: `C:\UnrealProjects\ThirdPerson5\Plugins\AAANKPose`
- ✅ "Hello World" function working
- ⏳ **Next**: Add PoseSearch database functions

---

## 🎯 Goal
Add 6 functions to your plugin to enable full Python automation of Motion Matching database:

1. `AddAnimationToDatabase()` - Add single animation
2. `AddAnimationsToDatabase()` - Batch add all 123 animations
3. `BuildDatabase()` - Build database index
4. `GetAnimationCount()` - Get animation count
5. `ClearDatabase()` - Clear all animations
6. `GetDatabaseInfo()` - Get database info

---

## 📝 Step-by-Step Instructions

### Step 1: Update Build Configuration (2 minutes)

**File**: `C:\UnrealProjects\ThirdPerson5\Plugins\AAANKPose\Source\AAANKPose\AAANKPose.Build.cs`

Add these dependencies:

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "UnrealEd",
    "PoseSearch",           // ← ADD THIS
    "PythonScriptPlugin"    // ← ADD THIS (if not already there)
});
```

### Step 2: Update Library Header (5 minutes)

**File**: `C:\UnrealProjects\ThirdPerson5\Plugins\AAANKPose\Source\AAANKPose\Public\AAANKPoseLibrary.h`

Add these includes at the top:
```cpp
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "AAANKPoseLibrary.generated.h"

// Forward declarations
class UPoseSearchDatabase;
class UAnimSequence;
```

Add these function declarations in your UCLASS:
```cpp
UCLASS()
class AAANKPOSE_API UAAANKPoseLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    // Your existing Hello World function...
    
    // NEW: PoseSearch functions
    UFUNCTION(BlueprintCallable, Category = "PoseSearch|Python")
    static bool AddAnimationToDatabase(
        UPoseSearchDatabase* Database,
        UAnimSequence* AnimSequence
    );

    UFUNCTION(BlueprintCallable, Category = "PoseSearch|Python")
    static int32 AddAnimationsToDatabase(
        UPoseSearchDatabase* Database,
        const TArray<UAnimSequence*>& AnimSequences
    );

    UFUNCTION(BlueprintCallable, Category = "PoseSearch|Python")
    static bool BuildDatabase(UPoseSearchDatabase* Database);

    UFUNCTION(BlueprintCallable, Category = "PoseSearch|Python")
    static int32 GetAnimationCount(UPoseSearchDatabase* Database);

    UFUNCTION(BlueprintCallable, Category = "PoseSearch|Python")
    static bool ClearDatabase(UPoseSearchDatabase* Database);

    UFUNCTION(BlueprintCallable, Category = "PoseSearch|Python")
    static FString GetDatabaseInfo(UPoseSearchDatabase* Database);
};
```

### Step 3: Update Library Implementation (10 minutes)

**File**: `C:\UnrealProjects\ThirdPerson5\Plugins\AAANKPose\Source\AAANKPose\Private\AAANKPoseLibrary.cpp`

Add these includes:
```cpp
#include "AAANKPoseLibrary.h"
#include "PoseSearch/PoseSearchDatabase.h"
#include "PoseSearch/PoseSearchSchema.h"
#include "Animation/AnimSequence.h"
#include "Misc/ScopedSlowTask.h"
#include "UObject/SavePackage.h"
```

**COPY THE COMPLETE IMPLEMENTATION** from:
`C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\plugin_files\PoseSearchPythonExtensionsLibrary.cpp`

Copy functions:
- `AddAnimationToDatabase()` (lines 9-43)
- `AddAnimationsToDatabase()` (lines 45-92)
- `BuildDatabase()` (lines 94-140)
- `GetAnimationCount()` (lines 142-151)
- `ClearDatabase()` (lines 153-198)
- `GetDatabaseInfo()` (lines 200-214)

### Step 4: Compile Plugin (5 minutes)

1. **Close Unreal Editor** (important!)
2. Open `C:\UnrealProjects\ThirdPerson5\ThirdPerson5.sln` in Visual Studio
3. Set configuration to **"Development Editor"**
4. **Build → Build Solution** (Ctrl+Shift+B)
5. Wait for "Build succeeded"

### Step 5: Test Plugin (2 minutes)

1. **Open Unreal Editor**
2. Open ThirdPerson5 project
3. Run test script:

```bash
cd C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc
python run_remote.py test_aaankpose_posesearch.py
```

---

## 🧪 Test Script

I'll create `test_aaankpose_posesearch.py` for you to test the new functions.

---

## 📊 Expected Results

After completing these steps:

```
✓ Plugin compiles without errors
✓ All 6 PoseSearch functions accessible from Python
✓ Can add animations to database
✓ Can build database
✓ 100% automation achieved!
```

---

## 🐛 Troubleshooting

**Compilation Error: "Cannot find PoseSearch"**
- Fix: Ensure PoseSearch plugin is enabled in project (Edit → Plugins)

**Compilation Error: "FPoseSearchDatabaseAnimationAsset not found"**
- Fix: Check you're using UE 5.7+ (this struct was added in 5.7)

**Python Error: "Function not found"**
- Fix: Ensure UFUNCTION has `BlueprintCallable` macro
- Fix: Restart editor after compilation

---

## 📁 Reference Files

All implementation code is ready in:
- `plugin_files/PoseSearchPythonExtensionsLibrary.h` - Header reference
- `plugin_files/PoseSearchPythonExtensionsLibrary.cpp` - Implementation reference

---

**Ready to proceed?** Follow the steps above, and let me know if you hit any issues!
