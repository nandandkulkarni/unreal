import unreal
import sys
import os

# Add path to finding includes
sys.path.insert(0, r"c:\UnrealProjects\coding\unreal\motion_system_track_based")

from motion_includes import mannequin_setup
from motion_includes.assets import Characters

def test_spawn():
    print("Testing Pia Spawn...")
    mannequin_setup.log = print # Override log
    
    path = "/Game/MetaHumans/Pia/BP_Pia.BP_Pia"
    # Or use Characters.BELICA if it points to Pia now
    # path = Characters.BELICA 
    print(f"Path: {path}")
    
    try:
        actor = mannequin_setup.create_mannequin("TestPia", unreal.Vector(0,0,0), unreal.Rotator(0,0,0), mesh_path=path)
        
        if actor:
            print(f"Spawned: {actor} Type: {type(actor)}")
            is_skel = isinstance(actor, unreal.SkeletalMeshActor)
            print(f"Is SkeletalMeshActor? {is_skel}")
            
            comps = actor.get_components_by_class(unreal.SkeletalMeshComponent)
            print(f"SkeletalMeshComponents found: {len(comps)}")
            for c in comps:
                print(f"  - {c.get_name()} ({type(c)})")
                
            return True
        else:
            print("Failed to spawn actor")
            return False
            
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_spawn()
