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
        self.runners = {}
        
        # Parse plan for add_actor commands
        for cmd in self.movie_data.get("plan", []):
            if cmd["command"] == "add_actor":
                runner_name = cmd["actor"]
                # Location is in cm (x, y, z)
                loc_cm = cmd["location"]
                
                # Assign ID based on name (Runner1 -> 0, etc.)
                try:
                    runner_id = int(runner_name.replace("Runner", "")) - 1
                except ValueError:
                    runner_id = len(self.runners)
                
                self.runners[runner_name] = {
                    "id": runner_id,
                    "name": runner_name,
                    "position": {
                        "x": loc_cm[0] / 100.0,  # Convert cm to m
                        "y": loc_cm[1] / 100.0
                    },
                    "speed": 0.0,
                    "acceleration": 3.0,  # Default
                    "max_speed": 9.5 + runner_id * 0.1,  # Default variation
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
        """Update single runner position based on active commands"""
        active_cmd = None
        cmd_start_time = 0.0
        
        # Find active command for this runner at current time
        # This is inefficient (O(N) per frame), but fine for small movies
        current_t = 0.0
        for cmd in self.movie_data.get("plan", []):
            duration = cmd.get("seconds", 0) or cmd.get("duration", 0)
            
            # Check if this command applies to this runner
            # Note: MovieBuilder flattens plan, so we need to track time per actor?
            # Actually, MovieBuilder plan is global sequential or parallel.
            # Simplified: Assume commands are sequential for each actor for now.
            # Real solution needs to track start_time for each command.
            
            # HACK: For sprint_100m, we know there's one move command
            if cmd.get("command") == "move_for_seconds":
                # Check if it's simultaneous group or single actor
                # The movie structure is complex: flat list of commands.
                # For 100m sprint, it's inside a 'for_actor' block which adds commands.
                
                # Let's assume the first move command belongs to this runner for 0-10s
                # TODO: Implement proper command scheduling
                if self.current_time < duration:
                    active_cmd = cmd
                    break
        
        if active_cmd:
            # Get physics parameters
            accel = active_cmd.get("acceleration", 0.0)
            target_speed = active_cmd.get("speed_mtps", 0.0)
            
            v0 = runner["speed"]
            
            # Calculate displacement using kinematic formulas
            if accel > 0:
                # Time remaining to reach target speed
                time_to_max = (target_speed - v0) / accel if target_speed > v0 else 0
                
                # Split dt into acceleration time and cruise time
                dt_accel = min(dt, max(0, time_to_max))
                dt_cruise = max(0, dt - dt_accel)
                
                # Displacement: d = v0*t + 0.5*a*t^2
                d_accel = v0 * dt_accel + 0.5 * accel * (dt_accel ** 2)
                v_new = v0 + accel * dt_accel
                
                # Constant speed displacement: d = v*t
                d_cruise = v_new * dt_cruise
                
                runner["speed"] = v_new
                displacement = d_accel + d_cruise
            else:
                runner["speed"] = target_speed
                displacement = target_speed * dt
                
            # Update position (simplified linear movement)
            runner["position"]["x"] += displacement
    
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
