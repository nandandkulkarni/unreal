#include "PoseSearchPythonExtensionsLibrary.h"
#include "PoseSearch/PoseSearchDatabase.h"
#include "PoseSearch/PoseSearchSchema.h"
#include "Animation/AnimSequence.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "Misc/ScopedSlowTask.h"
#include "UObject/SavePackage.h"

bool UPoseSearchPythonExtensionsLibrary::AddAnimationToDatabase(
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

    // Mark database for modification
    Database->Modify();

    // UE 5.7 has AddAnimationAsset() function!
    // Create FPoseSearchDatabaseAnimationAsset
    FPoseSearchDatabaseAnimationAsset AnimAsset;
    AnimAsset.Sequence = AnimSequence;
    
    // Add to database using the official API
    Database->AddAnimationAsset(AnimAsset);
    
    // Mark package as dirty
    Database->MarkPackageDirty();
    
    // Trigger property change notification to rebuild index
    FPropertyChangedEvent PropertyEvent(nullptr);
    Database->PostEditChangeProperty(PropertyEvent);

    UE_LOG(LogTemp, Log, TEXT("Successfully added animation to database"));
    
    return true;
}

int32 UPoseSearchPythonExtensionsLibrary::AddAnimationsToDatabase(
    UPoseSearchDatabase* Database,
    const TArray<UAnimSequence*>& AnimSequences)
{
    if (!Database)
    {
        UE_LOG(LogTemp, Error, TEXT("AddAnimationsToDatabase: Invalid database"));
        return 0;
    }

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
            AnimAsset.Sequence = Anim;
            
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
}

bool UPoseSearchPythonExtensionsLibrary::BuildDatabase(UPoseSearchDatabase* Database)
{
    if (!Database)
    {
        UE_LOG(LogTemp, Error, TEXT("BuildDatabase: Invalid database"));
        return false;
    }

    UE_LOG(LogTemp, Log, TEXT("Building database '%s'"), *Database->GetName());

    FScopedSlowTask Progress(1.0f, FText::FromString(TEXT("Building PoseSearch database")));
    Progress.MakeDialog();

    // Mark for modification
    Database->Modify();
    
    // Trigger a rebuild by simulating a property change
    // This forces the database to rebuild its search index
    FPropertyChangedEvent PropertyEvent(nullptr);
    Database->PostEditChangeProperty(PropertyEvent);
    
    // Mark package as dirty
    Database->MarkPackageDirty();
    
    // Save the asset
    FString PackageName = Database->GetOutermost()->GetName();
    FString PackageFileName = FPackageName::LongPackageNameToFilename(PackageName, 
        FPackageName::GetAssetPackageExtension());
    
    FSavePackageArgs SaveArgs;
    SaveArgs.TopLevelFlags = RF_Public | RF_Standalone;
    SaveArgs.SaveFlags = SAVE_NoError;
    
    bool bSaved = UPackage::SavePackage(Database->GetOutermost(), Database, 
        *PackageFileName, SaveArgs);
    
    if (bSaved)
    {
        UE_LOG(LogTemp, Log, TEXT("Database built and saved successfully"));
        return true;
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Database built but save failed"));
        return false;
    }
}

int32 UPoseSearchPythonExtensionsLibrary::GetAnimationCount(UPoseSearchDatabase* Database)
{
    if (!Database)
    {
        return 0;
    }

    // Use the existing method that's already accessible from Python
    return Database->GetNumAnimationAssets();
}

bool UPoseSearchPythonExtensionsLibrary::ClearDatabase(UPoseSearchDatabase* Database)
{
    if (!Database)
    {
        UE_LOG(LogTemp, Error, TEXT("ClearDatabase: Invalid database"));
        return false;
    }

    UE_LOG(LogTemp, Log, TEXT("Clearing database '%s'"), *Database->GetName());

    Database->Modify();
    
    // Get the AnimationAssets property
    static const FName AnimationAssetsPropertyName(TEXT("AnimationAssets"));
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
}

FString UPoseSearchPythonExtensionsLibrary::GetDatabaseInfo(UPoseSearchDatabase* Database)
{
    if (!Database)
    {
        return TEXT("Invalid database");
    }

    int32 AnimCount = Database->GetNumAnimationAssets();
    UPoseSearchSchema* Schema = Database->Schema;
    FString SchemaName = Schema ? Schema->GetName() : TEXT("None");
    
    return FString::Printf(TEXT("Database: %s\nAnimations: %d\nSchema: %s"),
        *Database->GetName(), AnimCount, *SchemaName);
}
