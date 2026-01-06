"""
Motion Matching Integration for Procedural Movies

This module shows how to integrate Motion Matching queries
into your existing procedural movie system.

Usage:
    from motion_matching_selector import MotionMatchingSelector
    
    selector = MotionMatchingSelector()
    anim, start_time = selector.select_for_velocity(velocity=500, direction=(1,0,0))
    
    # Use in your sequencer
    track.add_section(animation=anim, start_time=start_time)
"""

import unreal

class MotionMatchingSelector:
    """
    Animation selector using Motion Matching for procedural movies.
    
    This class spawns a hidden character, queries Motion Matching,
    and returns the best animation for desired movement.
    """
    
    def __init__(self, database_path="/Game/MotionMatching/MannyMotionDatabase"):
        """Initialize with Motion Matching database"""
        self.database = unreal.load_object(None, database_path)
        if not self.database:
            raise Exception(f"Database not found: {database_path}")
        
        self.character_bp_path = "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter"
        self.pose_search_lib = unreal.PoseSearchLibrary
        
        # Cache for spawned character (reuse to avoid spawning every time)
        self._character = None
        self._anim_instance = None
    
    def _ensure_character(self):
        """Spawn character if not already spawned"""
        if self._character is None:
            editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
            world = editor_subsystem.get_editor_world()
            
            character_bp = unreal.load_object(None, self.character_bp_path)
            
            # Spawn off-screen/hidden
            self._character = unreal.EditorLevelLibrary.spawn_actor_from_object(
                character_bp,
                unreal.Vector(-10000, -10000, -10000),  # Far away
                unreal.Rotator(0, 0, 0)
            )
            
            # Get AnimInstance
            skel_comp = self._character.get_components_by_class(unreal.SkeletalMeshComponent)[0]
            self._anim_instance = skel_comp.get_anim_instance()
    
    def select_for_velocity(self, velocity, direction=(1, 0, 0)):
        """
        Select best animation for given velocity and direction.
        
        Args:
            velocity: Speed in units/sec (e.g., 200=walk, 500=jog)
            direction: Normalized direction vector (x, y, z)
        
        Returns:
            (animation, start_time) tuple for use in sequencer
        """
        self._ensure_character()
        
        # Determine animation type based on velocity
        speed = abs(velocity)
        
        if speed < 100:
            anim_type = "Idle"
            anim_path = "/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle"
        elif speed < 350:
            anim_type = "Walk"
            anim_path = self._get_walk_anim_for_direction(direction)
        else:
            anim_type = "Jog"
            anim_path = self._get_jog_anim_for_direction(direction)
        
        # Load desired animation
        desired_anim = unreal.load_object(None, anim_path)
        
        # Create query parameters
        continuing_props = unreal.PoseSearchContinuingProperties()
        future_props = unreal.PoseSearchFutureProperties()
        
        if desired_anim:
            future_props.animation = desired_anim
            future_props.animation_time = 0.0
            future_props.interval_time = 0.5
        
        # Query Motion Matching
        result = self.pose_search_lib.motion_match(
            anim_instance=self._anim_instance,
            assets_to_search=[self.database],
            pose_history_name="PoseHistory",
            continuing_properties=continuing_props,
            future=future_props
        )
        
        if result.selected_anim:
            return result.selected_anim, result.selected_time
        else:
            # Fallback to desired animation
            return desired_anim, 0.0
    
    def _get_walk_anim_for_direction(self, direction):
        """Get walk animation based on direction"""
        x, y, z = direction
        
        if x > 0.7:
            return "/Game/Characters/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Fwd"
        elif x < -0.7:
            return "/Game/Characters/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Bwd"
        elif y > 0.7:
            return "/Game/Characters/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Right"
        elif y < -0.7:
            return "/Game/Characters/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Left"
        else:
            return "/Game/Characters/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Fwd"
    
    def _get_jog_anim_for_direction(self, direction):
        """Get jog animation based on direction"""
        x, y, z = direction
        
        if x > 0.7:
            return "/Game/Characters/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd"
        elif x < -0.7:
            return "/Game/Characters/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Bwd"
        elif y > 0.7:
            return "/Game/Characters/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Right"
        elif y < -0.7:
            return "/Game/Characters/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Left"
        else:
            return "/Game/Characters/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd"
    
    def cleanup(self):
        """Cleanup spawned character"""
        if self._character:
            self._character.destroy_actor()
            self._character = None
            self._anim_instance = None


# ============================================================================
# EXAMPLE USAGE IN YOUR PROCEDURAL MOVIE
# ============================================================================

def example_procedural_movie():
    """
    Example showing how to use Motion Matching in your procedural movie.
    """
    
    # Initialize selector
    selector = MotionMatchingSelector()
    
    # Your existing procedural movie code
    # Assuming you have a sequencer and character track
    
    # Scene 1: Character starts idle
    anim, start_time = selector.select_for_velocity(velocity=0)
    # track.add_section(time=0.0, animation=anim, start_time=start_time, duration=2.0)
    
    # Scene 2: Character walks forward
    anim, start_time = selector.select_for_velocity(velocity=200, direction=(1, 0, 0))
    # track.add_section(time=2.0, animation=anim, start_time=start_time, duration=3.0)
    
    # Scene 3: Character jogs forward
    anim, start_time = selector.select_for_velocity(velocity=500, direction=(1, 0, 0))
    # track.add_section(time=5.0, animation=anim, start_time=start_time, duration=2.0)
    
    # Scene 4: Character walks backward
    anim, start_time = selector.select_for_velocity(velocity=200, direction=(-1, 0, 0))
    # track.add_section(time=7.0, animation=anim, start_time=start_time, duration=2.0)
    
    # Cleanup
    selector.cleanup()
    
    print("Procedural movie created with Motion Matching!")


# ============================================================================
# INTEGRATION WITH YOUR EXISTING SYSTEM
# ============================================================================

"""
To integrate with your existing procedural movie system:

1. Import this module:
   from motion_matching_selector import MotionMatchingSelector

2. Create selector at the start of your movie:
   selector = MotionMatchingSelector()

3. Replace your animation selection logic:
   
   OLD WAY (manual selection):
   if speed < 350:
       anim = "/Game/Animations/Walk_Fwd"
   else:
       anim = "/Game/Animations/Jog_Fwd"
   
   NEW WAY (Motion Matching):
   anim, start_time = selector.select_for_velocity(
       velocity=character_speed,
       direction=character_direction
   )

4. Use in your sequencer tracks:
   track.add_section(
       time=current_time,
       animation=anim,
       start_time=start_time,  # Motion Matching picks best frame!
       duration=section_duration
   )

5. Cleanup at the end:
   selector.cleanup()

BENEFITS:
- Motion Matching automatically picks best animation frame
- Smoother transitions between animations
- Less manual animation selection logic
- Still deterministic (same input = same output)
"""
