import unreal
import sys

def focus_viewport():
    print("Moving Viewport Camera...")
    
    location = unreal.Vector(0, -3000, 2000)
    rotation = unreal.Rotator(-25, 90, 0) # Pitch, Yaw, Roll
    
    try:
        unreal.EditorLevelLibrary.set_level_viewport_camera_info(location, rotation)
        print("✓ Viewport camera moved to view the Garden.")
    except Exception as e:
        print(f"✗ Failed to move viewport: {e}")

if __name__ == "__main__":
    focus_viewport()
