// Copyright Epic Games, Inc. All Rights Reserved.

#include "AAANKPose.h"

#define LOCTEXT_NAMESPACE "FAAANKPoseModule"

void FAAANKPoseModule::StartupModule()
{
	// This code will execute after your module is loaded into memory; the exact timing is specified in the .uplugin file per-module
}

void FAAANKPoseModule::ShutdownModule()
{
	// This function may be called during shutdown to clean up your module.  For modules that support dynamic reloading,
	// we call this function before unloading the module.
}

FString FAAANKPoseModule::HelloWorld()
{
	return TEXT("Hello World");
}

#undef LOCTEXT_NAMESPACE
	
IMPLEMENT_MODULE(FAAANKPoseModule, AAANKPose)