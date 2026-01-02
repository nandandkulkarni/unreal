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
Logging utilities for track-based motion system
"""
from datetime import datetime
import os


# Default log directory and file
LOG_DIR = r"C:\UnrealProjects\Coding\unreal\motion_system_track_based\dist"
LOG_FILE = os.path.join(LOG_DIR, "scene_setup.log")


def log(message, log_file=None):
    """Print and write to log file"""
    if log_file is None:
        log_file = LOG_FILE
    
    print(message)
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"Warning: Could not write to log: {e}")


def log_header(title):
    """Log a section header"""
    log("=" * 60)
    log(title)
    log("=" * 60)

