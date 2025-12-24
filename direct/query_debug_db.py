"""
Database Query Helper - Interactive analysis of motion test results
"""

import sys
import os

# Add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from motion_system import debug_db, logger

# Get database instance
db = debug_db.get_debug_db()

def show_menu():
    """Display analysis menu"""
    print("\n" + "=" * 60)
    print("MOTION DEBUG DATABASE - QUERY HELPER")
    print("=" * 60)
    print("\nAvailable Queries:")
    print("  1. Test Summary")
    print("  2. Find Error Sources (> 1cm)")
    print("  3. Command Error Statistics")
    print("  4. Compare Pass 1 vs Pass 2")
    print("  5. Speed Validation")
    print("  6. Full Report")
    print("  7. Custom SQL Query")
    print("  0. Exit")
    print("=" * 60)

def print_rows(rows, title):
    """Pretty print query results"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    
    if not rows:
        print("No results found")
        return
    
    # Print column headers
    if hasattr(rows[0], 'keys'):
        headers = rows[0].keys()
        header_line = " | ".join(f"{h:15}" for h in headers)
        print(header_line)
        print("-" * len(header_line))
        
        # Print rows
        for row in rows:
            values = [str(row[h]) for h in headers]
            print(" | ".join(f"{v:15}" for v in values))
    else:
        # Simple tuple rows
        for row in rows:
            print(row)
    
    print(f"\nTotal: {len(rows)} row(s)")
    print("=" * 60)

def query_test_summary():
    """Show test summary"""
    rows = db.get_test_summary()
    print_rows(rows, "TEST SUMMARY")
    
    # Calculate stats
    if rows:
        total = len(rows)
        passed = sum(1 for r in rows if r['passed'])
        print(f"\nPass rate: {passed}/{total} ({100*passed/total:.1f}%)")

def query_error_sources():
    """Find commands that introduced errors"""
    rows = db.find_error_source(tolerance_cm=1.0)
    print_rows(rows, "ERROR SOURCES (> 1cm tolerance)")
    
    if rows:
        print("\nCommands with highest errors:")
        for row in sorted(rows, key=lambda r: max(r['error_x'], r['error_y'], r['error_z']), reverse=True)[:5]:
            max_error = max(row['error_x'], row['error_y'], row['error_z'])
            print(f"  Command #{row['command_index']} ({row['command_type']}): {max_error:.2f} cm")

def query_command_stats():
    """Show error statistics by command type"""
    rows = db.get_command_error_stats()
    print_rows(rows, "COMMAND ERROR STATISTICS")
    
    if rows:
        print("\nMost problematic commands:")
        for row in sorted(rows, key=lambda r: r['failures'], reverse=True)[:5]:
            print(f"  {row['command_type']}: {row['failures']} failures, avg error {row['avg_error']:.3f}")

def query_pass1_pass2():
    """Compare Pass 1 vs Pass 2 keyframes"""
    rows = db.compare_pass1_pass2(tolerance=0.1)
    print_rows(rows, "PASS 1 vs PASS 2 COMPARISON (> 0.1cm tolerance)")
    
    if rows:
        print("\nLargest conversion errors:")
        for row in sorted(rows, key=lambda r: max(abs(r['error_x']), abs(r['error_y']), abs(r['error_z'])), reverse=True)[:5]:
            max_error = max(abs(row['error_x']), abs(row['error_y']), abs(row['error_z']))
            print(f"  Frame {row['frame_number']}: {max_error:.3f} cm")

def query_speed_validation():
    """Validate speed calculations"""
    print("\nSpeed Validation")
    print("=" * 60)
    
    # Get all commands with speed
    rows = db.query('''
        SELECT command_id, command_type, parameters
        FROM commands
        WHERE parameters LIKE '%speed_mph%' OR parameters LIKE '%speed_mps%'
    ''')
    
    if not rows:
        print("No speed-based commands found")
        return
    
    import json
    for row in rows:
        params = json.loads(row['parameters'])
        intended_speed = params.get('speed_mph', params.get('speed_mps', 'unknown'))
        
        # Calculate actual speed
        actual_rows = db.calculate_actual_speed(row['command_id'])
        if actual_rows and actual_rows[0]['actual_mph']:
            actual = actual_rows[0]['actual_mph']
            print(f"Command {row['command_id']} ({row['command_type']}): Intended {intended_speed} mph, Actual {actual:.2f} mph")
        else:
            print(f"Command {row['command_id']} ({row['command_type']}): Cannot calculate actual speed")

def custom_query():
    """Run custom SQL query"""
    print("\nEnter SQL query (or 'back' to return):")
    print("Available tables: test_runs, tests, commands, keyframes_expected, keyframes_actual, assertions, waypoints")
    query = input("> ")
    
    if query.lower() == 'back':
        return
    
    try:
        rows = db.query(query)
        print_rows(rows, "CUSTOM QUERY RESULTS")
    except Exception as e:
        print(f"\n✗ Query error: {e}")

def interactive_mode():
    """Run interactive query mode"""
    while True:
        show_menu()
        choice = input("\nSelect option: ")
        
        if choice == '0':
            print("Exiting...")
            break
        elif choice == '1':
            query_test_summary()
        elif choice == '2':
            query_error_sources()
        elif choice == '3':
            query_command_stats()
        elif choice == '4':
            query_pass1_pass2()
        elif choice == '5':
            query_speed_validation()
        elif choice == '6':
            db.print_report()
        elif choice == '7':
            custom_query()
        else:
            print("Invalid option")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    print("Motion Debug Database Query Helper")
    print(f"Database: {db.db_path}")
    
    # Check if database has data
    test_count = db.query("SELECT COUNT(*) as count FROM tests")[0]['count']
    if test_count == 0:
        print("\n⚠ Database is empty. Run tests first: run_motion_tests.py")
    else:
        print(f"\nFound {test_count} test(s) in database")
        interactive_mode()
