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
Frame Capture Utility - Capture frames from sequences for visual verification
Uses tick callbacks to ensure proper rendering before capture
"""
import unreal
# from logger import log
import os


class FrameCaptureState:
    """State management for async frame capture"""
    def __init__(self, sequence, frames, output_dir, movie_name):
        self.sequence = sequence
        self.frames = frames
        self.output_dir = output_dir
        self.movie_name = movie_name
        self.current_index = 0
        self.captured_paths = []
        self.tick_handle = None
        self.ticks_waited = 0
        self.state = "init"  # init, waiting, capturing, done
        
        # Create output directory
        self.movie_dir = os.path.join(output_dir, movie_name)
        os.makedirs(self.movie_dir, exist_ok=True)
        
        # Delete old frames before capturing new ones
        for frame in frames:
            old_frame_path = os.path.join(self.movie_dir, f"frame_{frame:04d}.png")
            if os.path.exists(old_frame_path):
                try:
                    os.remove(old_frame_path)
                    log(f"  Deleted old frame: {old_frame_path}")
                except Exception as e:
                    log(f"  Warning: Could not delete old frame {old_frame_path}: {e}")


def capture_frame_now(sequence, frame_number, output_path, width=1920, height=1080):
    """
    Synchronously capture a single frame - freezes sequencer and takes screenshot immediately.
    Use this for testing/debugging when you need an immediate capture.
    
    Args:
        sequence: LevelSequence object
        frame_number: Frame number to capture
        output_path: Full path for output image
        width: Image width in pixels
        height: Image height in pixels
    
    Returns:
        output_path if successful, None otherwise
    """
    try:
        log(f"\n  Freezing sequencer at frame {frame_number}...")
        
        # Open sequence
        unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(sequence)
        
        # Pause playback
        unreal.LevelSequenceEditorBlueprintLibrary.pause()
        
        # Set to specific frame
        unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(frame_number)
        
        # Lock viewport to camera cuts
        unreal.LevelSequenceEditorBlueprintLibrary.set_lock_camera_cut_to_viewport(True)
        
        # Force refresh
        unreal.LevelSequenceEditorBlueprintLibrary.refresh_current_level_sequence()
        
        # Take screenshot immediately
        unreal.AutomationLibrary.take_high_res_screenshot(width, height, output_path)
        
        log(f"  ✓ Screenshot captured: {output_path}")
        return output_path
        
    except Exception as e:
        log(f"  ✗ Failed to capture frame {frame_number}: {e}")
        import traceback
        log(traceback.format_exc())
        return None


def _capture_tick_callback(delta_time, state):
    """Tick callback for frame capture - called each editor frame"""
    try:
        if state.state == "init":
            # Open sequence and prepare
            unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(state.sequence)
            unreal.LevelSequenceEditorBlueprintLibrary.set_lock_camera_cut_to_viewport(True)
            state.state = "waiting"
            state.ticks_waited = 0
            log(f"\n{'='*60}")
            log(f"CAPTURING VERIFICATION FRAMES")
            log(f"{'='*60}")
            log(f"Output directory: {state.movie_dir}")
            log(f"Frames to capture: {state.frames}")
            return
        
        if state.state == "waiting":
            # Set frame and wait for render
            if state.ticks_waited == 0:
                frame = state.frames[state.current_index]
                unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(frame)
                unreal.LevelSequenceEditorBlueprintLibrary.refresh_current_level_sequence()
                log(f"\n  Setting frame {frame}...")
            
            state.ticks_waited += 1
            
            # Wait 5 ticks for render to complete (increased from 3)
            if state.ticks_waited >= 5:
                state.state = "capturing"
                state.ticks_waited = 0
            return
        
        if state.state == "capturing":
            # Capture screenshot
            frame = state.frames[state.current_index]
            output_path = os.path.join(state.movie_dir, f"frame_{frame:04d}.png")
            
            unreal.AutomationLibrary.take_high_res_screenshot(1920, 1080, output_path)
            state.captured_paths.append(output_path)
            log(f"  ✓ Captured frame {frame} -> {output_path}")
            
            # Move to next frame
            state.current_index += 1
            
            if state.current_index >= len(state.frames):
                # All frames captured
                state.state = "done"
            else:
                # More frames to capture
                state.state = "waiting"
                state.ticks_waited = 0
            return
        
        if state.state == "done":
            # Cleanup and finish
            log(f"\n✓ Captured {len(state.captured_paths)}/{len(state.frames)} frames")
            
            # Unregister callback
            if state.tick_handle:
                unreal.unregister_slate_post_tick_callback(state.tick_handle)
                state.tick_handle = None
            return
            
    except Exception as e:
        log(f"  ✗ Error in frame capture: {e}")
        import traceback
        log(traceback.format_exc())
        
        # Cleanup on error
        if state.tick_handle:
            unreal.unregister_slate_post_tick_callback(state.tick_handle)
            state.tick_handle = None


def capture_verification_frames(sequence, frames, output_dir, movie_name):
    """
    Capture multiple frames for verification using tick callbacks.
    
    Args:
        sequence: LevelSequence object
        frames: List of frame numbers to capture
        output_dir: Base output directory (e.g., "dist/frames")
        movie_name: Name of movie (used for subdirectory)
    
    Returns:
        List of captured image paths
    """
    if not frames:
        return []
    
    # Create state object
    state = FrameCaptureState(sequence, frames, output_dir, movie_name)
    
    # Register tick callback
    state.tick_handle = unreal.register_slate_post_tick_callback(
        lambda delta: _capture_tick_callback(delta, state)
    )
    
    log(f"Frame capture started - will capture {len(frames)} frames asynchronously")
    
    # Note: This returns immediately - capture happens asynchronously via ticks
    # The callback will unregister itself when done
    return state.captured_paths

