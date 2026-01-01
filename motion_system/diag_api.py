import unreal
import json
import os

def diag():
    section = unreal.MovieSceneSkeletalAnimationSection()
    params = section.params
    
    info = {
        "params_type": str(type(params)),
        "play_rate_type": str(type(params.play_rate)),
        "play_rate_dir": dir(params.play_rate)
    }
    
    # Check if we can construct a variant
    if hasattr(unreal, "MovieSceneTimeWarpVariant"):
        info["variant_init"] = dir(unreal.MovieSceneTimeWarpVariant)
        
    log_path = r"C:\UnrealProjects\Coding\unreal\motion_system\dist\unreal_api_diag.json"
    with open(log_path, "w") as f:
        json.dump(info, f, indent=4)
        
if __name__ == "__main__":
    diag()
