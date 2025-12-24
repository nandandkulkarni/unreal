"""
Motion System Test Runner
Creates a simple test scene and validates motion commands
"""

import unreal
import sys
import os
import importlib

# Add parent directories to path
# Use absolute paths since __file__ is not available in remove execution context
script_dir = r"C:\UnrealProjects\Coding\unreal\motion_system\tests"
motion_system_dir = r"C:\UnrealProjects\Coding\unreal\motion_system"
unreal_dir = r"C:\UnrealProjects\Coding\unreal"

if unreal_dir not in sys.path:
    sys.path.insert(0, unreal_dir)
if motion_system_dir not in sys.path:
    sys.path.insert(0, motion_system_dir)

# Import motion system modules from parent package
from motion_system import logger, cleanup, sequence_setup, mannequin_setup
from motion_system import motion_planner, keyframe_applier, debug_db
from motion_system import test_motion_system

# Reload for development
importlib.reload(logger)
importlib.reload(cleanup)
importlib.reload(sequence_setup)
importlib.reload(mannequin_setup)
importlib.reload(motion_planner)
importlib.reload(keyframe_applier)
importlib.reload(debug_db)
importlib.reload(test_motion_system)

# Test configuration
FPS = 30
SEQUENCE_DURATION = 15

# Test cases
TEST_CASES = [
    {
        "name": "Simple Forward Movement",
        "plan": [
            {"command": "add_actor", "actor": "test_actor", "location": [0, 0, 6.882729], "rotation": [0,  0,0], "mesh_path": "/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica"},
            {"command": "add_camera", "actor": "test_camera", "location": [0, -300, 150], "rotation": [0, 45, 0]},
            {"actor": "test_actor", "command": "animation", "name": "Jog_Fwd"},
            {"actor": "test_actor", "command": "move_by_distance", "direction": "forward", "meters": 5, "speed_mph": 3}
        ]
    },
    {
        "name": "Turn and Move",
        "plan": [
            {"command": "add_actor", "actor": "test_actor", "location": [0, 0, 6.882729], "rotation": [0,  0,0], "mesh_path": "/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica"},
            {"command": "add_camera", "actor": "test_camera", "location": [0, -300, 150], "rotation": [0, 45, 0]},
            {"actor": "test_actor", "command": "animation", "name": "Jog_Fwd"},
            {"actor": "test_actor", "command": "turn_by_degree", "degrees": 90},
            {"actor": "test_actor", "command": "move_by_distance", "direction": "forward", "meters": 3, "speed_mph": 3}
        ]
    },
    {
        "name": "Move to Location",
        "plan": [
            {"command": "add_actor", "actor": "test_actor", "location": [0, 0, 6.882729], "rotation": [0,  0,0], "mesh_path": "/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica"},
            {"command": "add_camera", "actor": "test_camera", "location": [0, -300, 150], "rotation": [0, 45, 0]},
            {"actor": "test_actor", "command": "animation", "name": "Jog_Fwd"},
            {"actor": "test_actor", "command": "move_to_location", "target": [500, 500, 6.88], "speed_mph": 3}
        ]
    },
    {
        "name": "Waypoint Test",
        "plan": [
            {"command": "add_actor", "actor": "test_actor", "location": [0, 0, 6.882729], "rotation": [0,  0,0], "mesh_path": "/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica"},
            {"command": "add_camera", "actor": "test_camera", "location": [0, -300, 150], "rotation": [0, 45, 0]},
            {"actor": "test_actor", "command": "animation", "name": "Jog_Fwd"},
            {"actor": "test_actor", "command": "move_by_distance", "direction": "forward", "meters": 5, "speed_mph": 3, "waypoint_name": "point_A"},
            {"actor": "test_actor", "command": "turn_by_degree", "degrees": 180},
            {"actor": "test_actor", "command": "move_to_waypoint", "waypoint": "point_A", "speed_mph": 3}
        ]
    },
    {
        "name": "Complex Path",
        "plan": [
            {"command": "add_actor", "actor": "test_actor", "location": [0, 0, 6.882729], "rotation": [0, -90, 0], "mesh_path": "/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica"},
            {"command": "add_camera", "actor": "test_camera", "location": [0, -300, 150], "rotation": [0, 45, 0]},
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
    # {
    #     "name": "Dynamic Spawning",
    #     "verify_actor": "spawned_actor",
    #     "plan": [
    #         {"command": "add_actor", "actor": "spawned_actor", "location": [0, 0, 6.882729], "rotation": [0,  0,0], "mesh_path": "/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica"},
    #         {"actor": "spawned_actor", "command": "animation", "name": "Jog_Fwd"},
    #         {"actor": "spawned_actor", "command": "move_by_distance", "direction": "forward", "meters": 3, "speed_mph": 3},
    #         {"command": "add_camera", "actor": "spawned_cam", "location": [200, 0, 150], "rotation": [0, -45, 0]},
    #         {"actor": "spawned_cam", "command": "camera_move", "location": [200, 200, 150], "rotation": [0, -45, 90], "duration": 2.0}
    #     ]
    # }
]


def run_all_tests():
    """Run all test cases"""
    
    logger.log("=" * 60)
    logger.log("MOTION SYSTEM TEST SUITE")
    logger.log("=" * 60)
    
    # Initialize database
    db = debug_db.get_debug_db()
    run_id = db.start_run(version="v3", notes="Automated test suite with SQLite logging")
    logger.log(f"\nDatabase run ID: {run_id}")
    logger.log(f"Database path: {db.db_path}")
    
    test_results = []
    
    for i, test_case in enumerate(TEST_CASES, 1):
        logger.log(f"\n{'='*60}")
        logger.log(f"TEST {i}/{len(TEST_CASES)}: {test_case['name']}")
        logger.log(f"{'='*60}")
        # Start test in database
        db.start_test(
            test_name=test_case['name'],
            fps=FPS
        )
            
            # 
        try:
            # Create fresh sequence for this test
            sequence_name = f"MotionTest_{i:02d}"
            logger.log(f"\nCreating test sequence: {sequence_name}")
            
            # Cleanup previous test
            cleanup.cleanup_old_assets()
            
            # Create sequence
            sequence, seq_name, next_num, fps, duration_frames = sequence_setup.create_sequence(
                fps=FPS, 
                duration_seconds=SEQUENCE_DURATION
            )
            
            # Setup actors info (initially empty)
            actors_info = {}
            
            # Apply motion plan
            logger.log(f"\nApplying motion plan ({len(test_case['plan'])} commands)...")
            keyframe_data_all = motion_planner.plan_motion(test_case['plan'], actors_info, fps, sequence=sequence)
            
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
            
            # Determine which actor to verify
            verify_actor_name = test_case.get("verify_actor", "test_actor")
            
            # Adapt data structure for verifier
            if verify_actor_name not in keyframe_data_all:
                raise Exception(f"Verification actor '{verify_actor_name}' not found in keyframe data")
                
            raw_data = keyframe_data_all[verify_actor_name]
            verify_actor_info = actors_info[verify_actor_name]
            
            # Convert frame-based keyframes to include time
            location_kf = []
            for kf in raw_data["keyframes"]["location"]:
                location_kf.append({
                    "frame": kf["frame"],
                    "time": kf["frame"] / fps,
                    "x": kf["x"], "y": kf["y"], "z": kf["z"]
                })
            
            rotation_kf = []
            for kf in raw_data["keyframes"]["rotation"]:
                rotation_kf.append({
                    "frame": kf["frame"],
                    "time": kf["frame"] / fps,
                    "pitch": kf["pitch"], "yaw": kf["yaw"], "roll": kf["roll"]
                })
            
            keyframe_data = {
                "location_keyframes": location_kf,
                "rotation_keyframes": rotation_kf,
                "duration_seconds": location_kf[-1]["time"] if location_kf else 0,
                "waypoints": raw_data.get("waypoints", {})
            }

            # Run test validation
            logger.log(f"\nValidating results for '{verify_actor_name}'...")
            passed = test_motion_system.run_test(
                keyframe_data,
                sequence,
                verify_actor_info["binding"],
                verify_actor_info["location"],
                verify_actor_info["rotation"].yaw,
                fps
            )
            
            # End test in database
            duration = keyframe_data['duration_seconds']
            db.end_test(passed=passed, duration_seconds=duration)
            
            test_results.append({
                'name': test_case['name'],
                'passed': passed
            })
            
        except Exception as e:
            logger.log(f"\n✗ TEST CRASHED: {e}")
            import traceback
            logger.log(traceback.format_exc())
            test_results.append({
                'name': test_case['name'],
                'passed': False,
                'error': str(e)
            })
    
    # Final summary
    logger.log("\n" + "=" * 60)
    logger.log("FINAL TEST SUITE SUMMARY")
    logger.log("=" * 60)
    
    passed_count = sum(1 for r in test_results if r['passed'])
    failed_count = len(test_results) - passed_count
    
    for i, result in enumerate(test_results, 1):
        status = "✓ PASS" if result['passed'] else "✗ FAIL"
        logger.log(f"{i}. {status}: {result['name']}")
        if 'error' in result:
            logger.log(f"   Error: {result['error']}")
    
    
    # Print database report
    db.print_report()
    
    # Provide analysis hints
    logger.log("\n" + "=" * 60)
    logger.log("DATABASE ANALYSIS QUERIES")
    logger.log("=" * 60)
    logger.log("You can run these queries for deeper analysis:")
    logger.log("")
    logger.log("# Find which commands introduced errors:")
    logger.log("db.find_error_source(tolerance_cm=1.0)")
    logger.log("")
    logger.log("# Get error statistics by command type:")
    logger.log("db.get_command_error_stats()")
    logger.log("")
    logger.log("# Compare Pass 1 vs Pass 2 keyframes:")
    logger.log("db.compare_pass1_pass2(tolerance=0.1)")
    logger.log("")
    logger.log("# Get test summary:")
    logger.log("db.get_test_summary()")
    logger.log("=" * 60)
    logger.log("\n" + "-" * 60)
    logger.log(f"Total: {len(test_results)} tests")
    logger.log(f"✓ Passed: {passed_count}")
    logger.log(f"✗ Failed: {failed_count}")
    
    if failed_count == 0:
        logger.log("\n🎉 ALL TESTS PASSED!")
    else:
        logger.log(f"\n⚠ {failed_count} test(s) failed")
    
    logger.log("=" * 60)


if __name__ == "__main__":
    try:
        run_all_tests()
    except Exception as e:
        logger.log(f"\n✗ FATAL ERROR: {e}")
        import traceback
        logger.log(traceback.format_exc())
    
    print("\nTest run complete!")
