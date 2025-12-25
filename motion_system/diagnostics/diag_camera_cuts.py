"""
Diagnostic script to check camera cuts in the current sequence
"""
import unreal

def check_camera_cuts():
    # Get current sequence
    sequence = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
    
    if not sequence:
        print("No sequence is currently open")
        return
    
    print(f"\nSequence: {sequence.get_name()}")
    print(f"Playback range: {sequence.get_playback_start()} - {sequence.get_playback_end()}")
    
    # Find camera cuts track
    camera_cut_track = None
    all_tracks = sequence.find_tracks_by_type(unreal.MovieSceneCameraCutTrack)
    
    print(f"\nFound {len(all_tracks)} camera cut track(s)")
    
    for track in all_tracks:
        print(f"\nCamera Cut Track: {track.get_display_name()}")
        sections = track.get_sections()
        print(f"  Sections: {len(sections)}")
        
        for i, section in enumerate(sections):
            start = section.get_start_frame()
            end = section.get_end_frame()
            print(f"  Section {i+1}: frames {start} - {end}")
            
            # Try to get camera binding
            try:
                binding_id = section.get_camera_binding_id()
                print(f"    Binding ID: {binding_id}")
            except Exception as e:
                print(f"    Could not get binding: {e}")

if __name__ == "__main__":
    check_camera_cuts()
