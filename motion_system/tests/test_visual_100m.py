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
        # Use simpler resolution
        self.viz = TrackVisualizer(movie_data, width=800, height=600, scale_factor=1.0)
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
            cv2.imwrite("failed_100m.png", frame)
            
        assert pos is not None, "Runner detection failed"

def run_test():
    print("Running 100m Visual Test...")
    validator = VisualValidator100m(MOVIE)
    try:
        validator.test_single_runner_detection()
        print("PASS")
    except AssertionError as e:
        print(f"FAIL: {e}")

if __name__ == "__main__":
    run_test()
