
import unittest
from unittest.mock import MagicMock, patch
import os
import sys
import tkinter as tk

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from launcher.view_model import LauncherViewModel
# We need CharacterData/Characters for the logic check
from motion_includes.assets import Characters, CharacterData

class TestLauncherViewModel(unittest.TestCase):
    def setUp(self):
        # Mock Tkinter variables since we don't have a root window
        # We can't easily mock tk.StringVar without a root, 
        # so we'll patch Tkinter or just use a dummy root if needed.
        # Actually simplest is to mock the vars or instantiate a hidden root.
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.mock_model = MagicMock()
        self.mock_model.get_movie_list.return_value = ["movie1.py"]
        self.mock_model.load_last_selection.return_value = None
        
        self.mock_view = MagicMock()
        
        self.vm = LauncherViewModel(self.mock_model, self.mock_view)

    def tearDown(self):
        self.root.destroy()

    def test_update_enabled_for_known_character(self):
        # Setup
        self.vm.char_name_var.set("BELICA")
        
        # Action
        # Simulate result string from measure tool
        result = "Height: 180.00 cm (Source: ActorBounds)"
        self.vm.process_measure_result(result)
        
        # Verify
        self.mock_view.enable_update_asset.assert_called_with(True)
        self.mock_view.log.assert_any_call(">>> ENABLED UPDATE for BELICA")
        # Verify height parse
        self.assertEqual(self.vm.actual_height_val.get(), "1.80")

    def test_update_disabled_for_unknown_character(self):
        # Setup
        self.vm.char_name_var.set("UNKNOWN_CHAR_XYZ")
        
        # Action
        result = "Height: 150.00 cm (Source: ActorBounds)"
        self.vm.process_measure_result(result)
        
        # Verify
        self.mock_view.enable_update_asset.assert_called_with(False)
        self.mock_view.log.assert_any_call(">>> CANNOT UPDATE: UNKNOWN_CHAR_XYZ unknown")

if __name__ == '__main__':
    unittest.main()
