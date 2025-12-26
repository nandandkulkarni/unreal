"""
Trigger MetaHuman Animation Setup via Remote Control API
Executes the metahuman_animation_setup_auto.py script in Unreal Engine remotely
"""
import sys
import os

# Add parent directory to path to import unreal_connection
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from unreal_connection import UnrealRemote

def trigger_metahuman_setup(metahuman_name="Pia", use_auto_version=True):
    """
    Trigger MetaHuman animation setup in Unreal Engine via Remote Control
    
    Args:
        metahuman_name: Name of the MetaHuman to setup (default: "Pia")
        use_auto_version: If True, use auto version, else use manual version
    """
    
    print("=" * 80)
    print("  METAHUMAN ANIMATION SETUP - REMOTE TRIGGER")
    print("=" * 80)
    print()
    
    # Determine which script to run
    if use_auto_version:
        script_name = "metahuman_animation_setup_auto.py"
        print(f"[OK] Using AUTO version (recommended)")
    else:
        script_name = "metahuman_animation_setup_manual.py"
        print(f"[OK] Using MANUAL version")
    
    script_path = os.path.join(script_dir, script_name)
    
    if not os.path.exists(script_path):
        print(f"[ERROR] Script not found: {script_path}")
        return False
    
    print(f"[OK] Found script: {script_name}")
    print(f"[OK] Target MetaHuman: {metahuman_name}")
    print()
    
    # Create remote connection
    print("[1] Connecting to Unreal Engine...")
    unreal = UnrealRemote()
    
    if not unreal.is_connected():
        print("[ERROR] Cannot connect to Unreal Engine!")
        print()
        print("Setup steps:")
        print("  1. Open your Unreal Engine project")
        print("  2. Enable Remote Control plugin:")
        print("     Edit → Plugins → search 'Remote Control' → Enable → Restart")
        print("  3. Start WebControl server in Output Log console:")
        print("     WebControl.StartServer")
        print("  4. Verify connection:")
        print("     python unreal_connection.py")
        print()
        return False
    
    print("[OK] Connected to Unreal Engine!")
    print()
    
    # Read the script file
    print("[2] Reading script file...")
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        print(f"[OK] Loaded {len(script_content)} characters")
    except Exception as e:
        print(f"[ERROR] Failed to read script: {e}")
        return False
    
    print()
    
    # Execute the script in Unreal
    print("[3] Executing script in Unreal Engine...")
    print("-" * 80)
    print()
    
    success, result = unreal.execute_python(script_content)
    
    print()
    print("-" * 80)
    
    if success:
        print()
        print("=" * 80)
        print("  [SUCCESS] SCRIPT EXECUTED SUCCESSFULLY!")
        print("=" * 80)
        print()
        print("[INFO] Check Unreal Engine Output Log for detailed results")
        print()
        print("[INFO] NEXT STEPS (Manual):")
        print("1. Open Character Blueprint:")
        print("   /Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter")
        print()
        print("2. Select Mesh component")
        print()
        print("3. Set Skeletal Mesh to MetaHuman body mesh")
        print()
        print(f"4. Set Anim Class to:")
        print(f"   /Game/MetaHumans/{metahuman_name}/Animations/ABP_{metahuman_name}")
        print()
        print("5. Adjust Z-location if needed")
        print()
        print("6. Compile and Save")
        print()
        print("7. Click Play to test")
        print()
        print("=" * 80)
        return True
    else:
        print()
        print("=" * 80)
        print("  [FAILED] SCRIPT EXECUTION FAILED")
        print("=" * 80)
        print()
        print(f"Error: {result}")
        print()
        print("Troubleshooting:")
        print("  - Check Unreal Engine Output Log for error details")
        print("  - Verify MetaHuman 'Pia' is downloaded")
        print("  - Verify Third Person Template content is enabled")
        print("  - Try running the script directly in Unreal Python console")
        print()
        return False

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Trigger MetaHuman Animation Setup in Unreal')
    parser.add_argument('--metahuman', default='Pia', help='MetaHuman name (default: Pia)')
    parser.add_argument('--manual', action='store_true', help='Use manual version instead of auto')
    
    args = parser.parse_args()
    
    success = trigger_metahuman_setup(
        metahuman_name=args.metahuman,
        use_auto_version=not args.manual
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
