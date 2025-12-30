from typing import List, Dict, Any, Optional, Union, Tuple
import math
import motion_math

class VirtualState:
    def __init__(self, x=0.0, y=0.0, z=0.0, yaw=0.0, time=0.0):
        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw
        self.time = time
        
    @property
    def location(self):
        return (self.x, self.y, self.z)

    def copy(self):
        return VirtualState(self.x, self.y, self.z, self.yaw, self.time)

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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass # Nothing special to do on exit for now

    def build(self):
        return self.movie_data

    def add_command(self, command: Dict[str, Any]):
        self.movie_data["plan"].append(command)
        return self

    # --- Global Content ---
    def delete_all_skylights(self):
        return self.add_command({"command": "delete_all_skylights"})

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
    def add_actor(self, name: str, location: Tuple[float, float, float], yaw_offset: float = 0.0, mesh_path: str = None):
        # Initialize Virtual State
        self.actors[name] = VirtualState(x=location[0], y=location[1], z=location[2], yaw=yaw_offset, time=self.current_time)
        
        cmd = {
            "command": "add_actor",
            "actor": name,
            "location": list(location),
            "yaw_offset": yaw_offset
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
        # Update Global Time to match this actor's finish time
        # Note: In simultaneous blocks, this behavior is overridden/managed by the grouping context
        if self.state.time > self.mb.current_time:
            self.mb.current_time = self.state.time

    def get_state(self) -> VirtualState:
        return self.state

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

    def move_for_seconds(self, seconds: float, direction: str = "forward", speed_mtps: float = None, speed_mph: float = None, speed_mps: float = None):
        # Calculate speed
        speed_cm_s = 100.0 # Default
        if speed_mtps is not None:
             speed_cm_s = speed_mtps * 100
        elif speed_mph is not None:
             speed_cm_s = speed_mph * 44.704
        elif speed_mps is not None:
             speed_cm_s = speed_mps * 100
             
        # Update State
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
