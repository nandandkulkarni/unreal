"""
Integrated Motion Test Runner
Runs test → Verifies results → Reports pass/fail → Generates troubleshooting logs
"""

import unreal
import sys
import os
import importlib
from datetime import datetime

# Add motion_system directory to path
# Force absolute paths since __file__ may point to wrong location during remote execution
parent_dir = r"C:\UnrealProjects\Coding\unreal"
script_dir = r"C:\UnrealProjects\Coding\unreal\tests"

motion_system_dir = os.path.join(parent_dir, "motion_system")
if motion_system_dir not in sys.path:
    sys.path.insert(0, motion_system_dir)

# Also add tests directory for test_motion_system module
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Import modules directly (not as package)
import logger
import cleanup
import sequence_setup
import mannequin_setup
import motion_planner
import keyframe_applier
import debug_db
import test_motion_system
import axis_markers

# Reload for development
importlib.reload(logger)
importlib.reload(cleanup)
importlib.reload(sequence_setup)
importlib.reload(mannequin_setup)
importlib.reload(motion_planner)
importlib.reload(keyframe_applier)
importlib.reload(debug_db)
importlib.reload(test_motion_system)
importlib.reload(axis_markers)


class IntegratedTestRunner:
    """All-in-one test execution, verification, and reporting"""
    
    def __init__(self):
        self.db = debug_db.get_debug_db()
        self.run_id = None
        self.test_results = []
        self.troubleshooting_log = []
        
    def log_troubleshoot(self, message, level="INFO"):
        """Log message for AI troubleshooting"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        entry = f"[{timestamp}] [{level}] {message}"
        self.troubleshooting_log.append(entry)
        logger.log(entry)
    
    def save_troubleshooting_log(self, filename="troubleshooting_log.txt"):
        """Save troubleshooting log to file"""
        log_path = os.path.join(script_dir, filename)
        with open(log_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("MOTION SYSTEM TROUBLESHOOTING LOG\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Run ID: {self.run_id}\n")
            f.write("=" * 80 + "\n\n")
            
            for entry in self.troubleshooting_log:
                f.write(entry + "\n")
            
            # Add database analysis
            f.write("\n" + "=" * 80 + "\n")
            f.write("DATABASE ANALYSIS\n")
            f.write("=" * 80 + "\n\n")
            
            # Test summary
            f.write("TEST SUMMARY:\n")
            summary = self.db.get_test_summary()
            for row in summary:
                status = "PASS" if row['passed'] else "FAIL"
                f.write(f"  [{status}] {row['test_name']}\n")
                f.write(f"    Commands: {row['num_commands']}, ")
                f.write(f"Failed assertions: {row['failed_assertions']}, ")
                f.write(f"Duration: {row['duration_seconds']:.2f}s\n")
            
            # Error sources
            f.write("\nERROR SOURCES (>1cm):\n")
            errors = self.db.find_error_source(tolerance_cm=1.0)
            if errors:
                for err in errors:
                    f.write(f"  Command #{err['command_index']} ({err['command_type']})\n")
                    f.write(f"    Error X: {err['error_x']:.3f} cm, ")
                    f.write(f"Error Y: {err['error_y']:.3f} cm, ")
                    f.write(f"Error Z: {err['error_z']:.3f} cm\n")
                    f.write(f"    Parameters: {err['parameters']}\n")
            else:
                f.write("  No significant errors found\n")
            
            # Command statistics
            f.write("\nCOMMAND ERROR STATISTICS:\n")
            stats = self.db.get_command_error_stats()
            if stats:
                for stat in stats:
                    f.write(f"  {stat['command_type']}:\n")
                    f.write(f"    Occurrences: {stat['occurrences']}, ")
                    f.write(f"Avg error: {stat['avg_error']:.3f}, ")
                    f.write(f"Max error: {stat['max_error']:.3f}, ")
                    f.write(f"Failures: {stat['failures']}\n")
            
            # Pass 1 vs Pass 2 comparison
            f.write("\nPASS 1 vs PASS 2 COMPARISON (>0.1cm):\n")
            comparison = self.db.compare_pass1_pass2(tolerance=0.1)
            if comparison:
                for comp in comparison[:10]:  # Top 10
                    f.write(f"  Frame {comp['frame_number']}:\n")
                    f.write(f"    X: {comp['pass1_x']:.2f} → {comp['pass2_x']:.2f} (Δ{comp['error_x']:.3f})\n")
                    f.write(f"    Y: {comp['pass1_y']:.2f} → {comp['pass2_y']:.2f} (Δ{comp['error_y']:.3f})\n")
                    f.write(f"    Z: {comp['pass1_z']:.2f} → {comp['pass2_z']:.2f} (Δ{comp['error_z']:.3f})\n")
            else:
                f.write("  No significant Pass 1→2 conversion errors\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("END OF TROUBLESHOOTING LOG\n")
            f.write("=" * 80 + "\n")
        
        self.log_troubleshoot(f"Troubleshooting log saved: {log_path}", "SUCCESS")
        return log_path
    
    def run_single_test(self, test_name, motion_plan, start_position, start_rotation, fps=30, keep_sequence=False):
        """Run a single test with verification"""
        
        self.log_troubleshoot(f"Starting test: {test_name}", "TEST")
        
        try:
            # STEP 1: Start test in database
            self.log_troubleshoot("Registering test in database", "DB")
            test_id = self.db.start_test(
                test_name=test_name,
                start_position=start_position,
                start_rotation_yaw=start_rotation.yaw,
                fps=fps
            )
            
            # STEP 2: Cleanup and create sequence
            self.log_troubleshoot("Cleaning up previous assets", "SETUP")
            cleanup.cleanup_old_assets(keep_sequence=keep_sequence)
            
            self.log_troubleshoot("Creating sequence", "SETUP")
            sequence, seq_name, next_num, fps_actual, duration_frames = sequence_setup.create_sequence(
                fps=fps, 
                duration_seconds=60,
                test_name=test_name
            )
            
            # STEP 3: Create test actor
            self.log_troubleshoot(f"Creating test mannequin at {start_position}", "SETUP")
            mannequin_name = f"TestMannequin_{test_name.replace(' ', '_')}"
            mannequin = mannequin_setup.create_mannequin(mannequin_name, start_position, start_rotation)
            
            # STEP 4: Add to sequence
            self.log_troubleshoot("Adding actor to sequence", "SETUP")
            mannequin_binding = sequence_setup.add_actor_to_sequence(sequence, mannequin, mannequin_name)
            
            # STEP 5: Setup actors info
            actors_info = {
                "test_actor": {
                    "location": start_position,
                    "rotation": start_rotation,
                    "actor": mannequin,
                    "binding": mannequin_binding
                }
            }
            
            # STEP 6: Apply motion plan
            self.log_troubleshoot(f"Applying motion plan ({len(motion_plan)} commands)", "MOTION")
            
            # Pass 1: Motion commands → Keyframes
            self.log_troubleshoot("Pass 1: Planning motion (commands → keyframes)", "PASS1")
            keyframe_data_all = motion_planner.plan_motion(motion_plan, actors_info, fps)
            
            if "test_actor" not in keyframe_data_all:
                self.log_troubleshoot("No keyframe data generated!", "ERROR")
                return False
            
            # Adapt data structure (motion_planner returns "keyframes.location" but test expects "location_keyframes")
            raw_data = keyframe_data_all["test_actor"]
            
            # Convert frame-based keyframes to include time
            location_kf = []
            for kf in raw_data["keyframes"]["location"]:
                location_kf.append({
                    "frame": kf["frame"],
                    "time": kf["frame"] / fps,
                    "x": kf["x"],
                    "y": kf["y"],
                    "z": kf["z"]
                })
            
            rotation_kf = []
            for kf in raw_data["keyframes"]["rotation"]:
                rotation_kf.append({
                    "frame": kf["frame"],
                    "time": kf["frame"] / fps,
                    "pitch": kf["pitch"],
                    "yaw": kf["yaw"],
                    "roll": kf["roll"]
                })
            
            keyframe_data = {
                "location_keyframes": location_kf,
                "rotation_keyframes": rotation_kf,
                "duration_seconds": location_kf[-1]["time"] if location_kf else 0,
                "waypoints": raw_data.get("waypoints", {})
            }
            
            self.log_troubleshoot(f"Generated {len(keyframe_data['location_keyframes'])} location keyframes", "PASS1")
            self.log_troubleshoot(f"Generated {len(keyframe_data['rotation_keyframes'])} rotation keyframes", "PASS1")
            self.log_troubleshoot(f"Total duration: {keyframe_data['duration_seconds']:.2f}s", "PASS1")
            
            # Pass 2: Keyframes → Unreal
            self.log_troubleshoot("Pass 2: Applying keyframes to Unreal", "PASS2")
            for actor_name, actor_info in actors_info.items():
                if actor_name in keyframe_data_all:
                    keyframe_applier.apply_keyframes_to_actor(
                        actor_name,
                        actor_info["actor"],
                        actor_info["binding"],
                        keyframe_data_all[actor_name],
                        fps,
                        duration_frames
                    )
            
            self.log_troubleshoot("Keyframes applied successfully", "PASS2")
            
            # STEP 7: Verify results
            self.log_troubleshoot("Starting verification", "VERIFY")
            
            passed = test_motion_system.run_test(
                keyframe_data,
                sequence,
                mannequin_binding,
                start_position,
                start_rotation.yaw,
                fps
            )
            
            # STEP 8: Update database
            duration = keyframe_data['duration_seconds']
            self.db.end_test(passed=passed, duration_seconds=duration)
            
            # STEP 9: Log results
            if passed:
                self.log_troubleshoot(f"✓ TEST PASSED: {test_name}", "SUCCESS")
            else:
                self.log_troubleshoot(f"✗ TEST FAILED: {test_name}", "FAIL")
                
                # Add diagnostic information for failures
                self.log_troubleshoot("Analyzing failure...", "DIAGNOSE")
                
                # Find error sources
                errors = self.db.find_error_source(tolerance_cm=1.0)
                if errors:
                    self.log_troubleshoot(f"Found {len(errors)} commands with >1cm error", "DIAGNOSE")
                    for err in errors[:3]:  # Top 3
                        max_err = max(err['error_x'], err['error_y'], err['error_z'])
                        self.log_troubleshoot(
                            f"  Command #{err['command_index']} ({err['command_type']}): {max_err:.2f}cm error",
                            "DIAGNOSE"
                        )
                
                # Check Pass 1 vs Pass 2
                pass_comp = self.db.compare_pass1_pass2(tolerance=0.1)
                if pass_comp:
                    self.log_troubleshoot(
                        f"Found {len(pass_comp)} keyframes with Pass1→Pass2 conversion issues",
                        "DIAGNOSE"
                    )
            
            return passed
            
        except Exception as e:
            self.log_troubleshoot(f"TEST CRASHED: {str(e)}", "CRASH")
            import traceback
            for line in traceback.format_exc().split('\n'):
                if line.strip():
                    self.log_troubleshoot(f"  {line}", "CRASH")
            return False
    
    def run_test_suite(self, test_cases):
        """Run all tests in suite"""
        
        self.log_troubleshoot("=" * 80, "INFO")
        self.log_troubleshoot("INTEGRATED MOTION TEST SUITE", "INFO")
        self.log_troubleshoot("=" * 80, "INFO")
        
        # Start run in database
        self.run_id = self.db.start_run(
            version="v3",
            notes="Integrated test runner with verification and troubleshooting logs"
        )
        self.log_troubleshoot(f"Test run ID: {self.run_id}", "DB")
        self.log_troubleshoot(f"Database: {self.db.db_path}", "DB")
        
        # Create axis markers at world origin (once for entire test run)
        axis_markers.create_axis_markers()
        
        # Default test configuration
        start_position = unreal.Vector(0, 0, 6.882729)
        start_rotation = unreal.Rotator(pitch=0.0, yaw=-90.0, roll=0.0)
        fps = 30
        
        # Run each test
        for i, test_case in enumerate(test_cases, 1):
            self.log_troubleshoot(f"\n{'='*80}", "INFO")
            self.log_troubleshoot(f"TEST {i}/{len(test_cases)}: {test_case['name']}", "INFO")
            self.log_troubleshoot(f"{'='*80}", "INFO")
            
            passed = self.run_single_test(
                test_name=test_case['name'],
                motion_plan=test_case['plan'],
                start_position=start_position,
                start_rotation=start_rotation,
                fps=fps,
                keep_sequence=test_case.get('keep_sequence', False)
            )
            
            self.test_results.append({
                'name': test_case['name'],
                'passed': passed
            })
        
        # Final summary
        self.log_troubleshoot("\n" + "=" * 80, "INFO")
        self.log_troubleshoot("FINAL RESULTS", "INFO")
        self.log_troubleshoot("=" * 80, "INFO")
        
        passed_count = sum(1 for r in self.test_results if r['passed'])
        failed_count = len(self.test_results) - passed_count
        
        for i, result in enumerate(self.test_results, 1):
            status = "✓ PASS" if result['passed'] else "✗ FAIL"
            self.log_troubleshoot(f"{i}. {status}: {result['name']}", "RESULT")
        
        self.log_troubleshoot("", "INFO")
        self.log_troubleshoot(f"Total: {len(self.test_results)} tests", "SUMMARY")
        self.log_troubleshoot(f"Passed: {passed_count}", "SUMMARY")
        self.log_troubleshoot(f"Failed: {failed_count}", "SUMMARY")
        
        if failed_count == 0:
            self.log_troubleshoot("\n🎉 ALL TESTS PASSED!", "SUCCESS")
        else:
            self.log_troubleshoot(f"\n⚠ {failed_count} test(s) failed", "FAIL")
        
# Save troubleshooting log to output folder
        output_dir = os.path.join(parent_dir, 'output')
        os.makedirs(output_dir, exist_ok=True)
        log_filename = os.path.join(output_dir, f'troubleshooting_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
        log_file = self.save_troubleshooting_log(log_filename)
        
        self.log_troubleshoot("=" * 80, "INFO")
        self.log_troubleshoot(f"Troubleshooting log: {log_file}", "INFO")
        self.log_troubleshoot(f"Database: {self.db.db_path}", "INFO")
        self.log_troubleshoot("Run query_debug_db.py for interactive analysis", "INFO")
        self.log_troubleshoot("=" * 80, "INFO")
        
        return passed_count == len(self.test_results)


# Define test cases
TEST_CASES = [
    {
        "name": "Simple Forward Movement",
        "plan": [
            {"actor": "test_actor", "command": "animation", "name": "Jog_Fwd"},
            {"actor": "test_actor", "command": "move_by_distance", "direction": "forward", "meters": 5, "speed_mph": 3}
        ]
    },
    {
        "name": "Turn and Move",
        "plan": [
            {"actor": "test_actor", "command": "animation", "name": "Jog_Fwd"},
            {"actor": "test_actor", "command": "turn_by_degree", "degrees": 90},
            {"actor": "test_actor", "command": "move_by_distance", "direction": "forward", "meters": 3, "speed_mph": 3}
        ]
    },
    {
        "name": "Move to Location",
        "plan": [
            {"actor": "test_actor", "command": "animation", "name": "Jog_Fwd"},
            {"actor": "test_actor", "command": "move_to_location", "target": [500, 500, 6.88], "speed_mph": 3}
        ]
    },
    {
        "name": "Waypoint Test",
        "plan": [
            {"actor": "test_actor", "command": "animation", "name": "Jog_Fwd"},
            {"actor": "test_actor", "command": "move_by_distance", "direction": "forward", "meters": 5, "speed_mph": 3, "waypoint_name": "point_A"},
            {"actor": "test_actor", "command": "turn_by_degree", "degrees": 180},
            {"actor": "test_actor", "command": "move_to_waypoint", "waypoint": "point_A", "speed_mph": 3}
        ]
    },
    {
        "name": "Complex Path",
        "plan": [
            {"actor": "test_actor", "command": "animation", "name": "Jog_Fwd"},
            {"actor": "test_actor", "command": "move_by_distance", "direction": "forward", "meters": 3, "speed_mph": 3},
            {"actor": "test_actor", "command": "turn_by_degree", "degrees": 90},
            {"actor": "test_actor", "command": "move_by_distance", "direction": "forward", "meters": 3, "speed_mph": 3},
            {"actor": "test_actor", "command": "turn_by_degree", "degrees": 90},
            {"actor": "test_actor", "command": "move_by_distance", "direction": "forward", "meters": 3, "speed_mph": 3},
            {"actor": "test_actor", "command": "turn_by_degree", "degrees": 90},
            {"actor": "test_actor", "command": "move_by_distance", "direction": "forward", "meters": 3, "speed_mph": 3}
        ]
    },
    {
        "name": "Square Path Return",
        "keep_sequence": True,
        "plan": [
            {"actor": "test_actor", "command": "move_by_distance", "direction": "forward", "meters": 5, "speed_mph": 3},
            {"actor": "test_actor", "command": "turn_by_degree", "degrees": 90},
            {"actor": "test_actor", "command": "move_by_distance", "direction": "forward", "meters": 5, "speed_mph": 3},
            {"actor": "test_actor", "command": "turn_by_degree", "degrees": 90},
            {"actor": "test_actor", "command": "move_by_distance", "direction": "forward", "meters": 5, "speed_mph": 3},
            {"actor": "test_actor", "command": "turn_by_degree", "degrees": 90},
            {"actor": "test_actor", "command": "move_by_distance", "direction": "forward", "meters": 5, "speed_mph": 3},
            {"actor": "test_actor", "command": "turn_by_degree", "degrees": 90}
        ]
    }
]


if __name__ == "__main__":
    try:
        runner = IntegratedTestRunner()
        all_passed = runner.run_test_suite(TEST_CASES)
        
        print("\n" + "=" * 80)
        if all_passed:
            print("✓ ALL TESTS PASSED - System is working correctly!")
        else:
            print("✗ SOME TESTS FAILED - Check troubleshooting_log.txt for details")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nTest run complete!")
