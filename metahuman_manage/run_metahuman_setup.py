"""
Script runner for MetaHuman Animation Setup
Executes the metahuman_animation_setup_auto.py script with proper module reloading
"""
import unreal
import os
import sys
import importlib

# Handle path for remote execution where __file__ might be missing
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    script_dir = r"C:\UnrealProjects\Coding\unreal\metahuman_manage"

# Add script directory to path
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

def log_header(message):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"  {message}")
    print("=" * 80 + "\n")

def log(message):
    """Print a log message"""
    print(f"  {message}")

def run_metahuman_setup(metahuman_name="Pia", use_auto_version=True):
    """
    Run the MetaHuman animation setup script
    
    Args:
        metahuman_name: Name of the MetaHuman to setup (default: "Pia")
        use_auto_version: If True, use the auto version, else use manual version
    """
    
    log_header("METAHUMAN ANIMATION SETUP")
    
    # Determine which script to run
    if use_auto_version:
        script_name = "metahuman_animation_setup_auto.py"
        log("Using AUTO version (recommended)")
    else:
        script_name = "metahuman_animation_setup_manual.py"
        log("Using MANUAL version")
    
    script_path = os.path.join(script_dir, script_name)
    
    if not os.path.exists(script_path):
        log(f"✗ Script not found: {script_path}")
        return False
    
    log(f"✓ Found script: {script_name}")
    log(f"✓ Target MetaHuman: {metahuman_name}")
    
    try:
        # Read and execute the script
        log("\nExecuting script...")
        log("-" * 80)
        
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        # Create a namespace for execution
        script_globals = {
            '__name__': '__main__',
            '__file__': script_path,
        }
        
        # Execute the script
        exec(script_content, script_globals)
        
        log("-" * 80)
        log_header("SETUP COMPLETE")
        
        log("\n📋 NEXT STEPS (Manual):")
        log("1. Open Character Blueprint: /Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter")
        log("2. Select Mesh component")
        log("3. Set Skeletal Mesh to MetaHuman body mesh")
        log(f"4. Set Anim Class to: /Game/MetaHumans/{metahuman_name}/Animations/ABP_{metahuman_name}")
        log("5. Adjust Z-location if needed")
        log("6. Compile and Save")
        log("7. Click Play to test\n")
        
        return True
        
    except Exception as e:
        log(f"\n✗ Error executing script: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_with_custom_metahuman(metahuman_name):
    """
    Run setup for a custom MetaHuman name
    
    Args:
        metahuman_name: Name of the MetaHuman (e.g., "Ada", "Pia", "Quinn")
    """
    log_header(f"CUSTOM METAHUMAN SETUP: {metahuman_name}")
    
    # Note: The actual script will need to be modified to accept a parameter
    # For now, this runs the default script
    log("⚠ Note: Script currently configured for 'Pia'")
    log("   To use a different MetaHuman, edit the script's METAHUMAN_NAME variable")
    
    return run_metahuman_setup(metahuman_name=metahuman_name, use_auto_version=True)

if __name__ == "__main__":
    # Default: Run auto version for Pia
    success = run_metahuman_setup(metahuman_name="Pia", use_auto_version=True)
    
    if success:
        print("\n✅ Script executed successfully!")
    else:
        print("\n❌ Script execution failed!")
