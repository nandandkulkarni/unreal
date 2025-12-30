"""
Visual Validation Tests - 100m Sprint (Multi-Runner)

Validates simultaneous movement of multiple runners in different lanes.
"""

import sys
import os
import pygame
import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from visualizer.main import TrackVisualizer
from movies.sprint_100m import MOVIE

class VisualValidator100m:
    """Validate 100m sprint visual output with multiple runners"""
    
    def __init__(self, movie_data):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        # Large resolution to fit scale and margins
        self.viz = TrackVisualizer(movie_data, width=6000, height=1200, scale_factor=1.0)
        self.viz.ui.playing = False
    
    def capture_frame(self):
        """Capture the entire track area"""
        surface = pygame.Surface((6000, 1200))
        self.viz.draw_to_surface(surface, camera_offset_x=0)
        
        # Convert to OpenCV format (BGR)
        frame_array = pygame.surfarray.array3d(surface)
        frame_array = np.transpose(frame_array, (1, 0, 2))
        return cv2.cvtColor(frame_array, cv2.COLOR_RGB2BGR)
    
    def detect_runner(self, frame, color_bgr):
        """Detect runner of specific color (BGR)"""
        lower = np.array([max(0, c - 40) for c in color_bgr])
        upper = np.array([min(255, c + 40) for c in color_bgr])
        mask = cv2.inRange(frame, lower, upper)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            # Filter for reasonably sized blobs to avoid noise
            valid_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 20]
            if valid_contours:
                largest = max(valid_contours, key=cv2.contourArea)
                M = cv2.moments(largest)
                if M["m00"] > 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    return (cx, cy)
        return None

    def test_multi_runner_detection(self):
        print("Test: Multi-Runner Detection (Red & Blue)")
        frame = self.capture_frame()
        
        # Runner 1 (Red): (0, 0, 255) BGR
        pos1 = self.detect_runner(frame, (0, 0, 255))
        # Runner 2 (Blue): (255, 0, 0) BGR
        pos2 = self.detect_runner(frame, (255, 0, 0))
        
        if pos1: print(f"✅ Runner1 (Red) detected at {pos1}")
        else: print("❌ Runner1 (Red) NOT detected")
        
        if pos2: print(f"✅ Runner2 (Blue) detected at {pos2}")
        else: print("❌ Runner2 (Blue) NOT detected")
            
        assert pos1 is not None, "Runner1 (Red) detection failed"
        assert pos2 is not None, "Runner2 (Blue) detection failed"
        
        dist_y = abs(pos1[1] - pos2[1])
        print(f"Vertical separation: {dist_y}px")
        assert dist_y > 100, f"Runners overlap vertically! diff_y={dist_y}"

    def test_movement_over_time(self):
        print("Test: Movement Verification (Both Runners)")
        
        # 1. Capture Start (t=0)
        self.viz.simulation.reset()
        frame_0 = self.capture_frame()
        pos1_0 = self.detect_runner(frame_0, (0, 0, 255))
        pos2_0 = self.detect_runner(frame_0, (255, 0, 0))
        assert pos1_0 and pos2_0, "Failed to detect runners at start"
        
        # 2. Capture Mid (t=6)
        for _ in range(60): # 6s at dt=0.1
            self.viz.simulation.update(0.1)
        frame_mid = self.capture_frame()
        pos1_mid = self.detect_runner(frame_mid, (0, 0, 255))
        pos2_mid = self.detect_runner(frame_mid, (255, 0, 0))
        
        assert pos1_mid and pos2_mid, "Failed to detect runners at t=6"
        assert pos1_mid[0] > pos1_0[0], "Runner1 didn't move forward"
        assert pos2_mid[0] > pos2_0[0], "Runner2 didn't move forward"
        assert pos2_mid[0] > pos1_mid[0], f"Runner2 (faster) should be ahead! R1={pos1_mid[0]}, R2={pos2_mid[0]}"

        # Annotate and save for manual review
        for p, label, col in [(pos1_mid, "R1", (0, 0, 255)), (pos2_mid, "R2", (255, 0, 0))]:
            cv2.circle(frame_mid, p, 25, (0, 255, 0), 2)
            cv2.putText(frame_mid, label, (p[0]-10, p[1]-40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, col, 3)
        
        cv2.imwrite("docs/visual_mid_multi.png", frame_mid)
        print(f"✅ Multi-runner mid frame saved to docs/visual_mid_multi.png")
        print(f"🏃 Progress: R1_x={pos1_mid[0]}, R2_x={pos2_mid[0]}")

def run_test():
    print("="*40)
    print("Running 100m Visual Verification (Multi-Runner)")
    print("="*40)
    validator = VisualValidator100m(MOVIE)
    try:
        validator.test_multi_runner_detection()
        validator.test_movement_over_time()
        print("\n✅ ALL MULTI-RUNNER VISUAL TESTS PASSED")
    except AssertionError as e:
        print(f"\n❌ FAIL: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
    print("="*40)

if __name__ == "__main__":
    run_test()
