"""
Move Character Script - Run inside Unreal Engine Python Console
This moves the BP_ThirdPersonCharacter through waypoints using a timer (non-blocking).

Usage:
1. Open Unreal Engine
2. Go to Tools > Execute Python Script
3. Select this file
"""

import unreal
import time

# Global state to track movement
class MovementState:
    def __init__(self):
        self.actor = None
        self.positions = [
            (0, 0, 0),
            (300, 0, 0),
            (300, 300, 0),
            (0, 300, 0),
            (0, 0, 0)
        ]
        self.current_index = 0
        self.yaw = 0
        self.timer_handle = None
        self.start_time = 0
        self.delay = 2.0  # 2 seconds between waypoints

state = MovementState()

def find_actor():
    """Find the character actor in the level"""
    actor_path = '/Game/Main.Main:PersistentLevel.BP_ThirdPersonCharacter_C_1'
    state.actor = unreal.load_object(None, actor_path)
    
    if not state.actor:
        # Try finding by class
        actors = unreal.EditorLevelLibrary.get_all_level_actors()
        for a in actors:
            if 'ThirdPersonCharacter' in a.get_name():
                state.actor = a
                break
    
    if not state.actor:
        unreal.log_error("Could not find ThirdPersonCharacter actor!")
        return False
    
    unreal.log("Found actor: " + state.actor.get_name())
    return True

def move_to_next_waypoint():
    """Move to the next waypoint"""
    if state.current_index >= len(state.positions):
        unreal.log("Movement sequence complete!")
        # Unregister the timer
        if state.timer_handle:
            unreal.unregister_slate_post_tick_callback(state.timer_handle)
        return
    
    x, y, z = state.positions[state.current_index]
    unreal.log(f"Waypoint {state.current_index + 1}: Moving to ({x}, {y}, {z}) rotation {state.yaw} deg")
    
    # Set location
    new_location = unreal.Vector(x, y, z)
    state.actor.set_actor_location(new_location, False, False)
    
    # Set rotation
    new_rotation = unreal.Rotator(0, state.yaw, 0)  # Pitch, Yaw, Roll
    state.actor.set_actor_rotation(new_rotation, False)
    
    state.yaw = (state.yaw + 45) % 360
    state.current_index += 1
    state.start_time = time.time()

def tick_callback(delta_time):
    """Called every frame to check if it's time to move to next waypoint"""
    current_time = time.time()
    
    # Check if enough time has passed
    if current_time - state.start_time >= state.delay:
        move_to_next_waypoint()

def start_movement():
    """Initialize and start the movement sequence"""
    if not find_actor():
        return
    
    unreal.log("Starting movement sequence with timer...")
    
    # Reset state
    state.current_index = 0
    state.yaw = 0
    state.start_time = time.time()
    
    # Move to first waypoint immediately
    move_to_next_waypoint()
    
    # Register timer callback
    state.timer_handle = unreal.register_slate_post_tick_callback(tick_callback)
    
    unreal.log("Timer registered. Movement will continue every 2 seconds.")

# Run it
start_movement()
