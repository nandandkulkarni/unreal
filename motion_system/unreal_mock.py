"""
Mock classes for Unreal Engine Python API
Allows motion_planner.py to run in standard Python environments (visualizer)
"""

class Vector:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z
    def __repr__(self):
        return f"Vector(x={self.x}, y={self.y}, z={self.z})"

class Rotator:
    def __init__(self, pitch=0.0, yaw=0.0, roll=0.0):
        self.pitch = pitch
        self.yaw = yaw
        self.roll = roll
    def __repr__(self):
        return f"Rotator(p={self.pitch}, y={self.yaw}, r={self.roll})"

class MathLibrary:
    @staticmethod
    def get_forward_vector(rot):
        import math
        yaw_rad = math.radians(rot.yaw)
        return Vector(math.cos(yaw_rad), math.sin(yaw_rad), 0)
    
    @staticmethod
    def get_right_vector(rot):
        import math
        yaw_rad = math.radians(rot.yaw + 90)
        return Vector(math.cos(yaw_rad), math.sin(yaw_rad), 0)

# Empty containers for Unreal classes we don't need to mock fully
class StaticMeshActor: pass
class CineCameraActor: pass
class DirectionalLight: pass
class SkyLight: pass
class SpotLight: pass
class PointLight: pass
class RectLight: pass
class SkeletalAnimationTrack: pass
class MovieScene3DTransformTrack: pass
class MockActor:
    def __init__(self, label=""):
        self.label = label
        self.tags = []
        self._loc = Vector(0,0,0)
    def set_actor_label(self, label): self.label = label
    def get_actor_label(self): return self.label
    def set_actor_location(self, loc, sweep=False, teleport=False): self._loc = loc
    def set_actor_rotation(self, rot, teleport=False): pass
    def set_actor_scale3d(self, scale): pass
    def get_actor_location(self): return self._loc
    def get_actor_rotation(self): return Rotator(0,0,0)
    def get_actor_forward_vector(self): return Vector(1,0,0)
    def attach_to_actor(self, *args, **kwargs): pass
    @property
    def static_mesh_component(self): return self
    @property
    def skeletal_mesh_component(self): return self
    @property
    def text_render(self): return self
    def set_skinned_asset_and_update(self, mesh): pass
    def set_static_mesh(self, mesh): pass
    def set_material(self, index, mat): pass
    def set_editor_property(self, key, val): pass
    def set_text(self, text): pass
    def set_world_size(self, size): pass
    def set_text_render_color(self, color): pass
    def get_name(self): return "MockObject"

class SkeletalMeshActor: pass
class TextRenderActor: pass
class Vector4: pass
class Color:
    def __init__(self, r=0, g=0, b=0, a=255): pass

class MathLibrary:
    @staticmethod
    def get_forward_vector(rot):
        import math
        yaw_rad = math.radians(rot.yaw)
        return Vector(math.cos(yaw_rad), math.sin(yaw_rad), 0)
    
    @staticmethod
    def get_right_vector(rot):
        import math
        yaw_rad = math.radians(rot.yaw + 90)
        return Vector(math.cos(yaw_rad), math.sin(yaw_rad), 0)

    @staticmethod
    def vector_distance(v1, v2):
        import math
        return math.sqrt((v1.x-v2.x)**2 + (v1.y-v2.y)**2 + (v1.z-v2.z)**2)
    
    @staticmethod
    def find_look_at_rotation(start, end): return Rotator(0,0,0)

class EditorLevelLibrary:
    @staticmethod
    def get_all_level_actors(): return []
    @staticmethod
    def spawn_actor_from_class(cls, loc, rot): return MockActor()
    @staticmethod
    def destroy_actor(actor): pass

class EditorAssetLibrary:
    @staticmethod
    def save_loaded_asset(asset): return True

class LevelSequenceEditorBlueprintLibrary:
    @staticmethod
    def open_level_sequence(seq): pass
    @staticmethod
    def set_lock_camera_cut_to_viewport(lock): pass
    @staticmethod
    def refresh_current_level_sequence(): pass
    @staticmethod
    def set_current_time(time): pass
    @staticmethod
    def play(): pass

def load_asset(path): return object()
def load_object(outer, path): return object()

class MovieSceneSequenceExtensions:
    @staticmethod
    def add_possessable(seq, actor): return MockActor()

class MovieSceneObjectBindingID:
    def set_editor_property(self, key, val): pass

class CameraLookatTrackingSettings:
    def __init__(self):
        self.enable_look_at_tracking = False
        self.actor_to_track = None
        self.allow_roll = False
        self.look_at_tracking_interp_speed = 0.0
        self.relative_offset = Vector(0,0,0)
