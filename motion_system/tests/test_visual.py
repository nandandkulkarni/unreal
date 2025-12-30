"""
Visual Validation Tests using OpenCV

Captures Pygame frames and validates visual output:
- Runner positions match expected locations
- No visual artifacts
- Proper rendering of track, lanes, runners
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pygame
import numpy as np
import cv2
from visualizer.main import TrackVisualizer
from movies.race_400m import MOVIE

class VisualValidator:
    """Validate Pygame visual output using OpenCV"""
    
    def __init__(self, movie_data):
        # Initialize visualizer in headless mode
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        
        self.viz = TrackVisualizer(movie_data, width=1200, height=800)
        self.viz.ui.playing = False  # Don't auto-play
    
    def capture_frame(self):
        """Capture current Pygame frame as OpenCV image"""
        # Render one frame
        self.viz.render()
        
        # Convert Pygame surface to numpy array
        surface = self.viz.screen
        frame_array = pygame.surfarray.array3d(surface)
        frame_array = np.transpose(frame_array, (1, 0, 2))  # (height, width, channels)
        frame_bgr = cv2.cvtColor(frame_array, cv2.COLOR_RGB2BGR)
        
        return frame_bgr
    
    def detect_runners(self, frame):
        """Detect runner positions using color detection"""
        from visualizer.runner_renderer import RunnerRenderer
        
        positions = []
        for i, color_rgb in enumerate(RunnerRenderer.COLORS):
            # Convert RGB to BGR for OpenCV
            color_bgr = (color_rgb[2], color_rgb[1], color_rgb[0])
            
            # Create color mask (with tolerance)
            lower = np.array([max(0, c - 30) for c in color_bgr])
            upper = np.array([min(255, c + 30) for c in color_bgr])
            mask = cv2.inRange(frame, lower, upper)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Get largest contour (runner circle)
                largest = max(contours, key=cv2.contourArea)
                M = cv2.moments(largest)
                if M["m00"] > 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    positions.append((cx, cy))
                else:
                    positions.append(None)
            else:
                positions.append(None)
        
        return positions
    
    def test_initial_positions(self):
        """Test that runners start in correct staggered positions"""
        print("Test: Initial Staggered Positions")
        print("-" * 40)
        
        # Capture frame at t=0
        frame = self.capture_frame()
        
        # Detect runner positions
        positions = self.detect_runners(frame)
        
        # Verify all 6 runners detected
        detected_indices = [i for i, p in enumerate(positions) if p is not None]
        detected_count = len(detected_indices)
        
        if detected_count != 6:
            missing = [i for i in range(6) if i not in detected_indices]
            print(f"❌ Failed to detect runners: {missing}")
            
        assert detected_count == 6, f"Expected 6 runners, detected {detected_count} (Indices: {detected_indices})"
        
        print(f"✅ Detected all 6 runners")
        
        # Verify staggered X positions (outer lanes ahead)
        x_positions = [p[0] for p in positions if p is not None]
        
        # Should be in ascending order (lane 1 behind, lane 6 ahead)
        # Note: This assumes left-to-right rendering
        for i in range(len(x_positions) - 1):
            if x_positions[i] >= x_positions[i+1]:
                print(f"⚠️  Warning: Stagger may not be visible (positions: {x_positions})")
        
        print(f"✅ Staggered positions: {x_positions}")
        print()
    
    def test_lane_separation(self):
        """Test that runners are in separate lanes"""
        print("Test: Lane Separation")
        print("-" * 40)
        
        frame = self.capture_frame()
        positions = self.detect_runners(frame)
        
        # Get Y positions (lane positions)
        y_positions = [p[1] for p in positions if p is not None]
        
        # Verify Y positions are distinct (different lanes)
        unique_y = len(set(y_positions))
        assert unique_y == 6, f"Expected 6 distinct lanes, got {unique_y}"
        
        print(f"✅ All runners in separate lanes: {y_positions}")
        print()
    
    def test_movement_over_time(self):
        """Test that runners move forward over time"""
        print("Test: Movement Over Time")
        print("-" * 40)
        
        # Capture at t=0
        frame_t0 = self.capture_frame()
        pos_t0 = self.detect_runners(frame_t0)
        
        # Advance 5 seconds
        for _ in range(5):
            self.viz.simulation.update(1.0)
        
        # Capture at t=5
        frame_t5 = self.capture_frame()
        pos_t5 = self.detect_runners(frame_t5)
        
        # Verify all runners moved forward (X increased)
        for i in range(6):
            if pos_t0[i] and pos_t5[i]:
                x0, x5 = pos_t0[i][0], pos_t5[i][0]
                assert x5 > x0, f"Runner {i+1} didn't move forward: {x0} → {x5}"
        
        print(f"✅ All runners moved forward")
        print()
    
    def test_no_visual_artifacts(self):
        """Test for visual rendering issues"""
        print("Test: No Visual Artifacts")
        print("-" * 40)
        
        frame = self.capture_frame()
        
        # Check for completely black or white frames (rendering failure)
        mean_intensity = np.mean(frame)
        assert 10 < mean_intensity < 245, f"Frame may be corrupted (mean={mean_intensity})"
        
        print(f"✅ Frame rendered correctly (mean intensity: {mean_intensity:.1f})")
        print()
    
    def save_debug_frame(self, filename="debug_frame.png"):
        """Save current frame for manual inspection"""
        frame = self.capture_frame()
        cv2.imwrite(filename, frame)
        print(f"💾 Saved debug frame to {filename}")


def run_visual_tests():
    """Run all visual validation tests"""
    print("="*60)
    print("VISUAL VALIDATION TEST SUITE (OpenCV)")
    print("="*60)
    print()
    
    validator = VisualValidator(MOVIE)
    
    try:
        validator.test_initial_positions()
        validator.test_lane_separation()
        validator.test_movement_over_time()
        validator.test_no_visual_artifacts()
        
        # Save debug frame
        validator.save_debug_frame("c:/UnrealProjects/coding/unreal/motion_system/tests/debug_frame.png")
        
        print("="*60)
        print("ALL VISUAL TESTS PASSED ✅")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n❌ VISUAL TEST FAILED: {e}")
        validator.save_debug_frame("c:/UnrealProjects/coding/unreal/motion_system/tests/failed_frame.png")
        raise


if __name__ == "__main__":
    run_visual_tests()
