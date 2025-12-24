"""
Motion System Testing Framework
Simple verification that motion commands produce expected final positions
"""

import unreal
import sys
import os

# Add parent directory to path (to find motion_system)
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)  # Go up to unreal/
motion_system_dir = os.path.join(parent_dir, "motion_system")
if motion_system_dir not in sys.path:
    sys.path.insert(0, motion_system_dir)

# Import motion system modules directly
import motion_planner
import logger
import debug_db

class MotionTestFramework:
    """Simple testing framework for motion command system"""
    def __init__(self, use_db=True):
        self.tests_passed = 0
        self.tests_failed = 0
        self.tolerance_cm = 1.0  # Position tolerance in cm
        self.tolerance_deg = 0.5  # Rotation tolerance in degrees
        
        # Database integration
        self.use_db = use_db
        self.db = debug_db.get_debug_db() if use_db else None
    
    def log_test(self, message):
        """Log test message"""
        logger.log(f"[TEST] {message}")
    
    def assert_position(self, actual, expected, test_name):
        """Verify position matches expected within tolerance"""
        diff_x = abs(actual.x - expected.x)
        diff_y = abs(actual.y - expected.y)
        diff_z = abs(actual.z - expected.z)
        max_diff = max(diff_x, diff_y, diff_z)
        passed = max_diff <= self.tolerance_cm
        
        # Log to database
        if self.db:
            # Store individual axis assertions
            self.db.log_assertion('position_x', expected.x, actual.x, self.tolerance_cm, diff_x <= self.tolerance_cm)
            self.db.log_assertion('position_y', expected.y, actual.y, self.tolerance_cm, diff_y <= self.tolerance_cm)
            self.db.log_assertion('position_z', expected.z, actual.z, self.tolerance_cm, diff_z <= self.tolerance_cm)
        
        if max_diff <= self.tolerance_cm:
            self.tests_passed += 1
            self.log_test(f"✓ PASS: {test_name}")
            self.log_test(f"  Expected: ({expected.x:.2f}, {expected.y:.2f}, {expected.z:.2f})")
            self.log_test(f"  Actual:   ({actual.x:.2f}, {actual.y:.2f}, {actual.z:.2f})")
            self.log_test(f"  Diff:     ({diff_x:.2f}, {diff_y:.2f}, {diff_z:.2f}) cm")
            return True
        else:
            self.tests_failed += 1
            self.log_test(f"✗ FAIL: {test_name}")
            self.log_test(f"  Expected: ({expected.x:.2f}, {expected.y:.2f}, {expected.z:.2f})")
            self.log_test(f"  Actual:   ({actual.x:.2f}, {actual.y:.2f}, {actual.z:.2f})")
            self.log_test(f"  Diff:     ({diff_x:.2f}, {diff_y:.2f}, {diff_z:.2f}) cm")
            self.log_test(f"  Max diff: {max_diff:.2f} cm (tolerance: {self.tolerance_cm} cm)")
            return False
    
    def assert_rotation(self, actual_yaw, expected_yaw, test_name):
        """Verify rotation matches expected within tolerance"""
        # Normalize angles to -180 to 180
        def normalize_angle(angle):
            while angle > 180:
                angle -= 360
            while angle < -180:
                angle += 360
            return angle
        
        actual_norm = normalize_angle(actual_yaw)
        expected_norm = normalize_angle(expected_yaw)
        diff = abs(actual_norm - expected_norm)
        
        # Handle wrap-around (e.g., 179 vs -179 should be diff of 2, not 358)
        if diff > 180:
            diff = 360 - diff
        
        passed = diff <= self.tolerance_deg
        
        # Log to database
        if self.db:
            self.db.log_assertion('rotation_yaw', expected_norm, actual_norm, self.tolerance_deg, passed)
        
        if diff <= self.tolerance_deg:
            self.tests_passed += 1
            self.log_test(f"✓ PASS: {test_name}")
            self.log_test(f"  Expected: {expected_norm:.2f}°")
            self.log_test(f"  Actual:   {actual_norm:.2f}°")
            self.log_test(f"  Diff:     {diff:.2f}°")
            return True
        else:
            self.tests_failed += 1
            self.log_test(f"✗ FAIL: {test_name}")
            self.log_test(f"  Expected: {expected_norm:.2f}°")
            self.log_test(f"  Actual:   {actual_norm:.2f}°")
            self.log_test(f"  Diff:     {diff:.2f}° (tolerance: {self.tolerance_deg}°)")
            return False
    
    def assert_duration(self, actual_seconds, expected_seconds, test_name):
        """Verify duration matches expected"""
        tolerance_sec = 0.1  # 100ms tolerance
        diff = abs(actual_seconds - expected_seconds)
        passed = diff <= tolerance_sec
        
        # Log to database
        if self.db:
            self.db.log_assertion('duration', expected_seconds, actual_seconds, tolerance_sec, passed)
        
        if diff <= tolerance_sec:
            self.tests_passed += 1
            self.log_test(f"✓ PASS: {test_name}")
            self.log_test(f"  Expected: {expected_seconds:.2f}s")
            self.log_test(f"  Actual:   {actual_seconds:.2f}s")
            return True
        else:
            self.tests_failed += 1
            self.log_test(f"✗ FAIL: {test_name}")
            self.log_test(f"  Expected: {expected_seconds:.2f}s")
            self.log_test(f"  Actual:   {actual_seconds:.2f}s")
            self.log_test(f"  Diff:     {diff:.2f}s")
            return False
    
    def get_final_keyframe_from_sequence(self, sequence, actor_binding):
        """Read final keyframe values from sequence"""
        try:
            # Find transform track
            tracks = actor_binding.get_tracks()
            transform_track = None
            
            for track in tracks:
                if track.get_class().get_name() == "MovieScene3DTransformTrack":
                    transform_track = track
                    break
            
            if not transform_track:
                self.log_test("⚠ No transform track found")
                return None
            
            # Get sections
            sections = transform_track.get_sections()
            if not sections:
                self.log_test("⚠ No sections in transform track")
                return None
            
            section = sections[0]
            
            # Get channels
            channels = section.get_channels()
            location_x = None
            location_y = None
            location_z = None
            rotation_yaw = None
            
            for channel in channels:
                channel_name = channel.get_name()
                if channel_name == "Location.X":
                    location_x = channel
                elif channel_name == "Location.Y":
                    location_y = channel
                elif channel_name == "Location.Z":
                    location_z = channel
                elif channel_name == "Rotation.Z":  # Yaw is Z in Unreal
                    rotation_yaw = channel
            
            if not all([location_x, location_y, location_z]):
                self.log_test("⚠ Missing location channels")
                return None
            
            # Get all keys and find the last one
            keys_x = location_x.get_keys()
            keys_y = location_y.get_keys()
            keys_z = location_z.get_keys()
            
            if not keys_x:
                self.log_test("⚠ No keyframes found")
                return None
            
            # Last keyframe
            last_key_x = keys_x[-1]
            last_key_y = keys_y[-1]
            last_key_z = keys_z[-1]
            
            final_position = unreal.Vector(
                last_key_x.get_value(),
                last_key_y.get_value(),
                last_key_z.get_value()
            )
            
            final_yaw = 0.0
            if rotation_yaw:
                keys_yaw = rotation_yaw.get_keys()
                if keys_yaw:
                    final_yaw = keys_yaw[-1].get_value()
            
            # Get final time in frames
            final_frame = last_key_x.get_time().frame_number.value
            
            return {
                'position': final_position,
                'yaw': final_yaw,
                'frame': final_frame
            }
            
        except Exception as e:
            self.log_test(f"⚠ Error reading keyframes: {e}")
            return None
    
    def log_motion_plan_to_db(self, motion_plan, keyframe_data, fps):
        """Log commands and expected keyframes to database"""
        if self.db:
            for i, command in enumerate(motion_plan):
                command_id = self.db.log_command(
                    command_index=i,
                    actor_name=command.get('actor', 'test_actor'),
                    command_type=command['command'],
                    parameters=command,
                    start_time_seconds=0,  # Will be calculated
                    duration_seconds=0     # Will be calculated
                )
                
                # Log waypoints if created
                if 'waypoint_name' in command:
                    # Waypoint will be logged when we know its position
                    pass
            
            # Log expected keyframes
            for kf in keyframe_data['location_keyframes']:
                self.db.log_expected_keyframe(
                    command_id=self.db.current_command_id,  # Use last command for now
                    frame_number=kf['frame'],
                    time_seconds=kf['frame'] / fps,
                    x=kf['x'], y=kf['y'], z=kf['z'], yaw=0
                )
            
            for kf in keyframe_data['rotation_keyframes']:
                self.db.log_expected_keyframe(
                    command_id=self.db.current_command_id,
                    frame_number=kf['frame'],
                    time_seconds=kf['frame'] / fps,
                    x=0, y=0, z=0, yaw=kf['yaw']
                )
    
    def calculate_expected_final_state(self, keyframe_data, start_rotation):
        """Calculate expected final state from keyframe data"""
        # Get final position from last location keyframe
        if not keyframe_data['location_keyframes']:
            return None
        
        last_loc_kf = keyframe_data['location_keyframes'][-1]
        final_position = unreal.Vector(
            last_loc_kf['x'],
            last_loc_kf['y'],
            last_loc_kf['z']
        )
        
        # Get final rotation from last rotation keyframe
        final_yaw = start_rotation
        if keyframe_data['rotation_keyframes']:
            last_rot_kf = keyframe_data['rotation_keyframes'][-1]
            final_yaw = last_rot_kf['yaw']
        
        # Get duration
        duration_seconds = keyframe_data['duration_seconds']
        
        return {
            'position': final_position,
            'yaw': final_yaw,
            'duration_seconds': duration_seconds,
            'keyframe_data': keyframe_data  # Store for analysis
        }
    
    def run_tests(self):
        """Run all motion tests - Override in subclass"""
        pass
    
    def print_summary(self):
        """Print test summary"""
        total = self.tests_passed + self.tests_failed
        logger.log("\n" + "=" * 60)
        logger.log("TEST SUMMARY")
        logger.log("=" * 60)
        logger.log(f"Total tests: {total}")
        logger.log(f"✓ Passed: {self.tests_passed}")
        logger.log(f"✗ Failed: {self.tests_failed}")
        
        if self.tests_failed == 0:
            logger.log("\n🎉 ALL TESTS PASSED!")
        else:
            logger.log(f"\n⚠ {self.tests_failed} test(s) failed")
        
        logger.log("=" * 60)


