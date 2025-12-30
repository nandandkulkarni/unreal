"""
Simulation Engine for 2D Track Visualizer

Calculates runner positions based on speed profiles and waypoints.
"""

import math

class SimulationEngine:
    """Physics simulation for runner movement"""
    
    def __init__(self, movie_data):
        """Initialize simulation from MovieBuilder data
        
        Args:
            movie_data: Dictionary from MovieBuilder.build()
        """
        self.movie_data = movie_data
        self.fps = movie_data.get("fps", 30)
        self.runners = {}
        self.current_time = 0.0
        
        # Parse movie data and initialize runners
        self._initialize_runners()
    
    def _initialize_runners(self):
        """Extract runner data from movie plan"""
        # For now, create simple runner state
        # TODO: Parse actual movie_data plan
        
        # Example: 6 runners
        for i in range(6):
            runner_name = f"Runner{i+1}"
            self.runners[runner_name] = {
                "id": i,
                "name": runner_name,
                "position": {"x": 0.0, "y": i * 1.22},  # Lane spacing
                "speed": 0.0,
                "acceleration": 3.0,  # m/s²
                "max_speed": 9.5 + i * 0.1,  # Slight variation
                "waypoints": [],
                "current_waypoint_index": 0
            }
    
    def update(self, dt):
        """Update simulation by dt seconds
        
        Args:
            dt: Time delta in seconds
        """
        self.current_time += dt
        
        for runner_name, runner in self.runners.items():
            self._update_runner(runner, dt)
    
    def _update_runner(self, runner, dt):
        """Update single runner position"""
        # Simple physics: accelerate to max speed
        if runner["speed"] < runner["max_speed"]:
            runner["speed"] += runner["acceleration"] * dt
            runner["speed"] = min(runner["speed"], runner["max_speed"])
        
        # Move forward (simplified - just move in +x direction)
        runner["position"]["x"] += runner["speed"] * dt
    
    def get_runner_state(self, runner_name):
        """Get current state of a runner
        
        Returns:
            Dict with position, speed, etc.
        """
        return self.runners.get(runner_name, None)
    
    def get_all_runners(self):
        """Get all runner states"""
        return self.runners
    
    def reset(self):
        """Reset simulation to t=0"""
        self.current_time = 0.0
        self._initialize_runners()
    
    def set_time(self, time):
        """Jump to specific time (for scrubbing)"""
        self.reset()
        # Fast-forward to target time
        while self.current_time < time:
            self.update(0.016)  # ~60 FPS steps
