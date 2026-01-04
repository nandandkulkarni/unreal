#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "PoseSearchPythonExtensionsLibrary.generated.h"

// Forward declarations
class UPoseSearchDatabase;
class UAnimSequence;

/**
 * Blueprint Function Library to expose PoseSearch functions to Python
 * 
 * This library provides functions that are not accessible via Python's
 * standard API, specifically for manipulating PoseSearch databases.
 */
UCLASS()
class POSESEARCHPYTHONEXTENSIONS_API UPoseSearchPythonExtensionsLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    /**
     * Add an animation sequence to a PoseSearch database
     * @param Database - The PoseSearch database to modify
     * @param AnimSequence - The animation sequence to add
     * @return True if successful
     */
    UFUNCTION(BlueprintCallable, Category = "PoseSearch|Python")
    static bool AddAnimationToDatabase(
        UPoseSearchDatabase* Database,
        UAnimSequence* AnimSequence
    );

    /**
     * Add multiple animation sequences to a PoseSearch database
     * @param Database - The PoseSearch database to modify
     * @param AnimSequences - Array of animation sequences to add
     * @return Number of animations successfully added
     */
    UFUNCTION(BlueprintCallable, Category = "PoseSearch|Python")
    static int32 AddAnimationsToDatabase(
        UPoseSearchDatabase* Database,
        const TArray<UAnimSequence*>& AnimSequences
    );

    /**
     * Build/rebuild the PoseSearch database index
     * @param Database - The PoseSearch database to build
     * @return True if successful
     */
    UFUNCTION(BlueprintCallable, Category = "PoseSearch|Python")
    static bool BuildDatabase(UPoseSearchDatabase* Database);

    /**
     * Get the number of animation assets in the database
     * @param Database - The PoseSearch database
     * @return Number of animation assets
     */
    UFUNCTION(BlueprintCallable, Category = "PoseSearch|Python")
    static int32 GetAnimationCount(UPoseSearchDatabase* Database);

    /**
     * Clear all animations from the database
     * @param Database - The PoseSearch database to clear
     * @return True if successful
     */
    UFUNCTION(BlueprintCallable, Category = "PoseSearch|Python")
    static bool ClearDatabase(UPoseSearchDatabase* Database);

    /**
     * Get information about the database
     * @param Database - The PoseSearch database
     * @return String with database information
     */
    UFUNCTION(BlueprintCallable, Category = "PoseSearch|Python")
    static FString GetDatabaseInfo(UPoseSearchDatabase* Database);
};
