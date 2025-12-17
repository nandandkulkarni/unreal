"""
Comprehensive Remote Control API Function List
Tests all known Unreal subsystems and libraries to find what's accessible
"""

import requests
import json

REMOTE_CONTROL_URL = "http://localhost:30010/remote/object"

def describe_object(object_path):
    """Get all available functions/properties on an object"""
    url = f"{REMOTE_CONTROL_URL}/describe"
    payload = {"objectPath": object_path}
    
    try:
        response = requests.put(url, json=payload, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

def main():
    print("=" * 80)
    print("COMPREHENSIVE REMOTE CONTROL API FUNCTION LIST")
    print("=" * 80)
    
    # All objects to check
    objects_to_check = [
        # Sequencer/Level Sequence
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorSubsystem",
        "/Script/SequencerScripting.Default__SequencerTools",
        "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
        "/Script/LevelSequence.Default__LevelSequencePlayer",
        
        # Editor
        "/Script/UnrealEd.Default__EditorLevelLibrary",
        "/Script/UnrealEd.Default__EditorAssetLibrary",
        "/Script/UnrealEd.Default__EditorActorSubsystem",
        "/Script/UnrealEd.Default__EditorSubsystem",
        
        # Movie Pipeline
        "/Engine/Transient.DisplayClusterEditorEngine_0:MoviePipelineQueueSubsystem_0",
        "/Script/MovieRenderPipelineCore.Default__MoviePipelineQueueSubsystem",
        
        # Python (blocked but let's check)
        "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
        
        # World/Level
        "/Game/Main.Main:PersistentLevel",
        "/Engine/Transient.World_0",
    ]
    
    results = {}
    
    for obj_path in objects_to_check:
        print(f"\nChecking: {obj_path}")
        result = describe_object(obj_path)
        
        if result:
            functions = result.get("Functions", [])
            function_names = [f.get("Name") for f in functions]
            results[obj_path] = function_names
            print(f"  [OK] {len(function_names)} functions available")
        else:
            print(f"  [X] Not accessible")
    
    # Write results to file
    print("\n" + "=" * 80)
    print("WRITING RESULTS TO FILE")
    print("=" * 80)
    
    output_file = "C:/U/CinematicPipeline_Scripts/external_control/remote_api_complete_list.md"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Complete Remote Control API Function List\n\n")
        f.write("All accessible objects and their functions via Remote Control API\n\n")
        f.write("Generated: 2025-12-16\n\n")
        
        for obj_path, functions in results.items():
            f.write(f"## {obj_path}\n\n")
            f.write(f"**Total functions:** {len(functions)}\n\n")
            
            if len(functions) > 0:
                f.write("**Available functions:**\n")
                for func in sorted(functions):
                    f.write(f"- `{func}`\n")
                f.write("\n")
            else:
                f.write("*No functions or not accessible*\n\n")
            
            f.write("---\n\n")
        
        # Summary
        f.write("## Summary\n\n")
        f.write("### Accessible Objects:\n\n")
        for obj_path, functions in results.items():
            status = "[OK]" if len(functions) > 0 else "[X]"
            f.write(f"- {status} {obj_path} ({len(functions)} functions)\n")
    
    print(f"\n[OK] Results written to: {output_file}")
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    accessible = [(path, len(funcs)) for path, funcs in results.items() if len(funcs) > 0]
    not_accessible = [path for path, funcs in results.items() if len(funcs) == 0]
    
    print(f"\n[OK] Accessible: {len(accessible)} objects")
    for path, count in accessible:
        short_name = path.split(".")[-1]
        print(f"  - {short_name}: {count} functions")
    
    print(f"\n[X] Not accessible: {len(not_accessible)} objects")
    for path in not_accessible:
        short_name = path.split(".")[-1]
        print(f"  - {short_name}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    try:
        requests.get("http://localhost:30010/remote/info")
        print("[OK] Remote Control server is running\n")
    except:
        print("[X] Remote Control server not running!")
        print("   Start it in Unreal: WebControl.StartServer")
        exit(1)
    
    main()
