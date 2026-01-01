import json
import sys

def diag():
    import unreal
    info = {}
    if hasattr(unreal, "MovieSceneTimeWarpVariant"):
        variant_class = unreal.MovieSceneTimeWarpVariant
        info["class"] = str(variant_class)
        info["dir"] = dir(variant_class)
        
        try:
            v = unreal.MovieSceneTimeWarpVariant()
            info["instance_dir"] = dir(v)
            # Check for common property names in variants
            common_props = ["float_value", "value", "frame_rate", "rate"]
            for prop in common_props:
                if hasattr(v, prop):
                    info[f"has_{prop}"] = True
        except Exception as e:
            info["init_error"] = str(e)
            
    log_path = r"C:\UnrealProjects\Coding\unreal\motion_system\dist\unreal_variant_diag.json"
    try:
        with open(log_path, "w") as f:
            json.dump(info, f, indent=4)
    except:
        pass

# MOVIE constant for trigger_movie
MOVIE = {"name": "Diag", "plan": []}

# If inside Unreal, run diag
if "unreal" in sys.modules:
    diag()
