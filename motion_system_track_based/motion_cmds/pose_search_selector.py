"""
Motion Matching Selector (Remote / Hybrid)

This module runs locally (in the build script) but queries Unreal Engine
via Remote Control API to perform the actual Pose Search.
"""

import sys
import json
import requests
import os

# Remote Control URL
RC_URL = "http://localhost:30010/remote/object/call"

class PoseSearchSelector:
    """
    Selects animations using Unreal's Motion Matching system via Remote Control.
    """
    
    def __init__(self, database_path="/Game/MotionMatching/MannyMotionDatabase"):
        self.database_path = database_path

    def select(self, speed, direction=(1,0,0), context_hint=None):
        """
        Query the Unreal Engine for the best animation.
        """
        # Handle context_hint being None or a path
        context_anim_str = f"'{context_hint}'" if context_hint else "None"
        
        # We use string concatenation / formatting carefully
        # Note: double braces {{ and }} are for the outer script if used with format,
        # but here we construct the script string cleanly.
        
        script_body = """
import unreal
import json
import os
import traceback

# Output file path matches script
out_file = "C:/UnrealProjects/coding/unreal/motion_system_track_based/temp_mm_result.json"

def perform_query():
    try:
        # Load Database
        db_path = "{DB_PATH}"
        db = unreal.load_object(None, db_path)
        if not db:
            return {'error': 'Database not found: ' + db_path}

        # Spawn Temp Character
        character_bp = unreal.load_object(None, "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter")
        if not character_bp:
             return {'error': 'Character BP not found'}

        # Spawn hidden
        actor = unreal.EditorLevelLibrary.spawn_actor_from_object(
            character_bp, 
            unreal.Vector(-10000, -10000, -10000), 
            unreal.Rotator(0,0,0)
        )
        
        try:
            skel = actor.get_components_by_class(unreal.SkeletalMeshComponent)[0]
            anim_inst = skel.get_anim_instance()
            
            # Setup Query
            cont_props = unreal.PoseSearchContinuingProperties()
            future_props = unreal.PoseSearchFutureProperties()
            
            # Context Hint
            ctx_path = {CTX_VAL}
            if ctx_path:
                anim_obj = unreal.load_object(None, ctx_path)
                if anim_obj:
                    future_props.animation = anim_obj
            
            # SIMULATE VELOCITY? 
            # We are testing purely based on Context Hint and Database logic for now.
            # If we need speed, we might need a Trajectory generation step or input.
            
            

            # CHECK DATABASE CONTENT VIA PLUGIN
            num_assets = -1
            try:
                lib = unreal.AAANKPoseBlueprintLibrary
                num_assets = lib.get_animation_count(db)
            except:
                # Fallback props
                if hasattr(db, "animation_assets"):
                     try: num_assets = len(db.animation_assets)
                     except: pass
            
            # Context Debug
            debug_info = []
            if ctx_path:
                anim_obj = unreal.load_object(None, ctx_path)
                if anim_obj:
                    future_props.animation = anim_obj
                    debug_info.append(f"Set Future Anim: {anim_obj.get_name()}")
                else:
                    debug_info.append(f"Failed to load Context: {ctx_path}")
            
            # Execute
            res = unreal.PoseSearchLibrary.motion_match(
                anim_instance=anim_inst,
                assets_to_search=[db],
                pose_history_name="PoseHistory",
                continuing_properties=cont_props,
                future=future_props
            )
            
            r_name = "None"
            if res.selected_anim:
                 r_name = res.selected_anim.get_name()
            
            result_path = res.selected_anim.get_path_name() if res.selected_anim else None
            
            result_data = {
                'anim_path': result_path,
                'start_time': res.selected_time,
                'cost': res.search_cost,
                'debug_name': r_name,
                'db_asset_count': num_assets,
                'db_name': db.get_name(),
                'debug_log': "; ".join(debug_info)
            }
            return result_data
            
        finally:
             if actor: actor.destroy_actor()
             
    except Exception as e:
         return {'error': str(e) + "\\n" + traceback.format_exc()}

# Write result to file
try:
    result = perform_query()
    with open(out_file, 'w') as f:
        json.dump(result, f)
except Exception as main_e:
    # Last resort capture
    with open(out_file, 'w') as f:
        json.dump({'error': 'MAIN_SCRIPT_CRASH: ' + str(main_e)}, f)
"""
        # Inject variables
        script = script_body.replace("{DB_PATH}", self.database_path)
        script = script.replace("{CTX_VAL}", context_anim_str)
        
        # Output file path matches script
        out_file = "C:/UnrealProjects/coding/unreal/motion_system_track_based/temp_mm_result.json"
        
        # Clear previous result
        if os.path.exists(out_file):
            try: os.remove(out_file)
            except: pass
        
        # Send Request
        payload = {
            "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
            "functionName": "ExecutePythonCommand",
            "parameters": {"PythonCommand": script}
        }
        
        try:
            # Increase timeout to account for spawning overhead
            response = requests.put(RC_URL, json=payload, timeout=30)
            
            if response.status_code == 200:
                # Read result file
                import time
                time.sleep(0.1)
                
                if os.path.exists(out_file):
                    try:
                        with open(out_file, 'r') as f:
                            res_data = json.load(f)
                        
                        if res_data.get('anim_path'):
                             class AnimStub:
                                 def __init__(self, p): self.path = p
                                 def get_path_name(self): return self.path
                                 
                             return AnimStub(res_data['anim_path']), res_data.get('start_time', 0.0)
                        elif res_data.get('error'):
                             print(f"Remote Script Error: {res_data['error']}")
                    except Exception as read_err:
                        print(f"Error reading result file: {read_err}")
                else:
                    print("Error: Result file was not created by remote script.")
                
        except Exception as e:
            print(f"Remote Query Error: {e}")
            
        return None, 0.0

    def cleanup(self):
        pass
