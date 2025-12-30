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
                active_cmd = cmd
                break
        
        if active_cmd:
            cmd_type = active_cmd.get("command")
            
            # 1. Calculate Velocity (Speed + Ramping)
            v0 = active_cmd.get("start_speed", runner["speed"])
            v_target = active_cmd.get("target_speed", active_cmd.get("speed_mtps", v0))
            
            if active_cmd.get("velocity_ramp", False):
                # RAMP: Speed scales linearly over the command duration
                start_t = active_cmd.get("start_time", 0)
                dur = active_cmd.get("seconds", 1.0)
                progress = (self.current_time - start_t) / dur
                progress = max(0, min(1, progress))
                runner["speed"] = v0 + (v_target - v0) * progress
            elif active_cmd.get("acceleration", 0) > 0:
                # ACCEL: Physical acceleration
                accel = active_cmd["acceleration"]
                if runner["speed"] < v_target:
                    runner["speed"] = min(v_target, runner["speed"] + accel * dt)
                else:
                    runner["speed"] = v_target
            else:
                runner["speed"] = v_target

            # 2. Movement Logic
            displacement = runner["speed"] * dt
            
            if cmd_type == "move":
                # Get Direction Vector
                direction_val = active_cmd.get("direction", "forward")
                if direction_val == "forward":
                    vec_f = (1, 0) # X+
                elif isinstance(direction_val, (int, float)):
                    rad = math.radians(direction_val)
                    vec_f = (math.cos(rad), math.sin(rad))
                else: # Tuple/List
                    vec_f = direction_val
                
                # Apply Forward Movement
                runner["position"]["x"] += vec_f[0] * displacement
                runner["position"]["y"] += vec_f[1] * displacement
                
                # CORRIDOR CLAMPING (Equidistant)
                left = active_cmd.get("left_boundary")
                right = active_cmd.get("right_boundary")
                radius = active_cmd.get("radius", 0.0)
                
                if left is not None and right is not None:
                    # For straight tracks (X-aligned), we center Y between left/right
                    # TODO: Support arbitrary direction vectors for pure perpendicular clamping
                    target_y = (left + right) / 2.0
                    runner["position"]["y"] = target_y
            
            elif cmd_type == "move_for_seconds":
                # Legacy support
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
