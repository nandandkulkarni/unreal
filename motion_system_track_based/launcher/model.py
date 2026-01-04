
import os
import json
import re
import subprocess
import sys
import datetime
import shutil

# Constants
CONFIG_FILE = "launcher_config.jsonx"
MOVIES_DIR = "movies"
LOGS_DIR = "launcher_logs"
LOCK_FILE = "launcher.lock"
EXPLORATION_SCRIPT = "camera_settings_exploration.py"

# Tags for regex
FOCAL_LENGTH_TAG = "[EDITABLE_FOCAL_LENGTH]"
SET_HEIGHT_TAG = "[EDITABLE_SET_HEIGHT]"
ACTUAL_HEIGHT_TAG = "[EDITABLE_ACTUAL_HEIGHT]"

class LauncherModel:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.movies_dir = os.path.join(root_dir, MOVIES_DIR)
        self.config_path = os.path.join(root_dir, CONFIG_FILE)
        self.logs_dir = os.path.join(root_dir, LOGS_DIR)
        self.lock_file = os.path.join(root_dir, LOCK_FILE)
        
        # Ensure directories exist
        os.makedirs(self.logs_dir, exist_ok=True)
        os.makedirs(os.path.join(root_dir, "dist"), exist_ok=True)

    def get_movie_list(self):
        """Scans the movies/ folder for .py files"""
        if not os.path.exists(self.movies_dir):
            return []
        return [f for f in os.listdir(self.movies_dir) if f.endswith(".py") and not f.startswith("__")]

    def load_last_selection(self):
        """Loads last selected movie from jsonx file"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    return data.get("last_selected")
            except Exception as e:
                print(f"Error loading config: {e}")
        return None

    def save_selection(self, movie_name):
        """Saves current selection to jsonx file"""
        data = {"last_selected": movie_name}
        try:
            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def read_exploration_settings(self):
        """Reads settings from camera_settings_exploration.py"""
        script_path = os.path.join(self.movies_dir, EXPLORATION_SCRIPT)
        settings = {}
        
        if os.path.exists(script_path):
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Regex patterns
                patterns = {
                    "focal_length": rf"FOCAL_LENGTH\s*=\s*([\d.]+)\s*#\s*{re.escape(FOCAL_LENGTH_TAG)}",
                    "set_height": rf"SET_HEIGHT\s*=\s*([\d.]+)\s*#\s*{re.escape(SET_HEIGHT_TAG)}",
                    "actual_height": rf"ACTUAL_HEIGHT\s*=\s*([\d.]+)\s*#\s*{re.escape(ACTUAL_HEIGHT_TAG)}"
                }
                
                for key, pattern in patterns.items():
                    match = re.search(pattern, content)
                    if match:
                        settings[key] = match.group(1)
                        
            except Exception as e:
                print(f"Error reading script settings: {e}")
                
        return settings

    def update_exploration_script(self, focal_val, set_height, actual_height):
        """Updates the exploration script with new values"""
        script_path = os.path.join(self.movies_dir, EXPLORATION_SCRIPT)
        if not os.path.exists(script_path):
            return False, f"Script not found: {script_path}"

        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            updates = [
                (rf"FOCAL_LENGTH\s*=\s*([\d.]+)\s*#\s*{re.escape(FOCAL_LENGTH_TAG)}", 
                 f"FOCAL_LENGTH = {focal_val}  # {FOCAL_LENGTH_TAG}"),
                
                (rf"SET_HEIGHT\s*=\s*([\d.]+)\s*#\s*{re.escape(SET_HEIGHT_TAG)}", 
                 f"SET_HEIGHT = {set_height}  # {SET_HEIGHT_TAG}"),
                
                (rf"ACTUAL_HEIGHT\s*=\s*([\d.]+)\s*#\s*{re.escape(ACTUAL_HEIGHT_TAG)}", 
                 f"ACTUAL_HEIGHT = {actual_height}  # {ACTUAL_HEIGHT_TAG}")
            ]
            
            new_content = content
            changed = False
            for pattern, replacement in updates:
                if re.search(pattern, new_content):
                    new_content = re.sub(pattern, replacement, new_content)
                    changed = True
            
            if changed:
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True, "Script updated"
            return False, "No markers found or no changes needed"
            
        except Exception as e:
            return False, str(e)

    def update_asset_file(self, char_name, new_height):
        """Updates height in assets.py"""
        assets_path = os.path.join(self.root_dir, "motion_includes", "assets.py")
        if not os.path.exists(assets_path):
            return False, "assets.py not found"

        try:
            with open(assets_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Robust pattern for CharacterData
            # Matches: NAME = CharacterData("...", HEIGHT, ...)
            pattern = rf"(\s+{re.escape(char_name)}\s*=\s*CharacterData\s*\(\s*[^,]+,\s*)([\d.]+)"
            
            match = re.search(pattern, content)
            if match:
                current_val = float(match.group(2))
                if abs(current_val - new_height) < 0.001:
                    return False, f"Height for {char_name} is already {new_height}"
                
                new_content = re.sub(pattern, rf"\g<1>{new_height}", content, count=1)
                
                with open(assets_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True, f"Updated {char_name} height: {current_val} -> {new_height}"
            else:
                return False, f"Could not find definition for {char_name}"
        except Exception as e:
            return False, str(e)

    def acquire_lock(self):
        """Acquires lock file"""
        try:
            if os.path.exists(self.lock_file):
                try:
                    os.remove(self.lock_file)
                except OSError:
                    return None
            
            f = open(self.lock_file, 'w')
            f.write(str(os.getpid()))
            f.flush()
            return f
        except Exception:
            return None

    def release_lock(self, lock_handle):
        if lock_handle:
            lock_handle.close()
            try:
                os.remove(self.lock_file)
            except Exception:
                pass

    def prepare_log_file(self, movie_name):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.logs_dir, f"launcher_{movie_name}_{timestamp}.log")

    def cleanup_workspace(self):
        count = 0
        dist_dir = os.path.join(self.root_dir, "dist")
        
        # Cleanup dist
        if os.path.exists(dist_dir):
            try:
                for _, _, files in os.walk(dist_dir):
                    count += len(files)
                shutil.rmtree(dist_dir)
                os.makedirs(dist_dir, exist_ok=True)
            except Exception as e:
                print(f"Failed to clear dist: {e}")

        # Cleanup logs (except current?) - user asked for all logs
        if os.path.exists(self.logs_dir):
            try:
                for file in os.listdir(self.logs_dir):
                    file_path = os.path.join(self.logs_dir, file)
                    if os.path.isfile(file_path):
                        # Simple check: try delete, if locked it fails
                        try:
                            os.remove(file_path)
                            count += 1
                        except OSError:
                            pass
            except Exception as e:
                 print(f"Failed to clear logs: {e}")
        
        return count
