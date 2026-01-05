// Copyright Epic Games, Inc. All Rights Reserved.

#include "AAANKPoseBlueprintLibrary.h"
#include "AAANKPose.h"
#include "PoseSearch/PoseSearchDatabase.h"
#include "PoseSearch/PoseSearchSchema.h"
#include "Animation/AnimSequence.h"
#include "Misc/ScopedSlowTask.h"
#include "UObject/SavePackage.h"


FString UAAANKPoseBlueprintLibrary::GetHelloWorld()
{
	return FAAANKPoseModule::HelloWorld();
}

// ============================================================================
// PoseSearch Database Function Implementations
// ============================================================================

bool UAAANKPoseBlueprintLibrary::AddAnimationToDatabase(
	UPoseSearchDatabase* Database,
	UAnimSequence* AnimSequence)
{
	if (!Database || !AnimSequence)
	{
		UE_LOG(LogTemp, Error, TEXT("AddAnimationToDatabase: Invalid database or animation"));
		return false;
	}

	UE_LOG(LogTemp, Log, TEXT("Adding animation '%s' to database '%s'"), 
		*AnimSequence->GetName(), *Database->GetName());

#if WITH_EDITOR
	// Mark database for modification
	Database->Modify();

	// Create FPoseSearchDatabaseAnimationAsset
	FPoseSearchDatabaseAnimationAsset AnimAsset;
	AnimAsset.AnimAsset = AnimSequence;
	
	// Add to database using the official API
	Database->AddAnimationAsset(AnimAsset);
	
	// Mark package as dirty
	Database->MarkPackageDirty();
	
	// Trigger property change notification to rebuild index
	FPropertyChangedEvent PropertyEvent(nullptr);
	Database->PostEditChangeProperty(PropertyEvent);

	UE_LOG(LogTemp, Log, TEXT("Successfully added animation to database"));
	
	return true;
#else
	UE_LOG(LogTemp, Warning, TEXT("AddAnimationToDatabase is only available in editor builds"));
	return false;
#endif
}

int32 UAAANKPoseBlueprintLibrary::AddAnimationsToDatabase(
	UPoseSearchDatabase* Database,
	const TArray<UAnimSequence*>& AnimSequences)
{
	if (!Database)
	{
		UE_LOG(LogTemp, Error, TEXT("AddAnimationsToDatabase: Invalid database"));
		return 0;
	}

#if WITH_EDITOR
	FScopedSlowTask Progress(AnimSequences.Num(), 
		FText::FromString(TEXT("Adding animations to database")));
	Progress.MakeDialog();

	int32 AddedCount = 0;
	
	// Mark for modification once
	Database->Modify();
	
	for (UAnimSequence* Anim : AnimSequences)
	{
		Progress.EnterProgressFrame(1.0f);
		
		if (Anim)
		{
			FPoseSearchDatabaseAnimationAsset AnimAsset;
			AnimAsset.AnimAsset = Anim;
			
			Database->AddAnimationAsset(AnimAsset);
			AddedCount++;
			
			UE_LOG(LogTemp, Log, TEXT("Added animation %d/%d: %s"), 
				AddedCount, AnimSequences.Num(), *Anim->GetName());
		}
	}

	// Mark package as dirty
	Database->MarkPackageDirty();
	
	// Trigger rebuild
	FPropertyChangedEvent PropertyEvent(nullptr);
	Database->PostEditChangeProperty(PropertyEvent);

	UE_LOG(LogTemp, Log, TEXT("Added %d/%d animations to database '%s'"), 
		AddedCount, AnimSequences.Num(), *Database->GetName());

	return AddedCount;
#else
	UE_LOG(LogTemp, Warning, TEXT("AddAnimationsToDatabase is only available in editor builds"));
	return 0;
#endif
}

bool UAAANKPoseBlueprintLibrary::BuildDatabase(UPoseSearchDatabase* Database)
{
	if (!Database)
	{
		UE_LOG(LogTemp, Error, TEXT("BuildDatabase: Invalid database"));
		return false;
	}

#if WITH_EDITOR
	UE_LOG(LogTemp, Log, TEXT("Building database '%s'"), *Database->GetName());

	FScopedSlowTask Progress(1.0f, FText::FromString(TEXT("Building PoseSearch database")));
	Progress.MakeDialog();

	// Mark for modification
	Database->Modify();
	
	// Trigger a rebuild by simulating a property change
	FPropertyChangedEvent PropertyEvent(nullptr);
	Database->PostEditChangeProperty(PropertyEvent);
	
	// Mark package as dirty
	Database->MarkPackageDirty();
	
	UE_LOG(LogTemp, Log, TEXT("Database rebuilt successfully"));
	return true;
#else
	UE_LOG(LogTemp, Warning, TEXT("BuildDatabase is only available in editor builds"));
	return false;
#endif
}

int32 UAAANKPoseBlueprintLibrary::GetAnimationCount(UPoseSearchDatabase* Database)
{
	if (!Database)
	{
		return 0;
	}

	return Database->GetNumAnimationAssets();
}

bool UAAANKPoseBlueprintLibrary::ClearDatabase(UPoseSearchDatabase* Database)
{
	if (!Database)
	{
		UE_LOG(LogTemp, Error, TEXT("ClearDatabase: Invalid database"));
		return false;
	}

#if WITH_EDITOR
	UE_LOG(LogTemp, Log, TEXT("Clearing database '%s'"), *Database->GetName());

	Database->Modify();
	
	// Get the AnimationAssets property
	FName AnimationAssetsPropertyName = TEXT("AnimationAssets");
	FProperty* AnimAssetsProperty = Database->GetClass()->FindPropertyByName(AnimationAssetsPropertyName);
	
	if (!AnimAssetsProperty)
	{
		UE_LOG(LogTemp, Error, TEXT("Could not find AnimationAssets property"));
		return false;
	}

	// Get the array
	FArrayProperty* ArrayProperty = CastField<FArrayProperty>(AnimAssetsProperty);
	if (!ArrayProperty)
	{
		return false;
	}

	void* ArrayPtr = ArrayProperty->ContainerPtrToValuePtr<void>(Database);
	FScriptArrayHelper ArrayHelper(ArrayProperty, ArrayPtr);

	// Clear the array
	ArrayHelper.EmptyValues();
	
	// Mark as dirty
	Database->MarkPackageDirty();
	
	// Trigger property change
	FPropertyChangedEvent PropertyEvent(AnimAssetsProperty);
	Database->PostEditChangeProperty(PropertyEvent);

	UE_LOG(LogTemp, Log, TEXT("Database cleared successfully"));
	
	return true;
#else
	UE_LOG(LogTemp, Warning, TEXT("ClearDatabase is only available in editor builds"));
	return false;
#endif
}

FString UAAANKPoseBlueprintLibrary::GetDatabaseInfo(UPoseSearchDatabase* Database)
{
	if (!Database)
	{
		return TEXT("Invalid database");
	}

	int32 AnimCount = Database->GetNumAnimationAssets();
	const UPoseSearchSchema* Schema = Database->Schema;  // Added const
	FString SchemaName = Schema ? Schema->GetName() : TEXT("None");
	
	return FString::Printf(TEXT("Database: %s\nAnimations: %d\nSchema: %s"),
		*Database->GetName(), AnimCount, *SchemaName);
}
