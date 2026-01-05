// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "AAANKPoseBlueprintLibrary.generated.h"

// Forward declarations for PoseSearch
class UPoseSearchDatabase;
class UAnimSequence;


/**
 * Blueprint Function Library for AAANKPose Plugin
 */
UCLASS()
class AAANKPOSE_API UAAANKPoseBlueprintLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/** Returns "Hello World" from the AAANKPose plugin */
	UFUNCTION(BlueprintCallable, Category = "AAANKPose")
	static FString GetHelloWorld();

	// ========================================================================
	// PoseSearch Database Functions
	// ========================================================================

	/** Add an animation sequence to a PoseSearch database */
	UFUNCTION(BlueprintCallable, Category = "PoseSearch|Python")
	static bool AddAnimationToDatabase(
		UPoseSearchDatabase* Database,
		UAnimSequence* AnimSequence
	);

	/** Add multiple animation sequences to a PoseSearch database */
	UFUNCTION(BlueprintCallable, Category = "PoseSearch|Python")
	static int32 AddAnimationsToDatabase(
		UPoseSearchDatabase* Database,
		const TArray<UAnimSequence*>& AnimSequences
	);

	/** Build/rebuild the PoseSearch database index */
	UFUNCTION(BlueprintCallable, Category = "PoseSearch|Python")
	static bool BuildDatabase(UPoseSearchDatabase* Database);

	/** Get the number of animation assets in the database */
	UFUNCTION(BlueprintCallable, Category = "PoseSearch|Python")
	static int32 GetAnimationCount(UPoseSearchDatabase* Database);

	/** Clear all animations from the database */
	UFUNCTION(BlueprintCallable, Category = "PoseSearch|Python")
	static bool ClearDatabase(UPoseSearchDatabase* Database);

	/** Get information about the database */
	UFUNCTION(BlueprintCallable, Category = "PoseSearch|Python")
	static FString GetDatabaseInfo(UPoseSearchDatabase* Database);
};
