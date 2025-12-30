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
        """Pre-calculate the entire motion plan using the shared MotionPlanner"""
        from motion_planner import plan_motion
        
        self.runners = {}
        # We need a dummy actors_info for characters
        actors_info = {}
        for cmd in self.movie_data.get("plan", []):
            if cmd["command"] == "add_actor":
                name = cmd["actor"]
                loc = cmd["location"]
                import unreal_mock as unreal
                # Use absolute translation for the planner
                actors_info[name] = {
                    "location": unreal.Vector(loc[0], loc[1], loc[2]),
                    "rotation": unreal.Rotator(0, 0, 0)
                }
        
        # Plan the motion (Pass 1)
        self.fps = self.movie_data.get("fps", 60)
        self.calculated_keyframes, _ = plan_motion(self.movie_data["plan"], actors_info, self.fps)
        
        # Setup runners for playback
        for i, (name, info) in enumerate(actors_info.items()):
            self.runners[name] = {
                "id": i,
                "name": name,
                "position": {"x": info["location"].x / 100.0, "y": info["location"].y / 100.0},
                "speed": 0.0
            }
    
    def update(self, dt):
        """Playback-based update"""
        self.current_time += dt
        current_frame = int(self.current_time * self.fps)
        
        from motion_planner import get_actor_location_at_frame
        
        for name, runner in self.runners.items():
            if name in self.calculated_keyframes:
                pos = get_actor_location_at_frame(self.calculated_keyframes[name], current_frame)
                runner["position"]["x"] = pos["x"] / 100.0
                runner["position"]["y"] = pos["y"] / 100.0
                # Speed tracking (optional for renderer)
                runner["speed"] = 10.0 # Placeholder for now
            
    def get_runner_state(self, runner_name):
        """Get current state of a runner
        
        Returns:
            Dict with position, speed, etc.
        """
        return self.runners.get(runner_name, None)
    
    def get_all_runners(self):
        """Get all runner states"""
        return self.runners
    
    def check_proximity(self, runner_name, target_x=95.0, range_m=5.0):
        """Check if runner is within range of target position"""
        runner = self.get_runner_state(runner_name)
        if not runner:
            return False
            
        dist = abs(runner["position"]["x"] - target_x)
        return dist <= range_m
    
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
