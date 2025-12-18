"""
View recent scene setup logs

This script reads the scene_setup.log file and displays recent entries.
"""
import os
import sys

def find_log():
    """Find the scene setup log file"""
    # Local log file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    local_log = os.path.join(script_dir, "scene_setup.log")
    
    if os.path.exists(local_log):
        return local_log
    
    # Fallback: Unreal Engine log
    log_paths = [
        os.path.expandvars(r"%LOCALAPPDATA%\UnrealEngine\5.7\Saved\Logs\FirstVideo.log"),
        os.path.expandvars(r"%USERPROFILE%\AppData\Local\UnrealEngine\5.7\Saved\Logs\FirstVideo.log"),
    ]
    
    for log_path in log_paths:
        if os.path.exists(log_path):
            return log_path
    
    return None

def tail_log(log_file, lines=50):
    """Read the last N lines from the log file"""
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            all_lines = f.readlines()
        
        relevant_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        return relevant_lines
    except Exception as e:
        return [f"Error reading log: {str(e)}"]

def main():
    print("=" * 60)
    print("Scene Setup Logs")
    print("=" * 60)
    
    log_file = find_log()
    
    if not log_file:
        print("✗ Could not find log file")
        print("\nExpected location:")
        print("  - ./scene_setup.log")
        print("  - %LOCALAPPDATA%\\UnrealEngine\\5.7\\Saved\\Logs\\FirstVideo.log")
        return
    
    print(f"✓ Found log file: {log_file}")
    print("\nRecent logs:")
    print("-" * 60)
    
    # Get command line arguments
    num_lines = 50
    if len(sys.argv) > 1:
        try:
            num_lines = int(sys.argv[1])
        except:
            pass
    
    lines = tail_log(log_file, num_lines)
    
    if not lines:
        print("No logs found")
    else:
        for line in lines:
            print(line.rstrip())
    
    print("-" * 60)
    print(f"Showing last {len(lines)} log entries")
    print("\nUsage: python view_unreal_log.py [num_lines]")
    print("  Default: 50 lines")

if __name__ == "__main__":
    main()
