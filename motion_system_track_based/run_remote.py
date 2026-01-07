"""
Generic Remote Script Runner for Unreal Engine

This script executes Python scripts inside Unreal Engine via Remote Control.

Usage:
    python run_remote.py <script_name.py>
    python run_remote.py quick_diagnostic.py
"""
import requests
import os
import sys
import time

REMOTE_CONTROL_URL = "http://localhost:30010/remote/object/call"
TIMEOUT_SECONDS = 60

def get_script_directory():
    """Get the directory where this runner script is located"""
    return os.path.dirname(os.path.abspath(__file__))

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
    
    if not os.path.exists(script_path):
        print(f"✗ ERROR: Script not found: {script_path}")
        return False
    
    print("="*80)
    print(f"Remote Script Runner - Unreal Engine")
    print("="*80)
    print(f"Script: {script_name}")
    print()
    
    try:
        with open(script_path, "r", encoding='utf-8') as f:
            script_content = f.read()
    except Exception as e:
        print(f"✗ ERROR: Could not read script: {e}")
        return False
    
    print(f"Sending to Unreal Engine ({len(script_content)} bytes)...")
    
    start_time = time.time()
    status_code, result = execute_python_command(script_content)
    elapsed_time = time.time() - start_time
    
    print("="*80)
    
    if status_code is None:
        print(f"✗ FAILED: {result.get('error', 'Unknown error')}")
        return False
    
    if status_code == 200:
        print(f"✓ SUCCESS (HTTP {status_code}) - {elapsed_time:.2f}s")
        print(f"\nResponse: {result}")
        print("\n" + "="*80)
        print("Check Unreal Engine Output Log for detailed results")
        print("="*80)
        return True
    else:
        print(f"✗ FAILED (HTTP {status_code})")
        print(f"Response: {result}")
        return False

def tail_log(log_path, lines=20):
    """Print the last N lines of a log file"""
    if not os.path.exists(log_path):
        print(f"⚠ Log file not found: {log_path}")
        return

    print("\n" + "-"*80)
    print(f"Log Output ({log_path}):")
    print("-"*80)
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.readlines()
            # If file is small, print all of it
            start_idx = max(0, len(content) - lines)
            for line in content[start_idx:]:
                print(line.rstrip())
    except Exception as e:
        print(f"⚠ Could not read log file: {e}")
    print("-"*80 + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_remote.py <script_name.py> [--log <log_file_path>]")
        sys.exit(1)
    
    script_path_arg = sys.argv[1]
    log_file = None
    
    # Simple arg parsing
    if len(sys.argv) >= 4 and sys.argv[2] == "--log":
        log_file = sys.argv[3]
    
    if not script_path_arg.endswith('.py'):
        script_path_arg += '.py'
    
    success = run_script(script_path_arg)
    
    if success and log_file:
        # Wait a brief moment for file system to sync/flush
        time.sleep(0.5)
        tail_log(log_file, lines=50) # Show last 50 lines
        
    sys.exit(0 if success else 1)
