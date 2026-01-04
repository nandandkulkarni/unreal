#include "PoseSearchPythonExtensions.h"

#define LOCTEXT_NAMESPACE "FPoseSearchPythonExtensionsModule"

void FPoseSearchPythonExtensionsModule::StartupModule()
{
    UE_LOG(LogTemp, Log, TEXT("PoseSearchPythonExtensions module has started"));
}

void FPoseSearchPythonExtensionsModule::ShutdownModule()
{
    UE_LOG(LogTemp, Log, TEXT("PoseSearchPythonExtensions module has shut down"));
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FPoseSearchPythonExtensionsModule, PoseSearchPythonExtensions)
