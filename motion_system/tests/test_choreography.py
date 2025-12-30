"""
Automated Test Suite for Motion Choreography

Tests distance, speed, acceleration, and collision detection
using direct simulation state access.
"""

import pytest
import math
from visualizer.simulation_engine import SimulationEngine

class TestMotionPhysics:
    """Test physics calculations"""
    
    def setup_method(self):
        """Setup test data"""
        self.movie_data = {
            "name": "400m Dash",
            "fps": 30,
            "plan": []
        }
        self.sim = SimulationEngine(self.movie_data)
    
    def test_acceleration(self):
        """Test that runners accelerate correctly"""
        runner = self.sim.get_runner_state("Runner1")
        
        # Initial speed should be 0
        assert runner["speed"] == 0.0, "Should start at rest"
        
        # After 1 second: v = a*t = 3.0 * 1.0 = 3.0 m/s
        self.sim.update(1.0)
        runner = self.sim.get_runner_state("Runner1")
        assert 2.9 < runner["speed"] < 3.1, f"Expected ~3 m/s, got {runner['speed']}"
        
        # After 3 seconds: v = 3.0 * 3.0 = 9.0 m/s (near max)
        self.sim.update(2.0)
        runner = self.sim.get_runner_state("Runner1")
        assert 8.5 < runner["speed"] < 9.6, f"Expected ~9 m/s, got {runner['speed']}"
        
        # After 5 seconds: should hit max speed (9.5 m/s)
        self.sim.update(2.0)
        runner = self.sim.get_runner_state("Runner1")
        assert runner["speed"] == runner["max_speed"], "Should reach max speed"
    
    def test_distance_covered(self):
        """Test distance = ∫ v dt"""
        runner = self.sim.get_runner_state("Runner1")
        initial_x = runner["position"]["x"]
        
        # Run for 10 seconds
        for _ in range(10):
            self.sim.update(1.0)
        
        runner = self.sim.get_runner_state("Runner1")
        final_x = runner["position"]["x"]
        distance = final_x - initial_x
        
        # Expected: ~0.5*a*t² + v_max*(t-t_accel)
        # Acceleration phase: 0-3s, distance = 0.5*3*9 = 13.5m
        # Cruise phase: 3-10s, distance = 9.5*7 = 66.5m
        # Total: ~80m
        assert 75 < distance < 85, f"Expected ~80m, got {distance}m"
    
    def test_speed_profile(self):
        """Test complete speed profile over time"""
        speeds = []
        times = []
        
        for t in range(20):
            self.sim.update(1.0)
            runner = self.sim.get_runner_state("Runner1")
            speeds.append(runner["speed"])
            times.append(t + 1)
        
        # Verify acceleration phase (0-3s)
        assert speeds[0] < speeds[1] < speeds[2], "Should be accelerating"
        
        # Verify cruise phase (3-20s)
        for i in range(3, 20):
            assert abs(speeds[i] - speeds[3]) < 0.1, "Should maintain constant speed"
    
    def test_no_collisions(self):
        """Test that runners don't collide"""
        MIN_SAFE_DISTANCE = 0.5  # 0.5 meters
        
        # Run simulation for 60 seconds
        for t in range(60):
            self.sim.update(1.0)
            
            # Get all runner positions
            runners = self.sim.get_all_runners()
            positions = [
                (r["position"]["x"], r["position"]["y"]) 
                for r in runners.values()
            ]
            
            # Check all pairs
            for i, pos1 in enumerate(positions):
                for j, pos2 in enumerate(positions[i+1:], start=i+1):
                    dist = math.sqrt(
                        (pos1[0] - pos2[0])**2 + 
                        (pos1[1] - pos2[1])**2
                    )
                    assert dist > MIN_SAFE_DISTANCE, \
                        f"Collision at t={t}s: Runner{i} and Runner{j+1} are {dist:.2f}m apart"
    
    def test_lane_adherence(self):
        """Test that runners stay in their lanes for first 100m only"""
        LANE_WIDTH = 1.22  # meters
        TOLERANCE = 0.1    # 10cm tolerance
        LANE_BREAK_DISTANCE = 100.0  # Can break to inside after 100m
        
        for t in range(60):
            self.sim.update(1.0)
            
            for runner_name, runner in self.sim.get_all_runners().items():
                runner_id = runner["id"]
                distance_covered = runner["position"]["x"]
                
                # Only enforce lane adherence for first 100m
                if distance_covered < LANE_BREAK_DISTANCE:
                    expected_y = runner_id * LANE_WIDTH
                    actual_y = runner["position"]["y"]
                    
                    deviation = abs(actual_y - expected_y)
                    assert deviation < TOLERANCE, \
                        f"{runner_name} out of lane at {distance_covered:.1f}m: {deviation:.2f}m deviation"
                else:
                    # After 100m, runners can move to inside lane (lane 1)
                    # Just verify they're within track bounds
                    actual_y = runner["position"]["y"]
                    max_y = 6 * LANE_WIDTH  # 6 lanes
                    assert 0 <= actual_y <= max_y, \
                        f"{runner_name} outside track bounds at {distance_covered:.1f}m"
    
    def test_finish_times(self):
        """Test realistic finish times for 400m"""
        FINISH_LINE_X = 400.0  # 400 meters
        finish_times = {}
        
        # Run until all finish
        for t in range(100):
            self.sim.update(1.0)
            
            for runner_name, runner in self.sim.get_all_runners().items():
                if runner_name not in finish_times:
                    if runner["position"]["x"] >= FINISH_LINE_X:
                        finish_times[runner_name] = t
        
        # Verify all finished
        assert len(finish_times) == 6, "All runners should finish"
        
        # Verify realistic times (elite sprinters: 45-50s)
        for runner_name, time in finish_times.items():
            assert 40 < time < 55, \
                f"{runner_name} finished in {time}s (unrealistic)"
    
    def test_speed_variation(self):
        """Test that runners have different speeds"""
        # Run to max speed
        for _ in range(5):
            self.sim.update(1.0)
        
        speeds = [
            runner["speed"] 
            for runner in self.sim.get_all_runners().values()
        ]
        
        # Should have variation
        assert len(set(speeds)) > 1, "Runners should have different speeds"
        
        # Should be in reasonable range
        assert all(9.0 < s < 10.5 for s in speeds), "Speeds should be realistic"


class TestChoreographyValidation:
    """Test high-level choreography requirements"""
    
    def test_staggered_starts(self):
        """Test that outer lanes start ahead"""
        sim = SimulationEngine({"name": "Test", "fps": 30, "plan": []})
        
        # Initial positions
        positions = [
            runner["position"]["x"] 
            for runner in sim.get_all_runners().values()
        ]
        
        # All should start at x=0 (will implement stagger later)
        # TODO: Update when staggered starts are implemented
        assert all(x == 0.0 for x in positions), "Placeholder: all start at 0"
    
    def test_race_fairness(self):
        """Test that all runners cover same distance"""
        sim = SimulationEngine({"name": "Test", "fps": 30, "plan": []})
        
        # Run for 50 seconds
        for _ in range(50):
            sim.update(1.0)
        
        distances = [
            runner["position"]["x"] 
            for runner in sim.get_all_runners().values()
        ]
        
        # All should cover similar distance (within 10%)
        avg_distance = sum(distances) / len(distances)
        for dist in distances:
            deviation = abs(dist - avg_distance) / avg_distance
            assert deviation < 0.1, f"Distance deviation too large: {deviation*100:.1f}%"


def run_all_tests():
    """Run all tests and generate report"""
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_all_tests()
