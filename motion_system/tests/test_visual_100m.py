"""
Visual Validation Tests - 100m Sprint (Simple)

Simplified visual test for single runner.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pygame
import numpy as np
import cv2
from visualizer.main import TrackVisualizer
from movies.sprint_100m import MOVIE

class VisualValidator100m:
    """Validate 100m sprint visual output"""
    
    def __init__(self, movie_data):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        # Use large resolution to fit 5x scaled 100m track (approx 9000px wide)
        self.viz = TrackVisualizer(movie_data, width=10000, height=1200, scale_factor=5.0)
        self.viz.ui.playing = False
    
    def capture_frame(self):
        self.viz.render()
        surface = self.viz.screen
        frame_array = pygame.surfarray.array3d(surface)
        frame_array = np.transpose(frame_array, (1, 0, 2))
        return cv2.cvtColor(frame_array, cv2.COLOR_RGB2BGR)
    
    def detect_runner(self, frame):
        """Detect single runner (Red)"""
        # Red in BGR is (0, 0, 255) because of OpenCV
        # In RGB it is (255, 0, 0)
        
        # NOTE: RunnerRenderer.COLORS[0] is (255, 0, 0) RGB
        # OpenCV uses BGR, so we look for (0, 0, 255)
        
        lower = np.array([0, 0, 150])
        upper = np.array([50, 50, 255])
        mask = cv2.inRange(frame, lower, upper)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest = max(contours, key=cv2.contourArea)
            M = cv2.moments(largest)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                return (cx, cy)
        return None

    def test_single_runner_detection(self):
        print("Test: Single Runner Detection")
        frame = self.capture_frame()
        pos = self.detect_runner(frame)
        
        if pos:
            print(f"✅ Runner detected at {pos}")
        else:
            print("❌ Runner NOT detected")
            cv2.imwrite("docs/failed_100m.png", frame)
            
        assert pos is not None, "Runner detection failed"

    def test_movement_over_time(self):
        print("Test: Movement Verification (OpenCV Tracking)")
        
        # 1. Capture Start (t=0)
        self.viz.simulation.reset()
        frame_0 = self.capture_frame()
        pos_0 = self.detect_runner(frame_0)
        assert pos_0 is not None, "Failed to detect runner at start"
        
        # Annotate and save
        cv2.circle(frame_0, pos_0, 20, (0, 255, 0), 2)
        cv2.putText(frame_0, "Start (t=0)", (pos_0[0], pos_0[1]-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imwrite("docs/visual_start.png", frame_0)
        print(f"✅ Start frame saved to docs/visual_start.png")

        # 2. Capture Mid (t=6)
        for _ in range(60): # 6 seconds at dt=0.1
            self.viz.simulation.update(0.1)
        frame_mid = self.capture_frame()
        pos_mid = self.detect_runner(frame_mid)
        assert pos_mid is not None, "Failed to detect runner at t=6"
        assert pos_mid[0] > pos_0[0], f"Runner didn't move forward! {pos_0[0]} -> {pos_mid[0]}"
        
        cv2.circle(frame_mid, pos_mid, 20, (0, 255, 0), 2)
        cv2.putText(frame_mid, "Mid (t=6)", (pos_mid[0], pos_mid[1]-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imwrite("docs/visual_mid.png", frame_mid)
        print(f"✅ Mid frame saved to docs/visual_mid.png")

        # 3. Capture Finish (t=13) - Should be past 100m
        for _ in range(70): # 7 more seconds
            self.viz.simulation.update(0.1)
        frame_finish = self.capture_frame()
        pos_finish = self.detect_runner(frame_finish)
        assert pos_finish is not None, "Failed to detect runner at t=13"
        assert pos_finish[0] > pos_mid[0], f"Runner didn't move forward! {pos_mid[0]} -> {pos_finish[0]}"
        
        cv2.circle(frame_finish, pos_finish, 20, (0, 255, 0), 2)
        cv2.putText(frame_finish, "Finish (t=13)", (pos_finish[0], pos_finish[1]-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imwrite("docs/visual_end.png", frame_finish)
        print(f"✅ Finish frame saved to docs/visual_end.png")
        
        print(f"🏃 Movement tracked: X={pos_0[0]} -> X={pos_mid[0]} -> X={pos_finish[0]}")

def run_test():
    print("="*40)
    print("Running 100m Visual Verification...")
    print("="*40)
    validator = VisualValidator100m(MOVIE)
    try:
        validator.test_single_runner_detection()
        validator.test_movement_over_time()
        print("\n✅ ALL VISUAL TESTS PASSED")
    except AssertionError as e:
        print(f"\n❌ FAIL: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
    print("="*40)

if __name__ == "__main__":
    run_test()
