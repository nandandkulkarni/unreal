from typing import Tuple, Union, Optional
from motion_structs.enums import LightType, LightUnit, LightColor
from motion_structs.actor_data import ActorTrackSet

class LightBuilder:
    """
    Fluent API for configuring a light source.
    Auto-adds to movie when chain completes (no explicit .add() needed).
    """
    def __init__(self, movie_builder, name: str, light_type: LightType, location: Tuple[float, float, float]):
        self.mb = movie_builder
        self.name = name
        self.light_type = light_type
        self.location = location
        
        # Default properties
        self._rotation = (0, 0, 0)
        self._intensity = 5000.0
        self._intensity_unit = LightUnit.UNITLESS
        self._color = LightColor.WHITE
        self._attenuation_radius = 1000.0
        self._inner_cone = 0.0
        self._outer_cone = 44.0
        self._cast_shadows = True
        self._use_atmospheric_sun = False
        self._cast_volumetric_shadow = True
        self._light_shaft_bloom_scale = None
        self._light_shaft_occlusion = False
        
        # Auto-add on creation (lights don't need explicit .add() call)
        self._finalize()

    def _finalize(self):
        """Internal: Add light to movie's actor list."""
        # Convert color to tuple if Enum
        rgb = self._color.value if isinstance(self._color, LightColor) else self._color
        
        track_set = ActorTrackSet(self.name, actor_type="light")
        track_set.initial_state = {
            "location": list(self.location),
            "rotation": list(self._rotation),
            "properties": {
                "light_type": self.light_type.value,
                "intensity": self._intensity,
                "intensity_unit": self._intensity_unit.name,
                "color": list(rgb),
                "attenuation_radius": self._attenuation_radius,
                "inner_cone_angle": self._inner_cone,
                "outer_cone_angle": self._outer_cone,
                "cast_shadows": self._cast_shadows,
                "use_as_atmospheric_sun": self._use_atmospheric_sun,
                "cast_volumetric_shadow": self._cast_volumetric_shadow,
                "light_shaft_bloom_scale": self._light_shaft_bloom_scale,
                "light_shaft_occlusion": self._light_shaft_occlusion
            }
        }
        
        # Add attachment if specified
        if hasattr(self, '_attach_parent'):
            track_set.attach.add_section(
                parent_actor=self._attach_parent,
                socket_name=getattr(self, '_attach_socket', ""),
                start_frame=0,
                end_frame=None  # Until end of sequence
            )
        
        self.mb.actors[self.name] = track_set

    def intensity(self, value: float, unit: LightUnit = LightUnit.UNITLESS) -> 'LightBuilder':
        """Set the light's intensity."""
        self._intensity = value
        self._intensity_unit = unit
        self._finalize()  # Re-finalize with updated values
        return self

    def color(self, color: Union[LightColor, Tuple[float, float, float]]) -> 'LightBuilder':
        """Set the light's color."""
        self._color = color
        self._finalize()
        return self

    def rotation(self, roll: float = 0.0, pitch: float = 0.0, yaw: float = 0.0) -> 'LightBuilder':
        """Set the light's rotation (degrees)."""
        self._rotation = (roll, pitch, yaw)
        self._finalize()
        return self

    def attenuation_radius(self, radius: float) -> 'LightBuilder':
        """Set the light's attenuation radius (cm). Relevant for Point/Spot."""
        self._attenuation_radius = radius
        self._finalize()
        return self
    
    def cast_shadows(self, enable: bool) -> 'LightBuilder':
        """Enable or disable shadow casting for the light."""
        self._cast_shadows = enable
        self._finalize()
        return self

    def inner_cone_angle(self, angle: float) -> 'LightBuilder':
        """Set the inner cone angle (degrees). Relevant for Spot."""
        self._inner_cone = angle
        self._finalize()
        return self

    def outer_cone_angle(self, angle: float) -> 'LightBuilder':
        """Set the outer cone angle (degrees). Relevant for Spot."""
        self._outer_cone = angle
        self._finalize()
        return self
    
    def use_as_atmospheric_sun(self, enable: bool) -> 'LightBuilder':
        """Set whether this directional light acts as the atmospheric sun."""
        if self.light_type == LightType.DIRECTIONAL:
            self._use_atmospheric_sun = enable
            self._finalize()
        else:
            print(f"Warning: 'use_as_atmospheric_sun' is only applicable to Directional lights.")
        return self
    
    def cast_volumetric_shadow(self, enable: bool) -> 'LightBuilder':
        """Enable or disable volumetric shadow casting (shadows in fog)."""
        self._cast_volumetric_shadow = enable
        self._finalize()
        return self
    
    def light_shafts(self, bloom_scale="cinematic", enable_occlusion: bool = True) -> 'LightBuilder':
        """
        Enable god rays / light shafts.
        
        Args:
            bloom_scale: Bloom intensity preset ("subtle", "cinematic", "dramatic") or numeric value
            enable_occlusion: Enable light shaft occlusion
        """
        self._light_shaft_bloom_scale = bloom_scale
        self._light_shaft_occlusion = enable_occlusion
        self._finalize()
        return self
    
    # Convenience methods
    def radius(self, value: float) -> 'LightBuilder':
        """Convenience alias for attenuation_radius()."""
        return self.attenuation_radius(value)
    
    def cone(self, inner: float, outer: float) -> 'LightBuilder':
        """
        Convenience method to set both cone angles at once.
        
        Args:
            inner: Inner cone angle in degrees
            outer: Outer cone angle in degrees
        """
        self._inner_cone = inner
        self._outer_cone = outer
        self._finalize()
        return self
    
    def attach_to(self, parent_actor: str, socket: str = "") -> 'LightBuilder':
        """
        Attach light to another actor.
        
        Args:
            parent_actor: Name of actor to attach to
            socket: Optional socket name on parent's skeletal mesh
        
        Returns:
            Self for chaining
        """
        self._attach_parent = parent_actor
        self._attach_socket = socket
        self._finalize()
        return self