# Test runner function
def run_test(motion_plan, sequence, actor_binding, start_position, start_rotation, fps=30):
    """
    Run a single motion test
    
    Args:
        motion_plan: List of motion commands
        sequence: Unreal sequence object
        actor_binding: Actor binding in sequence
        start_position: Starting position (Vector)
        start_rotation: Starting yaw rotation (float)
        fps: Frames per second
    """
    framework = MotionTestFramework()
    
    logger.log("\n" + "=" * 60)
    logger.log("MOTION SYSTEM TEST")
    logger.log("=" * 60)
    
    # Calculate expected final state
    logger.log("\n[1] Calculating expected final state...")
    expected = framework.calculate_expected_final_state(
        motion_plan, start_position, start_rotation, fps
    )
    
    if not expected:
        logger.log("✗ Failed to calculate expected state")
        return False
    
    logger.log(f"  Expected position: ({expected['position'].x:.2f}, {expected['position'].y:.2f}, {expected['position'].z:.2f})")
    logger.log(f"  Expected rotation: {expected['yaw']:.2f}°")
    logger.log(f"  Expected duration: {expected['duration_seconds']:.2f}s")
    
    # Read actual final state from sequence
    logger.log("\n[2] Reading actual final state from sequence...")
    actual = framework.get_final_keyframe_from_sequence(sequence, actor_binding)
    
    if not actual:
        logger.log("✗ Failed to read actual state from sequence")
        return False
    
    actual_duration = actual['frame'] / fps
    
    logger.log(f"  Actual position: ({actual['position'].x:.2f}, {actual['position'].y:.2f}, {actual['position'].z:.2f})")
    logger.log(f"  Actual rotation: {actual['yaw']:.2f}°")
    logger.log(f"  Actual duration: {actual_duration:.2f}s")
    
    # Run assertions
    logger.log("\n[3] Running assertions...")
    framework.assert_position(actual['position'], expected['position'], "Final Position")
    framework.assert_rotation(actual['yaw'], expected['yaw'], "Final Rotation")
    framework.assert_duration(actual_duration, expected['duration_seconds'], "Total Duration")
    
    # Print summary
    framework.print_summary()
    
    return framework.tests_failed == 0


# Example usage
if __name__ == "__main__":
    logger.log("Motion System Testing Framework loaded")
    logger.log("Usage: run_test(motion_plan, sequence, actor_binding, start_position, start_rotation)")
