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
        """Extract runner data and group commands by actor"""
        self.runners = {}
        self.actor_plans = {}  # Categorized plans per actor
        
        # 1. Initialize runner states from add_actor commands
        for cmd in self.movie_data.get("plan", []):
            if cmd["command"] == "add_actor":
                runner_name = cmd["actor"]
                loc_cm = cmd["location"]
                
                try:
                    runner_id = int(runner_name.replace("Runner", "")) - 1
                except ValueError:
                    runner_id = len(self.runners)
                
                self.runners[runner_name] = {
                    "id": runner_id,
                    "name": runner_name,
                    "position": {
                        "x": loc_cm[0] / 100.0,
                        "y": loc_cm[1] / 100.0
                    },
                    "speed": 0.0
                }
                self.actor_plans[runner_name] = []

        # 2. Assign commands to respective actor plans
        # Note: Simultaneous commands are interleaved in the flat plan list.
        # For simplicity, we assume they all start at the relative time they appear.
        for cmd in self.movie_data.get("plan", []):
            actor = cmd.get("actor")
            if actor in self.actor_plans:
                # Calculate start_time for this specific actor's timeline
                prev_durations = sum(c.get("seconds", 0) for c in self.actor_plans[actor])
                cmd_copy = cmd.copy()
                cmd_copy["start_time"] = prev_durations
                self.actor_plans[actor].append(cmd_copy)
    
    def update(self, dt):
        """Update simulation by dt seconds"""
        self.current_time += dt
        for runner_name, runner in self.runners.items():
            self._update_runner(runner, dt)
    
    def _update_runner(self, runner, dt):
        """Update single runner position based on its specific active command"""
        active_cmd = None
        runner_name = runner["name"]
        
        # Find command for this runner active at self.current_time
        for cmd in self.actor_plans.get(runner_name, []):
            start = cmd.get("start_time", 0)
            duration = cmd.get("seconds", 0)
            if start <= self.current_time < (start + duration):
                if cmd["command"] == "move_for_seconds":
                    active_cmd = cmd
                    break
        
        if active_cmd:
            accel = active_cmd.get("acceleration", 0.0)
            target_speed = active_cmd.get("speed_mtps", 0.0)
            v0 = runner["speed"]
            
            if accel > 0:
                time_to_max = (target_speed - v0) / accel if target_speed > v0 else 0
                dt_accel = min(dt, max(0, time_to_max))
                dt_cruise = max(0, dt - dt_accel)
                
                d_accel = v0 * dt_accel + 0.5 * accel * (dt_accel ** 2)
                v_new = v0 + accel * dt_accel
                d_cruise = v_new * dt_cruise
                
                runner["speed"] = v_new
                displacement = d_accel + d_cruise
            else:
                runner["speed"] = target_speed
                displacement = target_speed * dt
                
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
