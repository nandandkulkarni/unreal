"""
Automated State Test for 100m Sprint

Validates physics logic for single runner 100m sprint.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from visualizer.simulation_engine import SimulationEngine
from movies.sprint_100m import MOVIE

class TestSprint100mPhysics:
    """Test physics calculations for 100m sprint"""
    
    def setup_method(self):
        """Setup test data from 100m movie"""
        self.movie_data = MOVIE
        self.sim = SimulationEngine(self.movie_data)
        self.runner_name = "Runner1"
    
    def test_runner_initialization(self):
        """Verify runner starts at correct location"""
        runner = self.sim.get_runner_state(self.runner_name)
        assert runner is not None, "Runner1 should exist"
        
        # Should start at 0,0
        assert runner["position"]["x"] == 0.0
        assert runner["position"]["y"] == 0.0
        assert runner["speed"] == 0.0
    
    def test_acceleration_phase(self):
        """Verify acceleration over first 5 seconds"""
        # Target: 0 to 10 m/s over 5s (accel=2.0)
        
        # t=1s: v=2.0
        self.sim.update(1.0)
        runner = self.sim.get_runner_state(self.runner_name)
        assert 1.9 < runner["speed"] < 2.1
        
        # t=3s: v=6.0
        self.sim.update(2.0)
        runner = self.sim.get_runner_state(self.runner_name)
        assert 5.9 < runner["speed"] < 6.1
        
        # t=5s: v=10.0 (max)
        self.sim.update(2.0)
        runner = self.sim.get_runner_state(self.runner_name)
        assert 9.9 < runner["speed"] < 10.1
        
    def test_cruise_phase(self):
        """Verify constant speed after acceleration"""
        # Advance 6 seconds (past accel phase)
        self.sim.update(6.0)
        
        runner = self.sim.get_runner_state(self.runner_name)
        speed_t6 = runner["speed"]
        
        # Advance another 2 seconds
        self.sim.update(2.0)
        runner = self.sim.get_runner_state(self.runner_name)
        speed_t8 = runner["speed"]
        
        assert speed_t6 == 10.0
        assert speed_t8 == 10.0
        
    def test_total_distance(self):
        """Verify approx distance covered in 10s"""
        # Accel phase (0-5s): d = 0.5 * 2 * 5^2 = 25m
        # Cruise phase (5-10s): d = 10 * 5 = 50m
        # Run for 10 seconds total
        # Use smaller dt for accuracy
        for _ in range(100):
            self.sim.update(0.1)
            
        runner = self.sim.get_runner_state(self.runner_name)
        dist = runner["position"]["x"]
        
        # Discrete integration error tolerance
        # Expected ~75m, allow +/- 2m error
        assert 73.0 < dist < 77.0, f"Expected ~75m, got {dist:.2f}m"

if __name__ == "__main__":
    # Manual run if executed directly
    test = TestSprint100mPhysics()
    test.setup_method()
    test.test_runner_initialization()
    print("Init Passed")
    test.setup_method() 
    test.test_acceleration_phase()
    print("Accel Passed")
    test.setup_method()
    test.test_cruise_phase()
    print("Cruise Passed")
    test.setup_method()
    test.test_total_distance()
    print("Distance Passed")
