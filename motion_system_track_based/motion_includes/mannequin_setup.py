# Simple inline logger functions for motion_includes
# This avoids import conflicts with other logger modules in the Python path

def log(message, log_file=None):
    """Print message"""
    print(message)

def log_header(title):
    """Print header"""
    print("=" * 60)
    print(title)
    print("=" * 60)


"""
Mannequin/character creation and configuration
"""
import unreal
from .assets import Characters, Shapes, Materials
# import logger
# from logger import log, log_header


def create_mannequin(mannequin_name, location=None, rotation=None, mesh_path=None, mesh_rotation=None):
    """Create a skeletal mesh actor (Belica character)"""
    log_header("STEP 4: Creating mannequin")

    if location is None:
        location = unreal.Vector(0, 0, 0)  # On the floor
    if rotation is None:
        # Standard Unreal forward is X+ (Yaw=0)
        rotation = unreal.Rotator(pitch=0.0, yaw=0.0, roll=0.0)

    # Detect if path is a Blueprint
    is_blueprint = False
    if mesh_path and ("BP_" in mesh_path or "_C" in mesh_path):
        is_blueprint = True
        
    if is_blueprint:
        # Load the Blueprint Class
        # Append _C if not present for class loading
        class_path = mesh_path
        if not class_path.endswith("_C"):
            class_path += "_C"
            
        actor_class = unreal.load_class(None, class_path)
        if actor_class:
            mannequin = unreal.EditorLevelLibrary.spawn_actor_from_class(
                actor_class,
                location,
                rotation
            )
            if mannequin:
                mannequin.set_actor_label(mannequin_name)
                mannequin.tags.append("MotionSystemActor")
                
                log(f"✓ Blueprint Actor created: {mannequin_name}")
                return mannequin
        else:
            log(f"✗ ERROR: Could not load Blueprint class: {class_path}")
            raise Exception("Blueprint load failed")

    # Regular Skeletal Mesh Logic
    skeletal_mesh = None
    if mesh_path:
        skeletal_mesh = unreal.load_object(None, mesh_path)
    
    if not skeletal_mesh:
        skeletal_mesh = unreal.load_object(None, Characters.BELICA.path)

    if not skeletal_mesh:
        # Fallback to Quinn if Belica is missing
        skeletal_mesh = unreal.load_object(None, Characters.QUINN_SIMPLE.path)

    if not skeletal_mesh:
        # Secondary fallback
        skeletal_mesh = unreal.load_object(
            None, Characters.QUINN_THIRD_PERSON.path)

    if skeletal_mesh:
        # Spawn a SkeletalMeshActor
        mannequin = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.SkeletalMeshActor,
            location,
            rotation
        )

        if mannequin:
            mannequin.set_actor_label(mannequin_name)
            mannequin.tags.append("MotionSystemActor")

            # Set the skeletal mesh on the component
            skel_comp = mannequin.skeletal_mesh_component
            skel_comp.set_skinned_asset_and_update(skeletal_mesh)
            
            if mesh_rotation:
                skel_comp.set_editor_property("relative_rotation", mesh_rotation)

            log(f"✓ Mannequin created: {mannequin_name}")
            log(f"  Location: {location}")
            log(f"  Mesh: {skeletal_mesh.get_name()}")
            log(f"  Rotation: Pitch={rotation.pitch}, Yaw={rotation.yaw}, Roll={rotation.roll}")

            # Debug: Check mannequin's forward direction
            forward_vec = mannequin.get_actor_forward_vector()
            log(f"  Forward Vector: X={forward_vec.x:.3f}, Y={forward_vec.y:.3f}, Z={forward_vec.z:.3f}")

            return mannequin
        else:
            log("✗ ERROR: Failed to spawn mannequin")
            raise Exception("Mannequin spawn failed")
    else:
        log("✗ ERROR: Could not load skeletal mesh")
        raise Exception("Skeletal mesh not found")
def spawn_thick_line(name, start, end, thickness_cm=50.0, color_name="Red"):
    """Draw a line between two points using a scaled Cube"""
    try:
        cube_mesh = unreal.load_object(None, Shapes.CUBE)
        if not cube_mesh:
            return None

        # 1. Calc distance for length
        distance = unreal.MathLibrary.vector_distance(start, end)
        
        # 2. Calc midpoint for location (pivot is center)
        midpoint = unreal.Vector(
            (start.x + end.x) / 2.0,
            (start.y + end.y) / 2.0,
            (start.z + end.z) / 2.0
        )
        
        # 3. Calc rotation to point from start to end
        rotation = unreal.MathLibrary.find_look_at_rotation(start, end)
        
        # Spawn
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, midpoint, rotation)
        if actor:
            actor.set_actor_label(name)
            smc = actor.static_mesh_component
            smc.set_static_mesh(cube_mesh)
            
            # 4. Scale: Cube is 100cm. 
            # X = Length, Y = Thickness, Z = Height (flat)
            scale = unreal.Vector(distance / 100.0, thickness_cm / 100.0, 0.01)
            actor.set_actor_scale3d(scale)
            
            # 5. Apply Material
            mat_path = Materials.get_color(color_name)
            mat = unreal.load_object(None, mat_path)
            if mat:
                smc.set_material(0, mat)
            
            actor.tags.append("MotionSystemActor")
            return actor
    except Exception as e:
        log(f"⚠ Failed to spawn thick line '{name}': {e}")
    return None


def add_axis_origin(location=None):
    """Spawn thick visual markers for X (Red) and Y (Green) axes"""
    if location is None:
        location = unreal.Vector(0, 0, 1) # Slightly above floor

    # Origin Text
    origin_text = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.TextRenderActor, location, unreal.Rotator(0,0,0))
    if origin_text:
        origin_text.set_actor_label("Origin_Marker")
        origin_text.text_render.set_text("ORIGIN (0,0)")
        origin_text.text_render.set_world_size(50)
        origin_text.text_render.set_text_render_color(unreal.Color(255,255,255,255))
        origin_text.tags.append("MotionSystemActor")

    # X-Axis (Red) - 10 meters North
    end_x = unreal.Vector(location.x + 1000, location.y, location.z)
    spawn_thick_line("X_Axis_Thick_Red", location, end_x, 50.0, "Red")

    # Y-Axis (Green) - 10 meters East
    end_y = unreal.Vector(location.x, location.y + 1000, location.z)
    spawn_thick_line("Y_Axis_Thick_Green", location, end_y, 50.0, "Green")
    
    log("✓ Added Thick Axis Visual Markers (50cm width: X-North-Red, Y-East-Green)")

