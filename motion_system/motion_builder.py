from typing import List, Dict, Any, Optional, Union, Tuple
import math
import motion_math

class VirtualState:
    def __init__(self, x=0.0, y=0.0, z=0.0, yaw=0.0, time=0.0, current_speed=0.0, radius=0.0):
        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw
        self.time = time
        self.current_speed = current_speed
        self.radius = radius
        
    @property
    def location(self):
        return (self.x, self.y, self.z)

    def copy(self):
        return VirtualState(self.x, self.y, self.z, self.yaw, self.time, self.current_speed, self.radius)

class MovieBuilder:
    def __init__(self, name: str, create_new_level: bool = True, fps: int = 30):
        self.movie_data = {
            "name": name,
            "create_new_level": create_new_level,
            "fps": fps,
            "plan": []
        }
        self.actors: Dict[str, VirtualState] = {}
        self.current_time = 0.0
        self.waypoints = {}  # Global waypoint registry: name -> waypoint_data
        self.dependencies = {}  # Track dependencies: actor -> [depends_on_actors]
        self.auto_waypoint_counters = {}  # Auto-waypoint naming: actor -> counter
        self.debug_waypoints = False  # Global waypoint visualization flag

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass # Nothing special to do on exit for now

    def build(self):
        return self.movie_data

    def save_to_json(self, filepath: str):
        import json
        with open(filepath, "w") as f:
            json.dump(self.movie_data, f, indent=4)
        print(f"Movie plan saved to: {filepath}")
        return self

    def run(self, to_unreal: bool = False):
        """Unified Run method: Flag-based execution for Sim or Unreal"""
        if to_unreal:
            from trigger_movie import trigger_movie
            # Save temporary and trigger
            self.save_to_json("dist/unreal_last_run.json")
            trigger_movie("dist/unreal_last_run.json")
        else:
            import subprocess
            import sys
            # Launch visualizer as a subprocess
            self.save_to_json("dist/sim_last_run.json")
            subprocess.Popen([sys.executable, "run_visualizer.py", "dist/sim_last_run.json"])
        return self

    def add_command(self, command: Dict[str, Any]):
        self.movie_data["plan"].append(command)
        return self

    # --- Global Content ---
    def delete_lights(self, light_types: List[str]):
        """Delete all lights of specified types
        
        Args:
            light_types: List of light type names, e.g. ["DirectionalLight", "SkyLight", "PointLight", "SpotLight", "RectLight"]
        """
        return self.add_command({"command": "delete_lights", "light_types": light_types})
    
    def delete_all_skylights(self):
        """Convenience method to delete all skylights"""
        return self.delete_lights(["SkyLight"])

    def delete_all_floors(self):
        return self.add_command({"command": "delete_all_floors"})

    def add_floor(self, actor_name: str, location: Tuple[float, float, float] = (0, 0, -0.5), scale: float = 1000.0):
        return self.add_command({
            "command": "add_floor", "actor": actor_name, "location": list(location), "scale": scale
        })
        
    def add_directional_light(self, actor_name: str, direction_from: str = "west", angle: str = "low", intensity: str = "bright", color: str = "golden", atmosphere_sun: bool = True):
        return self.add_command({
            "command": "add_directional_light", "actor": actor_name, "from": direction_from, "angle": angle, "intensity": intensity, "color": color, "atmosphere_sun": atmosphere_sun
        })

    def add_rect_light(self, actor_name: str, location: Tuple[float, float, float], rotation: Tuple[float, float, float], width: float, height: float, intensity: str = "bright", cast_shadows: bool = False):
        return self.add_command({
            "command": "add_rect_light", "actor": actor_name, "location": list(location), "rotation": list(rotation), "width": width, "height": height, "intensity": intensity, "cast_shadows": cast_shadows
        })

    # --- Actor Management ---
    def add_actor(self, name: str, location: Tuple[float, float, float], yaw_offset: float = 0.0, radius: float = 0.35, mesh_path: str = None):
        """Add actor with a persistent radius (default 0.35m for Unreal)"""
        # Initialize Virtual State
        self.actors[name] = VirtualState(x=location[0], y=location[1], z=location[2], yaw=yaw_offset, time=self.current_time, radius=radius)
        
        cmd = {
            "command": "add_actor",
            "actor": name,
            "location": list(location),
            "yaw_offset": yaw_offset,
            "radius": radius
        }
        if mesh_path:
            cmd["mesh_path"] = mesh_path
        return self.add_command(cmd)

    def add_camera(self, name: str, location: Tuple[float, float, float], rotation: Optional[Tuple[float, float, float]] = None, fov: float = 90.0, tint: Optional[Tuple[float, float, float]] = None, show_marker: str = None, look_at_actor: str = None, offset: Optional[Tuple[float, float, float]] = None, interp_speed: float = 0.0, auto_zoom: Optional[Dict[str, Any]] = None):
        # Cameras are actors too in our state machine (mostly)
        rot = rotation if rotation else (0,0,0)
        self.actors[name] = VirtualState(x=location[0], y=location[1], z=location[2], yaw=rot[1], time=self.current_time)
        
        cmd = {
            "command": "add_camera", "actor": name, "location": list(location), "fov": fov
        }
        if rotation: cmd["rotation"] = list(rotation)
        if tint: cmd["tint"] = list(tint)
        if show_marker: cmd["show_marker"] = show_marker
        if look_at_actor: cmd["look_at_actor"] = look_at_actor
        if offset: cmd["offset"] = list(offset)
        if interp_speed > 0: cmd["interp_speed"] = interp_speed
        if auto_zoom: cmd["auto_zoom"] = auto_zoom
        return self.add_command(cmd)

    def get_actor_state(self, name: str) -> VirtualState:
        if name not in self.actors:
            raise ValueError(f"Actor '{name}' not found in MovieBuilder state")
        return self.actors[name]

    # --- Context Managers ---
    def for_actor(self, actor_name: str) -> 'ActorBuilder':
        # Sync actor to global time if behind
        state = self.get_actor_state(actor_name)
        if state.time < self.current_time:
            state.time = self.current_time
        return ActorBuilder(self, actor_name)
    
    def simultaneous(self) -> 'SimultaneousContext':
        return SimultaneousContext(self)
        
    def at_time(self, time_sec: float) -> 'TimelineBuilder':
        # Advance global time context
        self.current_time = time_sec
        return TimelineBuilder(self, time_sec)

