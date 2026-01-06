"""
Terrain-Aware Motion Matching for Procedural Movies

Handles complex terrain scenarios like mountain climbing with:
- Different slope angles
- Turns and direction changes
- Terrain type detection
- Automatic animation selection based on terrain
"""

import unreal
import math

class TerrainAwareMotionMatchingSelector:
    """
    Advanced Motion Matching selector that accounts for terrain.
    Perfect for mountain climbing, stairs, slopes, etc.
    """
    
    def __init__(self, database_path="/Game/MotionMatching/MannyMotionDatabase"):
        self.database = unreal.load_object(None, database_path)
        self.character_bp_path = "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter"
        self.pose_search_lib = unreal.PoseSearchLibrary
        
        self._character = None
        self._anim_instance = None
    
    def _ensure_character(self):
        """Spawn character if needed"""
        if self._character is None:
            editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
            world = editor_subsystem.get_editor_world()
            character_bp = unreal.load_object(None, self.character_bp_path)
            
            self._character = unreal.EditorLevelLibrary.spawn_actor_from_object(
                character_bp,
                unreal.Vector(-10000, -10000, -10000),
                unreal.Rotator(0, 0, 0)
            )
            
            skel_comp = self._character.get_components_by_class(unreal.SkeletalMeshComponent)[0]
            self._anim_instance = skel_comp.get_anim_instance()
    
    def select_for_terrain_movement(self, start_pos, end_pos, duration, world=None):
        """
        Select animation based on terrain-aware movement.
        
        Args:
            start_pos: (x, y, z) tuple or unreal.Vector
            end_pos: (x, y, z) tuple or unreal.Vector
            duration: movement duration in seconds
            world: Optional world for terrain queries
        
        Returns:
            (animation, start_time, metadata) tuple
        """
        self._ensure_character()
        
        # Helper to convert Vector to tuple if needed
        def to_tuple(pos):
            if hasattr(pos, 'x') and hasattr(pos, 'y') and hasattr(pos, 'z'):
                return (pos.x, pos.y, pos.z)
            return pos

        start_pos = to_tuple(start_pos)
        end_pos = to_tuple(end_pos)
        
        # Calculate movement vector
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        dz = end_pos[2] - start_pos[2]
        
        # Calculate horizontal distance and slope
        horizontal_distance = math.sqrt(dx**2 + dy**2)
        slope_angle = math.degrees(math.atan2(dz, horizontal_distance)) if horizontal_distance > 0 else 0
        
        # Calculate velocity
        total_distance = math.sqrt(dx**2 + dy**2 + dz**2)
        velocity = total_distance / duration if duration > 0 else 0
        
        # Calculate horizontal direction
        if horizontal_distance > 0:
            direction = (dx/horizontal_distance, dy/horizontal_distance, 0)
        else:
            direction = (0, 0, 0)
        
        # Determine terrain type and animation category
        terrain_info = self._analyze_terrain(slope_angle, velocity)
        
        # Select appropriate animation
        anim_path = self._select_animation_for_terrain(
            terrain_info['type'],
            terrain_info['slope_category'],
            velocity,
            direction
        )
        
        # Load animation
        desired_anim = unreal.load_object(None, anim_path)
        
        # Query Motion Matching
        continuing_props = unreal.PoseSearchContinuingProperties()
        future_props = unreal.PoseSearchFutureProperties()
        
        if desired_anim:
            future_props.animation = desired_anim
            future_props.animation_time = 0.0
            future_props.interval_time = 0.5
        
        result = self.pose_search_lib.motion_match(
            anim_instance=self._anim_instance,
            assets_to_search=[self.database],
            pose_history_name="PoseHistory",
            continuing_properties=continuing_props,
            future=future_props
        )
        
        metadata = {
            'slope_angle': slope_angle,
            'terrain_type': terrain_info['type'],
            'velocity': velocity,
            'direction': direction
        }
        
        if result.selected_anim:
            return result.selected_anim, result.selected_time, metadata
        else:
            return desired_anim, 0.0, metadata
    
    def _analyze_terrain(self, slope_angle, velocity):
        """
        Analyze terrain based on slope angle.
        
        Returns terrain type and slope category.
        """
        abs_slope = abs(slope_angle)
        
        if abs_slope < 5:
            terrain_type = "flat"
            slope_category = "flat"
        elif abs_slope < 15:
            terrain_type = "gentle_slope"
            slope_category = "uphill" if slope_angle > 0 else "downhill"
        elif abs_slope < 30:
            terrain_type = "moderate_slope"
            slope_category = "uphill" if slope_angle > 0 else "downhill"
        elif abs_slope < 50:
            terrain_type = "steep_slope"
            slope_category = "uphill" if slope_angle > 0 else "downhill"
        else:
            terrain_type = "climbing"
            slope_category = "climbing" if slope_angle > 0 else "descending"
        
        return {
            'type': terrain_type,
            'slope_category': slope_category,
            'angle': slope_angle
        }
    
    def _select_animation_for_terrain(self, terrain_type, slope_category, velocity, direction):
        """
        Select appropriate animation based on terrain and movement.
        """
        # Determine speed category
        if velocity < 100:
            speed = "idle"
        elif velocity < 350:
            speed = "walk"
        else:
            speed = "jog"
        
        # Map terrain + speed to animation
        # NOTE: You'll need to add slope/climbing animations to your database
        
        if terrain_type == "flat":
            return self._get_flat_animation(speed, direction)
        
        elif terrain_type == "gentle_slope":
            if slope_category == "uphill":
                return "/Game/Characters/Mannequins/Anims/Slopes/Walk_Uphill_Gentle"
            else:
                return "/Game/Characters/Mannequins/Anims/Slopes/Walk_Downhill_Gentle"
        
        elif terrain_type == "moderate_slope":
            if slope_category == "uphill":
                return "/Game/Characters/Mannequins/Anims/Slopes/Walk_Uphill_Moderate"
            else:
                return "/Game/Characters/Mannequins/Anims/Slopes/Walk_Downhill_Moderate"
        
        elif terrain_type == "steep_slope":
            if slope_category == "uphill":
                return "/Game/Characters/Mannequins/Anims/Climbing/Climb_Steep"
            else:
                return "/Game/Characters/Mannequins/Anims/Climbing/Descend_Steep"
        
        elif terrain_type == "climbing":
            if slope_category == "climbing":
                return "/Game/Characters/Mannequins/Anims/Climbing/Climb_Vertical"
            else:
                return "/Game/Characters/Mannequins/Anims/Climbing/Descend_Vertical"
        
        # Fallback
        return "/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle"
    
    def _get_flat_animation(self, speed, direction):
        """Get animation for flat terrain"""
        x, y, _ = direction
        
        if speed == "idle":
            return "/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle"
        elif speed == "walk":
            if x > 0.7:
                return "/Game/Characters/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Fwd"
            elif x < -0.7:
                return "/Game/Characters/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Bwd"
            else:
                return "/Game/Characters/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Fwd"
        else:  # jog
            if x > 0.7:
                return "/Game/Characters/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd"
            else:
                return "/Game/Characters/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd"
    
    def cleanup(self):
        """Cleanup spawned character"""
        if self._character:
            self._character.destroy_actor()
            self._character = None
            self._anim_instance = None


