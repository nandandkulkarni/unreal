"""
Create a Blueprint with a Remote-Controllable Render Function

This Blueprint will wrap the render logic so it can be triggered
via a simple Remote Control API call.

Run this INSIDE Unreal: Tools → Execute Python Script
"""

import unreal

def create_render_blueprint():
    """Create a Blueprint Actor with a function to trigger video render"""
    
    print("=" * 60)
    print("Creating Remote-Controllable Render Blueprint")
    print("=" * 60)
    
    # Note: Creating Blueprints with Python in UE5 is limited
    # We'll create a Python-based Actor instead that can be called remotely
    
    # Create a new Blueprint class
    asset_path = "/Game/RemoteRenderController"
    package_path = "/Game/"
    asset_name = "RemoteRenderController"
    
    # Try to load existing asset first
    existing_asset = unreal.load_asset(asset_path)
    if existing_asset:
        print(f"✓ Found existing asset: {asset_path}")
        print("  You can call 'TriggerRender' function on this object remotely")
        return existing_asset
    
    print("\n📝 To create a remote-controllable render trigger:")
    print("\n1. Create a Blueprint Actor:")
    print("   - Content Browser → Right-click → Blueprint Class")
    print("   - Choose Actor as parent")
    print("   - Name it: RemoteRenderController")
    
    print("\n2. Add a function named 'TriggerRender':")
    print("   - Open the Blueprint")
    print("   - Functions panel → + Function")
    print("   - Name it: TriggerRender")
    
    print("\n3. Add this Python code to the function:")
    print("   - Add node: 'Execute Python Command'")
    print("   - Python Command input:")
    
    python_code = """
import unreal
sequence_path = "/Game/CharacterWalkSequence"
sequence_asset = unreal.load_asset(sequence_path)
subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
queue = subsystem.get_queue()
job = queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
job.sequence = unreal.SoftObjectPath(sequence_path)
job.map = unreal.SoftObjectPath("/Game/Main")
config = job.get_configuration()
output_setting = config.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
output_setting.output_directory = unreal.DirectoryPath("C:/U/CinematicPipeline/Saved/VideoCaptures")
output_setting.file_name_format = "{sequence_name}"
output_setting.output_resolution = unreal.IntPoint(1920, 1080)
output_setting.output_frame_rate = unreal.FrameRate(30, 1)
video_setting = config.find_or_add_setting_by_class(unreal.MoviePipelineAppleProResOutput)
subsystem.render_queue_with_executor(unreal.MoviePipelinePIEExecutor.static_class())
"""
    
    print(f"\n{python_code}")
    
    print("\n4. Place the Blueprint in the level:")
    print("   - Drag RemoteRenderController into Main.umap")
    print("   - Name the instance: RenderController")
    
    print("\n5. Expose to Remote Control:")
    print("   - Window → Developer Tools → Remote Control Web App")
    print("   - In outliner, find RenderController")
    print("   - Right-click → Expose to Remote Control")
    
    print("\n6. Test remotely:")
    print("   python remote_render_video_v2.py")
    
    print("\n" + "=" * 60)
    print("NOTE: Blueprint creation with Python is limited in UE5")
    print("Please follow the manual steps above")
    print("=" * 60)

if __name__ == "__main__":
    create_render_blueprint()