class ActorBuilder:
    def __init__(self, movie_builder: MovieBuilder, actor_name: str):
        self.mb = movie_builder
        self.actor_name = actor_name
        self.state = self.mb.get_actor_state(actor_name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Finalize any pending fluent move
        if hasattr(self, '_active_move') and self._active_move:
            self._active_move._commit()
            self._active_move = None
            
        # Update Global Time to match this actor's finish time
        if self.state.time > self.mb.current_time:
            self.mb.current_time = self.state.time

    def radius(self, r: float):
        """Update persistent actor radius"""
        self.state.radius = r
        return self._add({"command": "set_radius", "radius": r})

    def get_state(self) -> VirtualState:
        return self.state

    def move(self) -> 'MotionCommandBuilder':
        """Start a fluent movement command chain"""
        if hasattr(self, '_active_move') and self._active_move:
            self._active_move._commit()
            
        self._active_move = MotionCommandBuilder(self)
        return self._active_move

    def _add(self, cmd: Dict[str, Any]):
        cmd["actor"] = self.actor_name
        self.mb.add_command(cmd)
        return self


    # --- Actions ---
    def animation(self, name: str):
        # Animations don't inherently advance time unless we know their duration (which we don't here)
        # So we just add the command. User must use .wait() or .move() for time.
        return self._add({"command": "animation", "name": name})

    def wait(self, seconds: float):
        self.state.time += seconds
        return self._add({"command": "wait", "seconds": seconds})
        
    def wait_until(self, time_sec: float):
        delta = time_sec - self.state.time
        if delta > 0:
            return self.wait(delta)
        return self

    def face(self, direction: str, duration: float = 1.0):
        # Update State
        target_yaw = motion_math.get_cardinal_angle(direction)
        if target_yaw is None: # Check for variable directions
             # For dynamic facing (face another actor), we can't easily predict 'yaw' without more info.
             # Ideally we resolve 'direction' if it's an actor name.
             # For now, just advance time.
             pass
        else:
             self.state.yaw = motion_math.get_shortest_path_yaw(self.state.yaw, target_yaw)
        
        self.state.time += duration
        return self._add({"command": "face", "direction": direction, "duration": duration})
    
    def face_actor(self, target_actor_name: str, duration: float = 1.0):
        # Calculate target yaw to face another actor
        target = self.mb.get_actor_state(target_actor_name)
        dx = target.x - self.state.x
        dy = target.y - self.state.y
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        
        self.state.yaw = angle_deg # Set exact yaw
        self.state.time += duration
        
        # We output a 'face' command with degrees, or direction if supported
        # The underlying system supports 'degrees' in face command
        return self._add({"command": "face", "degrees": angle_deg, "duration": duration})

    def move_for_seconds(self, seconds: float, direction: str = "forward", speed_mtps: float = None, speed_mph: float = None, speed_mps: float = None, acceleration: float = None):
        # Calculate speed
        speed_cm_s = 100.0 # Default
        if speed_mtps is not None:
             speed_cm_s = speed_mtps * 100
        elif speed_mph is not None:
             speed_cm_s = speed_mph * 44.704
        elif speed_mps is not None:
             speed_cm_s = speed_mps * 100
             
        # Update State
        # If acceleration is provided, calculate distance with acceleration
        if acceleration is not None:
            # d = v0*t + 0.5*a*t²
            # Assume starting from current speed (or 0 if not specified)
            initial_speed_cm_s = 0  # TODO: Track current speed in state
            distance_cm = initial_speed_cm_s * seconds + 0.5 * (acceleration * 100) * (seconds ** 2)
        else:
            distance_cm = seconds * speed_cm_s
        
        new_pos = motion_math.calculate_new_position(
            start_pos={"x": self.state.x, "y": self.state.y, "z": self.state.z},
            start_yaw=self.state.yaw,
            direction=direction,
            distance_cm=distance_cm
        )
        self.state.x = new_pos["x"]
        self.state.y = new_pos["y"]
        self.state.z = new_pos["z"]
        self.state.time += seconds
        
        cmd = {
            "command": "move_for_seconds",
            "seconds": seconds,
            "direction": direction,
        }
        if speed_mtps is not None: cmd["speed_mtps"] = speed_mtps
        if speed_mph is not None: cmd["speed_mph"] = speed_mph
        if speed_mps is not None: cmd["speed_mps"] = speed_mps
        if acceleration is not None: cmd["acceleration"] = acceleration
        
        return self._add(cmd)

    def move_by_distance(self, meters: float, direction: str = "forward", speed_mph: float = None, speed_mps: float = None, waypoint_name: str = None):
        # Calculate speed in cm/s
        speed_cm_s = 100.0
        if speed_mph:
            speed_cm_s = speed_mph * 44.704
        elif speed_mps:
            speed_cm_s = speed_mps * 100
            
        distance_cm = meters * 100
        duration = distance_cm / speed_cm_s
        
        # Update State
        new_pos = motion_math.calculate_new_position(
            start_pos={"x": self.state.x, "y": self.state.y, "z": self.state.z},
            start_yaw=self.state.yaw,
            direction=direction,
            distance_cm=distance_cm
        )
        self.state.x = new_pos["x"]
        self.state.y = new_pos["y"]
        self.state.z = new_pos["z"]
        self.state.time += duration
        
        cmd = {
            "command": "move_by_distance",
            "direction": direction,
            "meters": meters,
        }
        if speed_mph: cmd["speed_mph"] = speed_mph
        if speed_mps: cmd["speed_mps"] = speed_mps
        if waypoint_name: cmd["waypoint_name"] = waypoint_name
        
        return self._add(cmd)

    def move_and_turn(self, direction: str, meters: float, turn_degrees: float, speed_mph: float = None, turn_speed_deg_per_sec: float = 45):
        # Calculate move duration
        speed_cm_s = 100.0
        if speed_mph:
             speed_cm_s = speed_mph * 44.704
             
        distance_cm = meters * 100
        duration = distance_cm / speed_cm_s
        
        # Update State (Move)
        new_pos = motion_math.calculate_new_position(
            start_pos={"x": self.state.x, "y": self.state.y, "z": self.state.z},
            start_yaw=self.state.yaw,
            direction=direction,
            distance_cm=distance_cm
        )
        self.state.x = new_pos["x"]
        self.state.y = new_pos["y"]
        self.state.z = new_pos["z"]
        
        # Update State (Turn)
        self.state.yaw += turn_degrees
        self.state.time += duration 
        
        cmd = {
            "command": "move_and_turn",
            "direction": direction,
            "meters": meters,
            "turn_degrees": turn_degrees,
            "turn_speed_deg_per_sec": turn_speed_deg_per_sec
        }
        if speed_mph: cmd["speed_mph"] = speed_mph
        
        return self._add(cmd)

    def move_to_location(self, target: Tuple[float, float, float], speed_mtps: float = 1.0):
        # Calculate duration
        dx = target[0] - self.state.x
        dy = target[1] - self.state.y
        dz = target[2] - self.state.z
        distance_cm = math.sqrt(dx*dx + dy*dy + dz*dz)
        speed_cm_s = speed_mtps * 100
        duration = distance_cm / speed_cm_s
        
        self.state.x = target[0]
        self.state.y = target[1]
        self.state.z = target[2]
        self.state.time += duration
        
        return self._add({
            "command": "move_to_location",
            "target": list(target),
            "speed_mtps": speed_mtps
        })
    
    def mark_waypoint(self, name: str, visualize: bool = None):
        """Mark current position as a named waypoint
        
        Args:
            name: Waypoint name (use constants for type safety)
            visualize: Override global visualization setting
        
        Returns:
            self for method chaining
        """
        # Determine visualization setting
        should_visualize = visualize if visualize is not None else self.mb.debug_waypoints
        
        # Create waypoint object
        waypoint = {
            "name": name,
            "location": (self.state.x, self.state.y, self.state.z),
            "actor": self.actor_name,
            "time": self.state.time,
            "rotation": self.state.yaw,
            "visualize": should_visualize
        }
        
        # Store in global registry
        self.mb.waypoints[name] = waypoint
        
        # Add command to plan
        return self._add({
            "command": "mark_waypoint",
            "waypoint": waypoint
        })
    
    def auto_waypoint(self):
        """Auto-generate waypoint at current position
        
        Returns:
            self for method chaining
        """
        # Get or initialize counter for this actor
        if self.actor_name not in self.mb.auto_waypoint_counters:
            self.mb.auto_waypoint_counters[self.actor_name] = 0
        
        counter = self.mb.auto_waypoint_counters[self.actor_name]
        self.mb.auto_waypoint_counters[self.actor_name] += 1
        
        # Generate name
        auto_name = f"{self.actor_name}_auto_{counter}"
        
        # Use mark_waypoint with auto-generated name
        return self.mark_waypoint(auto_name, visualize=False)
    
    def follow_actor_path(self, actor: str, offset: Tuple[float, float, float] = (0, 0, 0), 
                         speed_multiplier: float = 1.0):
        """Follow another actor's path with offset and speed modification
        
        Args:
            actor: Name of actor to follow
            offset: Spatial offset (x, y, z) from followed actor
            speed_multiplier: Speed multiplier (1.0 = same speed, 1.2 = 20% faster)
        
        Returns:
            self for method chaining
        """
        # Track dependency
        if self.actor_name not in self.mb.dependencies:
            self.mb.dependencies[self.actor_name] = []
        self.mb.dependencies[self.actor_name].append(actor)
        
        # Add command (will be processed in multi-pass execution)
        return self._add({
            "command": "follow_actor_path",
            "follow_actor": actor,
            "offset": list(offset),
            "speed_multiplier": speed_multiplier
        })


class SimultaneousContext:
    def __init__(self, movie_builder: MovieBuilder):
        self.mb = movie_builder
        self.start_time = movie_builder.current_time
        self.max_end_time = self.start_time

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # When exiting the simultaneous block, the global time should be set to 
        # the time of the actor who finished LAST.
        self.mb.current_time = self.max_end_time

    def for_actor(self, actor_name: str) -> ActorBuilder:
        # Create a customized ActorBuilder that updates THIS context's max time instead of global time directly
        builder = ActorBuilder(self.mb, actor_name)
        
        # Reset this actor to the start of the simultaneous block (parallel execution)
        if builder.state.time < self.start_time:
            builder.state.time = self.start_time
            
        # We need a hook to capture the end time when this builder finishes
        original_exit = builder.__exit__
        
        def wrapped_exit(exc_type, exc_val, exc_tb):
            original_exit(exc_type, exc_val, exc_tb)
            # Update the max time tracker
            if builder.state.time > self.max_end_time:
                self.max_end_time = builder.state.time
                
        builder.__exit__ = wrapped_exit
        return builder

class TimelineBuilder:
    def __init__(self, movie_builder: MovieBuilder, time_sec: float):
        self.mb = movie_builder
        self.time_sec = time_sec

    def camera_cut(self, camera_name: str):
        self.mb.add_command({
            "command": "camera_cut",
            "camera": camera_name,
            "at_time": self.time_sec
        })
        return self

class MotionCommandBuilder:
    """Helper for fluent movement chaining move().xxx.move().yyy"""
    
    def __init__(self, actor_builder: 'ActorBuilder'):
        self.ab = actor_builder
        self.cmd = {
            "command": "move",
            "actor": self.ab.actor_name,
            "direction": "forward",
            "start_speed": self.ab.state.current_speed,
            "radius": self.ab.state.radius
        }
    
    def move(self) -> 'MotionCommandBuilder':
        """Commit current move and start a new one (chaining)"""
        self._commit()
        new_builder = MotionCommandBuilder(self.ab)
        self.ab._active_move = new_builder # Ensure ActorBuilder knows about the NEXT link
        return new_builder

    def for_seconds(self, s: float):
        self.cmd["seconds"] = s
        return self

    def by_distance(self, m: float):
        self.cmd["meters"] = m
        return self

    def speed(self, mtps: float):
        self.cmd["speed_mtps"] = mtps
        self.cmd["target_speed"] = mtps
        return self

    def velocity(self, to: float, start_from: float = None):
        if start_from is not None:
            self.cmd["start_speed"] = start_from
        self.cmd["target_speed"] = to
        self.cmd["velocity_ramp"] = True
        return self

    def accelerate(self, rate: float):
        self.cmd["acceleration"] = rate
        return self

    def direction(self, d: Union[str, float, Tuple[float, float]]):
        self.cmd["direction"] = d
        return self

    def in_corridor(self, left: float, right: float):
        self.cmd["left_boundary"] = left
        self.cmd["right_boundary"] = right
        return self

    def with_radius(self, r: float):
        self.cmd["radius"] = r
        return self

    def _commit(self):
        """Internal: Finalize current command and update virtual state"""
        if getattr(self, '_finalized', False):
            return
        self._finalized = True
        
        # Determine Physics Parameters
        v0 = self.cmd.get("start_speed", self.ab.state.current_speed)
        v_target = self.cmd.get("target_speed", self.cmd.get("speed_mtps", v0))
        dist = self.cmd.get("meters", 0.0)
        secs = self.cmd.get("seconds", 0.0)
        
        # Kinematic Duration Calculation
        if self.cmd.get("velocity_ramp", False):
            # v_avg = (v0 + v1) / 2
            v_avg = (v0 + v_target) / 2.0
            if v_avg <= 0: v_avg = 1.0 # Avoid div by zero
            
            if dist > 0 and secs == 0:
                secs = dist / v_avg
            elif secs > 0 and dist == 0:
                dist = secs * v_avg
        else:
            speed = self.cmd.get("speed_mtps", 1.0)
            if dist > 0 and secs == 0:
                secs = dist / speed
            elif secs > 0 and dist == 0:
                dist = secs * speed
        
        self.cmd["seconds"] = secs
        self.cmd["meters"] = dist
        self.cmd["start_speed"] = v0 # Ensure start_speed is persisted
            
        # Update Virtual State
        self.ab.state.time += secs
        self.ab.state.current_speed = v_target
        
        # Add to global plan
        self.ab.mb.add_command(self.cmd)

    def __enter__(self): return self
    def __exit__(self, *args):
        self._commit()
