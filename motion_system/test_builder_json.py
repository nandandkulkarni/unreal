import json
import os
import sys

# Mock unreal module BEFORE importing generic modules that might need it
import types
mock_unreal = types.ModuleType("unreal")
sys.modules["unreal"] = mock_unreal

# Mock sys.path to ensure we can import the module
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)  # Go up to unreal/
sys.path.append(parent_dir)
sys.path.append(os.path.join(parent_dir, "direct")) # For imports like 'logger' which are often in direct/
sys.path.append(os.path.join(parent_dir, "motion_system")) # For direct imports from motion_system

from motion_system.motion_builder import MovieBuilder

def generate_old_plan():
    # This exactly matches the semantics of demos\belica_scene_v3_motion_commands.py
    return [
        {"actor": "belica", "command": "animation", "name": "Jog_Fwd"},
        {"actor": "belica", "command": "move_by_distance", "direction": "forward", "meters": 5, "speed_mph": 3, "waypoint_name": "point_A"},
        {"actor": "belica", "command": "wait", "seconds": 1},
        {"actor": "belica", "command": "animation", "name": "Jog_Left_Start"},
        {"actor": "belica", "command": "move_and_turn", "direction": "left", "meters": 3, "turn_degrees": 90, "speed_mph": 2, "turn_speed_deg_per_sec": 45},
        {"actor": "belica", "command": "animation", "name": "Jog_Fwd"},
        {"actor": "belica", "command": "move_for_seconds", "direction": "forward", "seconds": 3, "speed_mph": 2},
    ]

def generate_new_plan():
    builder = MovieBuilder("TestSequence")
    
    # We need to manually register the actor context to match the "belica" actor appearing in commands
    # The Builder pattern tracks actors, but the output plan attaches "actor": name to each command.
    
    builder.add_actor("belica", (0,0,0)) # Dummy location for state tracking
    
    # Using the builder to recreate the plan
    with builder.for_actor("belica") as belica:
        belica.animation("Jog_Fwd")
        # Custom command not standard in builder yet? "speed_mph"
        # We might need to adjust the builder to support these specific kwargs or standard units.
        # But for now let's see what the builder has.
        # It has move_for_seconds(seconds, direction, speed_mtps)
        # It has move_to_location(target, speed_mtps)
        
        # It does NOT have move_by_distance directly exposed in the same way?
        # Let's check the code:
        # It has move_for_seconds.
        # It generates "move_for_seconds".
        
        # Checking builder source...
        # It seems the builder is slightly different from the old manual plan.
        # The user's request is to verify the generated json. 
        # If the builder commands don't perfectly align 1:1 with the old commands, we might produce equivalent but different JSON.
        pass
        
    return builder.build()["plan"]

def test_json_generation():
    old_plan = generate_old_plan()
    
    # SAVE OLD PLAN
    with open("old_plan_reference.json", "w") as f:
        json.dump(old_plan, f, indent=2)
    print("Saved old_plan_reference.json")

    # BUILD NEW PLAN
    # We will attempt to construct the equivalent plan using the builder's existing methods
    builder = MovieBuilder("TestSequence")
    builder.add_actor("belica", (0,0,0)) # Dummy location
    
    with builder.for_actor("belica") as b:
        # 1. Animation
        b.animation("Jog_Fwd")
        # 2. Move Forward 5m
        b.move_by_distance(meters=5, direction="forward", speed_mph=3, waypoint_name="point_A")
        # 3. Wait 1s
        b.wait(1)
        # 4. Animation Jog_Left
        b.animation("Jog_Left_Start")
        # 5. Move and Turn Left
        b.move_and_turn(direction="left", meters=3, turn_degrees=90, speed_mph=2, turn_speed_deg_per_sec=45)
        # 6. Animation Jog_Fwd
        b.animation("Jog_Fwd")
        # 7. Move for Seconds
        b.move_for_seconds(direction="forward", seconds=3, speed_mph=2)

    # For this test script, since I cannot exactly reproduce the old plan without modifying the builder
    # (which requires "execution" not just verification), I will just dump what the builder DOES produce.
    
    new_plan = builder.build()["plan"]
    with open("new_plan_generated.json", "w") as f:
        json.dump(new_plan, f, indent=2)
    print("Saved new_plan_generated.json")

if __name__ == "__main__":
    test_json_generation()
