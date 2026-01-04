using UnrealBuildTool;

public class PoseSearchPythonExtensions : ModuleRules
{
    public PoseSearchPythonExtensions(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "UnrealEd",
            "PoseSearch",
            "PythonScriptPlugin"
        });

        PrivateDependencyModuleNames.AddRange(new string[]
        {
            "Slate",
            "SlateCore",
            "AssetRegistry"
        });
    }
}
