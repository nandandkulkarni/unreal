#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

/**
 * PoseSearch Python Extensions Module
 * Exposes PoseSearch database functions to Python
 */
class FPoseSearchPythonExtensionsModule : public IModuleInterface
{
public:
    /** IModuleInterface implementation */
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
