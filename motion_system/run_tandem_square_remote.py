"""
Remote Runner for Tandem Square Sequence
"""
import sys
import os

# Ensure we can import unreal_connection from parent dir
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

from unreal_connection import UnrealRemote

def get_log_timestamp():
    """Get current timestamp from log file to mark execution start"""
    log_path = "C:/UnrealProjects/ThirdPerson/Saved/Logs/ThirdPerson.log"
    if not os.path.exists(log_path):
        return None
    
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        f.seek(0, 2)  # Go to end
        size = f.tell()
        read_size = min(size, 5000)  # Read last 5KB
        f.seek(size - read_size)
        lines = f.readlines()
    
    # Find the most recent timestamp
    for line in reversed(lines):
        if line.startswith("["):
            # Extract timestamp like [2025.12.29-23.56.26:847]
            try:
                timestamp_str = line.split("]")[0][1:]
                return timestamp_str
            except:
                pass
    return None

def check_logs_for_errors(log_path, since_timestamp=None):
    """Check logs for Python errors after a specific timestamp"""
    if not os.path.exists(log_path):
        return None, []
    
    import time
    time.sleep(2)  # Wait for logs to flush
    
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        f.seek(0, 2)
        size = f.tell()
        read_size = min(size, 300000)  # Read last 300KB
        f.seek(size - read_size)
        lines = f.readlines()
    
    errors = []
    current_error = []
    capture = False
    current_timestamp = None
    
    for line in lines:
        # Extract timestamp from line
        if line.startswith("["):
            try:
                line_timestamp = line.split("]")[0][1:]
                current_timestamp = line_timestamp
            except:
                pass
        
        # Skip lines before our start timestamp
        if since_timestamp and current_timestamp and current_timestamp < since_timestamp:
            continue
        
        if "LogPython: Error:" in line or "LogPython: FATAL ERROR:" in line:
            if current_error:
                errors.append('\n'.join(current_error))
            current_error = [line.strip()]
            capture = True
        elif capture:
            if line.strip() and not line.startswith("["):
                current_error.append(line.strip())
            elif line.startswith("[") and "LogPython" not in line:
                capture = False
                
    if current_error:
        errors.append('\n'.join(current_error))
    
    # Get most recent error
    latest_error = errors[-1] if errors else None
    return latest_error, errors

def main():
    script_path = os.path.join(script_dir, "unreal_run_tandem_square.py")
    log_path = "C:/UnrealProjects/ThirdPerson/Saved/Logs/ThirdPerson.log"
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        if retry_count > 0:
            print(f"\n{'='*60}")
            print(f"RETRY ATTEMPT {retry_count}/{max_retries}")
            print(f"{'='*60}")
        else:
            print("=" * 60)
            print("LAUNCHING TANDEM SQUARE")
            print("=" * 60)
        
        # Get timestamp BEFORE execution
        start_timestamp = get_log_timestamp()
        print(f"Execution start timestamp: {start_timestamp}")
        
        unreal = UnrealRemote()
        if not unreal.is_connected():
            print("Error: Could not connect to Unreal Engine.")
            return
    
        print("Executing inside Unreal...")
        success, result = unreal.execute_python_file(script_path)
        
        if not success:
            print(f"\n✗ FAILED: {result}")
            return
        
        print("\n✓ Remote execution completed.")
        print("Checking logs for runtime errors...")
        
        latest_error, all_errors = check_logs_for_errors(log_path, since_timestamp=start_timestamp)
        
        if not latest_error:
            print("\n" + "="*60)
            print("✅ SUCCESS - No errors detected!")
            print("="*60)
            print("Check Unreal Editor for the running sequence.")
            return
        
        # Error detected
        print("\n" + "="*60)
        print("⚠️  RUNTIME ERROR DETECTED")
        print("="*60)
        print(latest_error)
        print("="*60)
        
        # Extract error type
        if "AttributeError" in latest_error:
            print("\n💡 Detected: Missing function/attribute")
        elif "ImportError" in latest_error or "ModuleNotFoundError" in latest_error:
            print("\n💡 Detected: Import error")
        elif "NameError" in latest_error:
            print("\n💡 Detected: Undefined variable")
        else:
            print("\n💡 Detected: Runtime error")
        
        retry_count += 1
        
        if retry_count < max_retries:
            print(f"\n⏳ Waiting for manual fix... (will retry in 5 seconds)")
            print("   Fix the error in the code, then this will auto-retry.")
            import time
            time.sleep(5)
        else:
            print(f"\n❌ Max retries ({max_retries}) reached. Please fix the error manually.")
            return

if __name__ == "__main__":
    main()


