"""
View recent Unreal Engine Python logs

This script reads the Unreal Engine log file and displays recent Python-related entries.
"""
import os
import sys

def find_unreal_log():
    """Find the most recent Unreal Engine log file"""
    # Common log locations
    log_paths = [
        os.path.expandvars(r"%LOCALAPPDATA%\UnrealEngine\5.7\Saved\Logs"),
        os.path.expandvars(r"%USERPROFILE%\AppData\Local\UnrealEngine\5.7\Saved\Logs"),
    ]
    
    for log_dir in log_paths:
        if os.path.exists(log_dir):
            # Find FirstVideo.log (project log)
            project_log = os.path.join(log_dir, "FirstVideo.log")
            if os.path.exists(project_log):
                return project_log
    
    return None

def tail_log(log_file, lines=50, filter_python=True):
    """Read the last N lines from the log file"""
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            all_lines = f.readlines()
            
        if filter_python:
            # Filter for Python-related logs
            python_lines = [line for line in all_lines if 'LogPython' in line or 'Python' in line or 'Error:' in line]
            relevant_lines = python_lines[-lines:] if len(python_lines) > lines else python_lines
        else:
            relevant_lines = all_lines[-lines:]
        
        return relevant_lines
    except Exception as e:
        return [f"Error reading log: {str(e)}"]

def main():
    print("=" * 60)
    print("Unreal Engine Python Logs")
    print("=" * 60)
    
    log_file = find_unreal_log()
    
    if not log_file:
        print("✗ Could not find Unreal Engine log file")
        print("\nExpected locations:")
        print("  - %LOCALAPPDATA%\\UnrealEngine\\5.7\\Saved\\Logs\\FirstVideo.log")
        print("\nMake sure:")
        print("  1. Unreal Engine is running")
        print("  2. The FirstVideo project is open")
        return
    
    print(f"✓ Found log file: {log_file}")
    print("\nRecent Python logs:")
    print("-" * 60)
    
    # Get command line arguments
    num_lines = 50
    if len(sys.argv) > 1:
        try:
            num_lines = int(sys.argv[1])
        except:
            pass
    
    lines = tail_log(log_file, num_lines, filter_python=True)
    
    if not lines:
        print("No Python logs found in recent entries")
    else:
        for line in lines:
            print(line.rstrip())
    
    print("-" * 60)
    print(f"Showing last {len(lines)} Python-related log entries")
    print("\nUsage: python view_unreal_log.py [num_lines]")
    print("  Default: 50 lines")

if __name__ == "__main__":
    main()
