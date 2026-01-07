"""
Check Track and Line Dimensions
Reports actual sizes of track and lane markings
"""
import unreal
import sys

# ==============================================================================
# LOGGING
# ==============================================================================
LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\dimensions.log"

class FileLogger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, 'w', encoding='utf-8')
        
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = FileLogger(LOG_FILE_PATH)

print("=" * 80)
print("TRACK DIMENSIONS CHECK")
print("=" * 80)

world = unreal.EditorLevelLibrary.get_editor_world()
all_actors = unreal.EditorLevelLibrary.get_all_level_actors()

# Find track segments
track_segments = []
lane_lines = []
start_line = None

for actor in all_actors:
    label = actor.get_actor_label()
    if "SimpleTrack_Segment" in label:
        track_segments.append(actor)
    elif "LaneLine_Dash" in label:
        lane_lines.append(actor)
    elif "StartFinishLine" in label:
        start_line = actor

print(f"\nFound {len(track_segments)} track segments")
print(f"Found {len(lane_lines)} lane line dashes")
print(f"Found start/finish line: {'Yes' if start_line else 'No'}")

if track_segments:
    print("\n" + "=" * 80)
    print("TRACK DIMENSIONS")
    print("=" * 80)
    
    # Get first segment to check dimensions
    segment = track_segments[0]
    scale = segment.get_actor_scale3d()
    
    # Scale is in Unreal units (1 unit = 1cm)
    # Our cubes are 100x100x100 base size
    length_per_segment = scale.x * 100  # cm
    width = scale.y * 100  # cm
    height = scale.z * 100  # cm
    
    total_length = len(track_segments) * length_per_segment
    
    print(f"Individual Segment:")
    print(f"  Length: {length_per_segment:.0f}cm = {length_per_segment/100:.1f}m")
    print(f"  Width: {width:.0f}cm = {width/100:.1f}m")
    print(f"  Height: {height:.1f}cm")
    
    print(f"\nTotal Track:")
    print(f"  Length: {total_length:.0f}cm = {total_length/100:.0f}m")
    print(f"  Width: {width:.0f}cm = {width/100:.1f}m")
    print(f"  Segments: {len(track_segments)}")

if lane_lines:
    print("\n" + "=" * 80)
    print("LANE LINE DIMENSIONS")
    print("=" * 80)
    
    # Get first dash to check size
    dash = lane_lines[0]
    decal_comp = dash.decal
    
    # Get decal size
    decal_size = decal_comp.get_editor_property("decal_size")
    
    # Decal size is in half-extents (radius)
    dash_length = decal_size.x * 2  # Full length
    line_width = decal_size.y * 2   # Full width
    
    print(f"Dashed Center Line:")
    print(f"  Dash length: {dash_length:.0f}cm = {dash_length/100:.1f}m")
    print(f"  Line width: {line_width:.0f}cm = {line_width/100:.2f}m")
    print(f"  Number of dashes: {len(lane_lines)}")

if start_line:
    print("\n" + "=" * 80)
    print("START/FINISH LINE DIMENSIONS")
    print("=" * 80)
    
    decal_comp = start_line.decal
    decal_size = decal_comp.get_editor_property("decal_size")
    
    line_thickness = decal_size.x * 2
    line_width = decal_size.y * 2
    
    print(f"Start/Finish Line:")
    print(f"  Thickness: {line_thickness:.0f}cm = {line_thickness/100:.1f}m")
    print(f"  Width: {line_width:.0f}cm = {line_width/100:.1f}m")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
if track_segments:
    print(f"✓ Track: {total_length/100:.0f}m long × {width/100:.1f}m wide")
if lane_lines:
    print(f"✓ Lane lines: {line_width/100:.2f}m wide, {dash_length/100:.1f}m dashes")
if start_line:
    print(f"✓ Start line: {line_thickness/100:.1f}m thick × {line_width/100:.1f}m wide")
