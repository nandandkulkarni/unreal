"""
Generic Remote Script Runner for Unreal Engine

This script executes Python scripts inside Unreal Engine via Remote Control.
It can run any script in the root-motion-matching-poc folder.

Usage:
    python run_remote.py <script_name.py>
    python run_remote.py create_motion_database.py
    
Or run without arguments to see available scripts.
"""
import requests
import os
import sys
import time

# Remote Control configuration
REMOTE_CONTROL_URL = "http://localhost:30010/remote/object/call"
TIMEOUT_SECONDS = 60

def get_script_directory():
    """Get the directory where this runner script is located"""
    return os.path.dirname(os.path.abspath(__file__))

def list_available_scripts():
    """List all Python scripts in the current directory"""
    script_dir = get_script_directory()
    scripts = []
    
    for file in os.listdir(script_dir):
        if file.endswith('.py') and file != 'run_remote.py':
            scripts.append(file)
    
    return sorted(scripts)

def execute_python_command(command, timeout=TIMEOUT_SECONDS):
    """Execute Python command in Unreal via Remote Control"""
    payload = {
        "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
        "functionName": "ExecutePythonCommand",
        "parameters": {"PythonCommand": command}
    }
    
    try:
        response = requests.put(
            REMOTE_CONTROL_URL, 
            headers={'Content-Type': 'application/json'}, 
            json=payload,
            timeout=timeout
        )
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return None, {"error": "Could not connect to Unreal Engine"}
    except requests.exceptions.Timeout:
        return None, {"error": f"Request timed out after {timeout} seconds"}
    except Exception as e:
        return None, {"error": str(e)}

def run_script(script_name):
    """Run a Python script inside Unreal Engine"""
    script_dir = get_script_directory()
    script_path = os.path.join(script_dir, script_name)
    
    # Check if script exists
    if not os.path.exists(script_path):
        print(f"✗ ERROR: Script not found: {script_path}")
        print("\nAvailable scripts:")
        for script in list_available_scripts():
            print(f"  - {script}")
        return False
    
    print("="*80)
    print(f"Remote Script Runner - Unreal Engine")
    print("="*80)
    print(f"Script: {script_name}")
    print(f"Path: {script_path}")
    print(f"Remote Control: {REMOTE_CONTROL_URL}")
    print("="*80)
    print()
    
    # Read the script content
    try:
        with open(script_path, "r", encoding='utf-8') as f:
            script_content = f.read()
    except Exception as e:
        print(f"✗ ERROR: Could not read script: {e}")
        return False
    
    print(f"Script loaded ({len(script_content)} bytes)")
    print("Sending to Unreal Engine...")
    print()
    
    # Execute the script
    start_time = time.time()
    status_code, result = execute_python_command(script_content)
    elapsed_time = time.time() - start_time
    
    # Display results
    print("="*80)
    print("Execution Result")
    print("="*80)
    
    if status_code is None:
        print(f"✗ FAILED: {result.get('error', 'Unknown error')}")
        print()
        print("Troubleshooting:")
        print("1. Ensure Unreal Engine is running")
        print("2. Enable 'Remote Control' plugin in Unreal")
        print("3. Verify HTTP server is running on port 30010")
        print("4. Check Windows Firewall settings")
        return False
    
    if status_code == 200:
        print(f"✓ SUCCESS (HTTP {status_code})")
        print(f"Execution time: {elapsed_time:.2f} seconds")
        print()
        print("Response:")
        print(result)
        print()
        print("="*80)
        print("Check Unreal Engine Output Log for detailed results")
        print("="*80)
        return True
    else:
        print(f"✗ FAILED (HTTP {status_code})")
        print(f"Response: {result}")
        return False

def show_usage():
    """Display usage information"""
    print("="*80)
    print("Remote Script Runner for Unreal Engine")
    print("="*80)
    print()
    print("Usage:")
    print("  python run_remote.py <script_name.py>")
    print()
    print("Examples:")
    print("  python run_remote.py create_motion_database.py")
    print()
    print("Available scripts in this directory:")
    
    scripts = list_available_scripts()
    if scripts:
        for script in scripts:
            print(f"  - {script}")
    else:
        print("  (No scripts found)")
    
    print()
    print("="*80)

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        show_usage()
        return 0
    
    script_name = sys.argv[1]
    
    # Add .py extension if not provided
    if not script_name.endswith('.py'):
        script_name += '.py'
    
    success = run_script(script_name)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
