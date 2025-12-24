"""
Motion System Debug Database
SQLite-based structured logging and analysis for motion command debugging
"""

import sqlite3
import json
import os
from datetime import datetime

class DebugDB:
    """SQLite debug database with structured logging and query capabilities"""
    
    def __init__(self, db_path=None):
        if db_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(script_dir, 'motion_debug.db')
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        self.cursor = self.conn.cursor()
        
        self.current_run_id = None
        self.current_test_id = None
        self.current_command_id = None
        
        self._create_schema()
    
    def _create_schema(self):
        """Create database schema"""
        
        # Test runs (top level)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_runs (
                run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                version TEXT,
                notes TEXT
            )
        ''')
        
        # Individual tests
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tests (
                test_id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                test_name TEXT NOT NULL,
                start_position_x REAL,
                start_position_y REAL,
                start_position_z REAL,
                start_rotation_yaw REAL,
                fps INTEGER,
                passed INTEGER,
                duration_seconds REAL,
                timestamp TEXT,
                FOREIGN KEY (run_id) REFERENCES test_runs(run_id)
            )
        ''')
        
        # Motion commands
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS commands (
                command_id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id INTEGER NOT NULL,
                command_index INTEGER NOT NULL,
                actor_name TEXT NOT NULL,
                command_type TEXT NOT NULL,
                parameters TEXT,
                start_time_seconds REAL,
                duration_seconds REAL,
                FOREIGN KEY (test_id) REFERENCES tests(test_id)
            )
        ''')
        
        # Expected keyframes (Pass 1 - motion_planner output)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS keyframes_expected (
                keyframe_id INTEGER PRIMARY KEY AUTOINCREMENT,
                command_id INTEGER NOT NULL,
                frame_number INTEGER NOT NULL,
                time_seconds REAL,
                x REAL,
                y REAL,
                z REAL,
                yaw REAL,
                FOREIGN KEY (command_id) REFERENCES commands(command_id)
            )
        ''')
        
        # Actual keyframes (Pass 2 - read from Unreal sequence)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS keyframes_actual (
                keyframe_id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id INTEGER NOT NULL,
                frame_number INTEGER NOT NULL,
                time_seconds REAL,
                x REAL,
                y REAL,
                z REAL,
                yaw REAL,
                FOREIGN KEY (test_id) REFERENCES tests(test_id)
            )
        ''')
        
        # Test assertions
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS assertions (
                assertion_id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id INTEGER NOT NULL,
                assertion_type TEXT NOT NULL,
                expected_value REAL,
                actual_value REAL,
                tolerance REAL,
                passed INTEGER,
                error_magnitude REAL,
                FOREIGN KEY (test_id) REFERENCES tests(test_id)
            )
        ''')
        
        # Waypoints created during test
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS waypoints (
                waypoint_id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id INTEGER NOT NULL,
                waypoint_name TEXT NOT NULL,
                x REAL,
                y REAL,
                z REAL,
                created_at_command_index INTEGER,
                FOREIGN KEY (test_id) REFERENCES tests(test_id)
            )
        ''')
        
        # Create useful indexes
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_commands_test ON commands(test_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_keyframes_exp_cmd ON keyframes_expected(command_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_keyframes_act_test ON keyframes_actual(test_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_assertions_test ON assertions(test_id)')
        
        self.conn.commit()
    
    def start_run(self, version="v3", notes=None):
        """Start a new test run"""
        timestamp = datetime.now().isoformat()
        self.cursor.execute('''
            INSERT INTO test_runs (timestamp, version, notes)
            VALUES (?, ?, ?)
        ''', (timestamp, version, notes))
        self.conn.commit()
        self.current_run_id = self.cursor.lastrowid
        return self.current_run_id
    
    def start_test(self, test_name, start_position, start_rotation_yaw, fps):
        """Start a new test"""
        timestamp = datetime.now().isoformat()
        self.cursor.execute('''
            INSERT INTO tests (run_id, test_name, start_position_x, start_position_y, 
                             start_position_z, start_rotation_yaw, fps, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (self.current_run_id, test_name, 
              start_position.x, start_position.y, start_position.z,
              start_rotation_yaw, fps, timestamp))
        self.conn.commit()
        self.current_test_id = self.cursor.lastrowid
        return self.current_test_id
    
    def end_test(self, passed, duration_seconds):
        """Mark test as complete"""
        self.cursor.execute('''
            UPDATE tests 
            SET passed = ?, duration_seconds = ?
            WHERE test_id = ?
        ''', (1 if passed else 0, duration_seconds, self.current_test_id))
        self.conn.commit()
    
    def log_command(self, command_index, actor_name, command_type, parameters, 
                   start_time_seconds, duration_seconds):
        """Log a motion command"""
        self.cursor.execute('''
            INSERT INTO commands (test_id, command_index, actor_name, command_type, 
                                parameters, start_time_seconds, duration_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (self.current_test_id, command_index, actor_name, command_type,
              json.dumps(parameters), start_time_seconds, duration_seconds))
        self.conn.commit()
        self.current_command_id = self.cursor.lastrowid
        return self.current_command_id
    
    def log_expected_keyframe(self, command_id, frame_number, time_seconds, x, y, z, yaw):
        """Log expected keyframe from motion planner (Pass 1)"""
        self.cursor.execute('''
            INSERT INTO keyframes_expected (command_id, frame_number, time_seconds, x, y, z, yaw)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (command_id, frame_number, time_seconds, x, y, z, yaw))
        self.conn.commit()
    
    def log_actual_keyframe(self, test_id, frame_number, time_seconds, x, y, z, yaw):
        """Log actual keyframe from Unreal sequence (Pass 2)"""
        self.cursor.execute('''
            INSERT INTO keyframes_actual (test_id, frame_number, time_seconds, x, y, z, yaw)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (test_id, frame_number, time_seconds, x, y, z, yaw))
        self.conn.commit()
    
    def log_assertion(self, assertion_type, expected_value, actual_value, tolerance, passed):
        """Log a test assertion"""
        error_magnitude = abs(expected_value - actual_value)
        self.cursor.execute('''
            INSERT INTO assertions (test_id, assertion_type, expected_value, actual_value, 
                                  tolerance, passed, error_magnitude)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (self.current_test_id, assertion_type, expected_value, actual_value, 
              tolerance, 1 if passed else 0, error_magnitude))
        self.conn.commit()
    
    def log_waypoint(self, waypoint_name, x, y, z, created_at_command_index):
        """Log waypoint creation"""
        self.cursor.execute('''
            INSERT INTO waypoints (test_id, waypoint_name, x, y, z, created_at_command_index)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.current_test_id, waypoint_name, x, y, z, created_at_command_index))
        self.conn.commit()
    
    def query(self, sql, params=None):
        """Execute query and return results"""
        if params:
            self.cursor.execute(sql, params)
        else:
            self.cursor.execute(sql)
        return self.cursor.fetchall()
    
    def close(self):
        """Close database connection"""
        self.conn.close()
    
    # ===== ANALYSIS QUERIES =====
    
    def find_error_source(self, tolerance_cm=1.0):
        """Find which command introduced position error > tolerance"""
        return self.query('''
            SELECT 
                c.command_index,
                c.command_type,
                c.parameters,
                ABS(ke.x - ka.x) as error_x,
                ABS(ke.y - ka.y) as error_y,
                ABS(ke.z - ka.z) as error_z
            FROM commands c
            JOIN keyframes_expected ke ON c.command_id = ke.command_id
            JOIN keyframes_actual ka ON ke.frame_number = ka.frame_number
            WHERE c.test_id = ?
              AND (ABS(ke.x - ka.x) > ? OR ABS(ke.y - ka.y) > ? OR ABS(ke.z - ka.z) > ?)
            ORDER BY c.command_index
        ''', (self.current_test_id, tolerance_cm, tolerance_cm, tolerance_cm))
    
    def get_command_error_stats(self):
        """Get error statistics by command type across all tests"""
        return self.query('''
            SELECT 
                c.command_type,
                COUNT(*) as occurrences,
                AVG(a.error_magnitude) as avg_error,
                MAX(a.error_magnitude) as max_error,
                SUM(CASE WHEN a.passed = 0 THEN 1 ELSE 0 END) as failures
            FROM commands c
            JOIN tests t ON c.test_id = t.test_id
            JOIN assertions a ON t.test_id = a.test_id
            WHERE t.run_id = ?
            GROUP BY c.command_type
            ORDER BY failures DESC, avg_error DESC
        ''', (self.current_run_id,))
    
    def compare_pass1_pass2(self, tolerance=0.1):
        """Compare Pass 1 (expected) vs Pass 2 (actual) keyframes"""
        return self.query('''
            SELECT 
                ke.frame_number,
                ke.x as pass1_x, ka.x as pass2_x, (ke.x - ka.x) as error_x,
                ke.y as pass1_y, ka.y as pass2_y, (ke.y - ka.y) as error_y,
                ke.z as pass1_z, ka.z as pass2_z, (ke.z - ka.z) as error_z,
                ke.yaw as pass1_yaw, ka.yaw as pass2_yaw, (ke.yaw - ka.yaw) as error_yaw
            FROM keyframes_expected ke
            JOIN commands c ON ke.command_id = c.command_id
            JOIN keyframes_actual ka ON ke.frame_number = ka.frame_number AND ka.test_id = c.test_id
            WHERE c.test_id = ?
              AND (ABS(ke.x - ka.x) > ? OR ABS(ke.y - ka.y) > ? OR ABS(ke.z - ka.z) > ?)
            ORDER BY ke.frame_number
        ''', (self.current_test_id, tolerance, tolerance, tolerance))
    
    def get_test_summary(self):
        """Get summary of current test run"""
        return self.query('''
            SELECT 
                test_name,
                passed,
                duration_seconds,
                (SELECT COUNT(*) FROM commands WHERE test_id = t.test_id) as num_commands,
                (SELECT COUNT(*) FROM assertions WHERE test_id = t.test_id AND passed = 0) as failed_assertions
            FROM tests t
            WHERE run_id = ?
            ORDER BY test_id
        ''', (self.current_run_id,))
    
    def get_regression_analysis(self, baseline_run_id):
        """Compare current run with baseline to detect regressions"""
        return self.query('''
            SELECT 
                current.test_name,
                current.passed as current_passed,
                baseline.passed as baseline_passed,
                CASE 
                    WHEN current.passed = 0 AND baseline.passed = 1 THEN 'REGRESSION'
                    WHEN current.passed = 1 AND baseline.passed = 0 THEN 'FIXED'
                    ELSE 'NO CHANGE'
                END as status
            FROM tests current
            LEFT JOIN tests baseline ON current.test_name = baseline.test_name
            WHERE current.run_id = ? AND baseline.run_id = ?
        ''', (self.current_run_id, baseline_run_id))
    
    def calculate_actual_speed(self, command_id, fps=30):
        """Calculate actual speed from keyframes for a command"""
        return self.query('''
            WITH movement AS (
                SELECT 
                    ke.frame_number,
                    ke.x, ke.y,
                    LAG(ke.x) OVER (ORDER BY ke.frame_number) as prev_x,
                    LAG(ke.y) OVER (ORDER BY ke.frame_number) as prev_y,
                    LAG(ke.frame_number) OVER (ORDER BY ke.frame_number) as prev_frame
                FROM keyframes_expected ke
                WHERE ke.command_id = ?
            )
            SELECT 
                AVG(
                    SQRT(POW(x - prev_x, 2) + POW(y - prev_y, 2)) / 
                    ((frame_number - prev_frame) / ?) * 0.0223694
                ) as actual_mph
            FROM movement
            WHERE prev_frame IS NOT NULL
        ''', (command_id, fps))
    
    def print_report(self):
        """Print comprehensive debug report"""
        print("\n" + "=" * 60)
        print("DEBUG DATABASE REPORT")
        print("=" * 60)
        
        # Test summary
        print("\nTEST SUMMARY:")
        summary = self.get_test_summary()
        for row in summary:
            status = "✓ PASS" if row['passed'] else "✗ FAIL"
            print(f"  {status}: {row['test_name']}")
            print(f"    Commands: {row['num_commands']}, Failed assertions: {row['failed_assertions']}, Duration: {row['duration_seconds']:.2f}s")
        
        # Command error stats
        print("\nCOMMAND ERROR STATISTICS:")
        stats = self.get_command_error_stats()
        if stats:
            for row in stats:
                print(f"  {row['command_type']}:")
                print(f"    Occurrences: {row['occurrences']}, Avg error: {row['avg_error']:.3f}, Max error: {row['max_error']:.3f}, Failures: {row['failures']}")
        else:
            print("  No data available")
        
        print("=" * 60)


# Global instance for easy access
_db_instance = None

def get_debug_db():
    """Get or create global debug database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DebugDB()
    return _db_instance

def close_debug_db():
    """Close global debug database"""
    global _db_instance
    if _db_instance:
        _db_instance.close()
        _db_instance = None
