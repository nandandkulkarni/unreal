"""
Quick test script to capture a single frame at origin (frame 0)
"""
import sys
import os

# Add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# This script runs inside Unreal
import unreal
from motion_includes import frame_capture

# Get the most recent sequence
sequence_path = "/Game/Cinematics/Sprint_With_Camera"
sequence = unreal.load_asset(sequence_path)

if sequence:
    output_path = os.path.join(script_dir, "dist", "frames", "test_frame_0.png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"Capturing frame 0 from {sequence_path}...")
    result = frame_capture.capture_frame_now(sequence, 0, output_path)
    
    if result:
        print(f"✓ Success! Frame saved to: {result}")
    else:
        print("✗ Failed to capture frame")
else:
    print(f"✗ Could not load sequence: {sequence_path}")