# ============================================================================
# EXAMPLE: MOUNTAIN CLIMBING MOVIE
# ============================================================================

def create_mountain_climbing_movie():
    """
    Example: Character climbs a mountain with varying terrain.
    """
    
    selector = TerrainAwareMotionMatchingSelector()
    
    # Define mountain path with varying elevations
    mountain_path = [
        # (x, y, z), duration, description
        ((0, 0, 0), (100, 0, 0), 2.0, "Flat approach"),
        ((100, 0, 0), (200, 0, 20), 3.0, "Gentle uphill"),
        ((200, 0, 20), (300, 0, 60), 4.0, "Moderate slope"),
        ((300, 0, 60), (350, 0, 120), 5.0, "Steep climb"),
        ((350, 0, 120), (400, 0, 180), 6.0, "Very steep climb"),
        ((400, 0, 180), (450, 0, 200), 3.0, "Gentle slope to summit"),
        ((450, 0, 200), (500, 0, 200), 2.0, "Flat summit"),
    ]
    
    current_time = 0.0
    
    print("=" * 60)
    print("MOUNTAIN CLIMBING MOVIE - ANIMATION SEQUENCE")
    print("=" * 60)
    
    for start_pos, end_pos, duration, description in mountain_path:
        # Get terrain-aware animation
        anim, start_time, metadata = selector.select_for_terrain_movement(
            start_pos, end_pos, duration
        )
        
        print(f"\n{description}:")
        print(f"  Time: {current_time:.1f}s - {current_time + duration:.1f}s")
        print(f"  Elevation: {start_pos[2]}m → {end_pos[2]}m")
        print(f"  Slope: {metadata['slope_angle']:.1f}°")
        print(f"  Terrain: {metadata['terrain_type']}")
        print(f"  Animation: {anim.get_name() if anim else 'None'}")
        
        # Add to sequencer
        # track.add_section(
        #     time=current_time,
        #     animation=anim,
        #     start_time=start_time,
        #     duration=duration
        # )
        
        current_time += duration
    
    selector.cleanup()
    
    print("\n" + "=" * 60)
    print(f"Total movie duration: {current_time:.1f} seconds")
    print("=" * 60)


# ============================================================================
# TERRAIN CLASSIFICATION GUIDE
# ============================================================================

"""
SLOPE ANGLE CLASSIFICATION:

0-5°:    Flat ground (normal walk/jog)
5-15°:   Gentle slope (slight uphill/downhill walk)
15-30°:  Moderate slope (noticeable uphill effort)
30-50°:  Steep slope (climbing animations)
50°+:    Vertical/near-vertical (rock climbing)

EXAMPLE CALCULATIONS:

Flat: (0,0,0) → (100,0,0) = 0° slope
Gentle: (0,0,0) → (100,0,10) = 5.7° slope
Moderate: (0,0,0) → (100,0,30) = 16.7° slope
Steep: (0,0,0) → (100,0,60) = 31° slope
Climbing: (0,0,0) → (100,0,100) = 45° slope
"""

if __name__ == "__main__":
    create_mountain_climbing_movie()
