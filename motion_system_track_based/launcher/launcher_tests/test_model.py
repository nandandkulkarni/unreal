
import unittest
import os
import sys
import shutil
from unittest.mock import MagicMock, patch

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from launcher.model import LauncherModel

class TestLauncherModel(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join(os.getcwd(), "test_env")
        os.makedirs(self.test_dir, exist_ok=True)
        self.model = LauncherModel(self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_save_load_selection(self):
        self.model.save_selection("test_movie.py")
        loaded = self.model.load_last_selection()
        self.assertEqual(loaded, "test_movie.py")

    def test_update_exploration_script(self):
        # Create dummy script
        script_dir = os.path.join(self.test_dir, "movies")
        os.makedirs(script_dir, exist_ok=True)
        script_path = os.path.join(script_dir, "camera_settings_exploration.py")
        
        with open(script_path, 'w') as f:
            f.write("FOCAL_LENGTH = 50.0 # [EDITABLE_FOCAL_LENGTH]\n")
            f.write("SET_HEIGHT = 1.0 # [EDITABLE_SET_HEIGHT]\n")
            f.write("ACTUAL_HEIGHT = 1.0 # [EDITABLE_ACTUAL_HEIGHT]\n")

        # Update
        success, msg = self.model.update_exploration_script(85.0, 1.8, 1.75)
        self.assertTrue(success, msg)
        
        # Verify
        with open(script_path, 'r') as f:
            content = f.read()
            self.assertIn("FOCAL_LENGTH = 85.0", content)
            self.assertIn("SET_HEIGHT = 1.8", content)
            self.assertIn("ACTUAL_HEIGHT = 1.75", content)

    def test_update_asset_file(self):
        # Create dummy assets.py
        assets_dir = os.path.join(self.test_dir, "motion_includes")
        os.makedirs(assets_dir, exist_ok=True)
        assets_path = os.path.join(assets_dir, "assets.py")
        
        with open(assets_path, 'w') as f:
            f.write('class Characters:\n')
            f.write('    BELICA = CharacterData("/Path/To/Mesh", 1.8)\n')

        # Update
        success, msg = self.model.update_asset_file("BELICA", 1.95)
        self.assertTrue(success, msg)
        
        # Verify
        with open(assets_path, 'r') as f:
            content = f.read()
            self.assertIn('BELICA = CharacterData("/Path/To/Mesh", 1.95)', content)

    def test_update_asset_unknown(self):
        success, msg = self.model.update_asset_file("UNKNOWN", 1.0)
        self.assertFalse(success)
        self.assertIn("not found", msg)

if __name__ == '__main__':
    unittest.main()
