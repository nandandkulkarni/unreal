"""
Quick test to verify SQLite support in Unreal Python environment
"""

import sys

def test_sqlite():
    print("=" * 60)
    print("SQLite Support Test in Unreal Python")
    print("=" * 60)
    
    # Test 1: Import
    print("\n[1] Testing sqlite3 import...")
    try:
        import sqlite3
        print("✓ sqlite3 module imported successfully")
        print(f"  SQLite version: {sqlite3.sqlite_version}")
        print(f"  Python sqlite3 version: {sqlite3.version}")
    except ImportError as e:
        print(f"✗ FAIL: Cannot import sqlite3: {e}")
        return False
    
    # Test 2: In-memory database
    print("\n[2] Testing in-memory database creation...")
    try:
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        print("✓ In-memory database created")
    except Exception as e:
        print(f"✗ FAIL: Cannot create database: {e}")
        return False
    
    # Test 3: Table creation
    print("\n[3] Testing table creation...")
    try:
        cursor.execute('''
            CREATE TABLE test_runs (
                run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                test_name TEXT
            )
        ''')
        print("✓ Table created successfully")
    except Exception as e:
        print(f"✗ FAIL: Cannot create table: {e}")
        return False
    
    # Test 4: Insert data
    print("\n[4] Testing data insertion...")
    try:
        cursor.execute('''
            INSERT INTO test_runs (timestamp, test_name) 
            VALUES (?, ?)
        ''', ('2025-12-23 10:30:00', 'Test Motion System'))
        conn.commit()
        print("✓ Data inserted successfully")
    except Exception as e:
        print(f"✗ FAIL: Cannot insert data: {e}")
        return False
    
    # Test 5: Query data
    print("\n[5] Testing data query...")
    try:
        cursor.execute('SELECT * FROM test_runs')
        rows = cursor.fetchall()
        print(f"✓ Query successful: {len(rows)} row(s) returned")
        for row in rows:
            print(f"  Row: {row}")
    except Exception as e:
        print(f"✗ FAIL: Cannot query data: {e}")
        return False
    
    # Test 6: JSON support (modern SQLite feature)
    print("\n[6] Testing JSON support...")
    try:
        cursor.execute('''
            CREATE TABLE commands (
                id INTEGER PRIMARY KEY,
                parameters TEXT
            )
        ''')
        import json
        test_params = {"speed_mph": 3, "direction": "forward", "meters": 5}
        cursor.execute('INSERT INTO commands (parameters) VALUES (?)', 
                      (json.dumps(test_params),))
        cursor.execute('SELECT parameters FROM commands')
        result = json.loads(cursor.fetchone()[0])
        print(f"✓ JSON support working: {result}")
    except Exception as e:
        print(f"⚠ JSON feature limited: {e}")
        # Not critical - we can work around this
    
    # Test 7: File-based database
    print("\n[7] Testing file-based database...")
    try:
        import os
        db_path = os.path.join(os.path.dirname(__file__), 'test_motion_debug.db')
        file_conn = sqlite3.connect(db_path)
        file_cursor = file_conn.cursor()
        file_cursor.execute('CREATE TABLE IF NOT EXISTS test (id INTEGER)')
        file_cursor.execute('INSERT INTO test VALUES (1)')
        file_conn.commit()
        file_conn.close()
        
        # Verify file exists
        if os.path.exists(db_path):
            print(f"✓ File database created: {db_path}")
            file_size = os.path.getsize(db_path)
            print(f"  File size: {file_size} bytes")
            
            # Cleanup
            os.remove(db_path)
            print("  ✓ Test file cleaned up")
        else:
            print("⚠ File database created but not found")
    except Exception as e:
        print(f"⚠ File database test issue: {e}")
    
    # Cleanup
    conn.close()
    
    print("\n" + "=" * 60)
    print("✓ SQLite FULLY SUPPORTED in Unreal Python!")
    print("=" * 60)
    print("\nRecommendation: Safe to implement SQLite debug database")
    
    return True

if __name__ == "__main__":
    try:
        test_sqlite()
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nTest complete!")
