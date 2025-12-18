"""
Unreal Engine Remote Python Execution Module

This module allows you to execute Python code inside Unreal Engine from external Python scripts.
It uses the Remote Control API to send Python commands to Unreal's Python interpreter.

Prerequisites:
1. Unreal Engine must be running
2. Remote Control plugin must be enabled (Edit → Plugins → "Remote Control")
3. WebControl server must be started (in Unreal console: WebControl.StartServer)
4. PythonScriptLibrary must be exposed in Remote Control settings

Usage:
    from unreal_connection import UnrealRemote
    
    unreal = UnrealRemote()
    if unreal.is_connected():
        # Execute Python code that runs inside Unreal
        code = '''
import unreal
actors = unreal.EditorLevelLibrary.get_all_level_actors()
print(f"Found {len(actors)} actors")
'''
        unreal.execute_python(code)
"""

import requests
import json
import sys


class UnrealRemote:
    """
    Remote Python execution for Unreal Engine.
    
    This class allows you to execute Python code inside Unreal Engine from external scripts.
    The code runs in Unreal's Python interpreter and has access to the 'unreal' module.
    """
    
    def __init__(self, host="localhost", port=30010):
        """
        Initialize remote connection to Unreal Engine.
        
        Args:
            host: Hostname where Unreal is running (default: localhost)
            port: Remote Control API port (default: 30010)
        """
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}/remote/object/call"
        self.timeout = 10
    
    def is_connected(self):
        """
        Test if Unreal Engine Remote Control API is accessible.
        
        Returns:
            True if connected, False otherwise
        """
        try:
            # Try to access the base remote control endpoint
            test_url = f"http://{self.host}:{self.port}/remote/info"
            response = requests.get(test_url, timeout=5)
            # Any response from /remote/* means the server is running
            return response.status_code in [200, 404]
        except Exception as e:
            return False
    
    def execute_python(self, python_code):
        """
        Execute Python code inside Unreal Engine.
        
        The code runs in Unreal's Python interpreter and has full access to the 'unreal' module.
        
        Args:
            python_code: Python code string to execute (can be multi-line)
            
        Returns:
            Tuple of (success: bool, result: dict or str)
            
        Example:
            code = '''
import unreal
actors = unreal.EditorLevelLibrary.get_all_level_actors()
print(f"Found {len(actors)} actors")
'''
            success, result = unreal.execute_python(code)
        """
        payload = {
            "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
            "functionName": "ExecutePythonCommand",
            "parameters": {"PythonCommand": python_code}
        }
        
        try:
            response = requests.put(self.base_url, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, response.text
                
        except requests.exceptions.ConnectionError:
            return False, f"Cannot connect to Unreal at {self.host}:{self.port}"
        except requests.exceptions.Timeout:
            return False, f"Request timeout after {self.timeout} seconds"
        except Exception as e:
            return False, str(e)
    
    def execute_python_file(self, file_path):
        """
        Execute a Python file inside Unreal Engine.
        
        Args:
            file_path: Path to Python file to execute
            
        Returns:
            Tuple of (success: bool, result: dict or str)
        """
        import os
        import py_compile
        import tempfile
        
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"
        
        # Syntax check with py_compile
        print(f"Checking syntax of {file_path}...")
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.pyc', delete=False) as tmp:
                tmp_path = tmp.name
            
            py_compile.compile(file_path, cfile=tmp_path, doraise=True)
            print("✓ Syntax check passed")
            
            # Clean up temp file
            try:
                os.remove(tmp_path)
            except:
                pass
                
        except py_compile.PyCompileError as e:
            return False, f"Syntax error in {file_path}:\n{str(e)}"
        
        # Read the file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                python_code = f.read()
        except Exception as e:
            return False, f"Failed to read file: {e}"
        
        # Execute the code
        return self.execute_python(python_code)
    
    def call_function(self, object_path, function_name, parameters=None):
        """
        Call an Unreal function directly via Remote Control API.
        
        Args:
            object_path: Full Unreal object path
            function_name: Name of function to call
            parameters: Dict of parameters (optional)
            
        Returns:
            Tuple of (success: bool, result: dict or str)
        """
        payload = {
            "objectPath": object_path,
            "functionName": function_name
        }
        
        if parameters:
            payload["parameters"] = parameters
        
        try:
            response = requests.put(self.base_url, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, response.text
        except Exception as e:
            return False, str(e)


def main():
    """Test connection and execute simple Python code in Unreal"""
    print("=" * 60)
    print("Unreal Engine Remote Python Execution - Test")
    print("=" * 60)
    print()
    
    # Create remote connection
    unreal = UnrealRemote()
    
    # Test connection
    print("[1] Testing connection...")
    if not unreal.is_connected():
        print("✗ Cannot connect to Unreal Engine!")
        print()
        print("Setup steps:")
        print("  1. Open your Unreal Engine project")
        print("  2. Enable Remote Control plugin:")
        print("     Edit → Plugins → search 'Remote Control' → Enable → Restart")
        print("  3. Open Output Log:")
        print("     Window → Developer Tools → Output Log")
        print("  4. Start WebControl server in console:")
        print("     WebControl.StartServer")
        print("  5. Enable PythonScriptLibrary in Remote Control:")
        print("     See ENABLE_PYTHON_EXECUTION.md in reference folder")
        print()
        return False
    
    print("✓ Connected to Unreal Engine!")
    print()
    
    # Execute test Python code
    print("[2] Executing test Python code in Unreal...")
    test_code = """
import unreal

# Get all actors in the level
actors = unreal.EditorLevelLibrary.get_all_level_actors()
print(f"Found {len(actors)} actors in level")

# Show first 5 actors
for i, actor in enumerate(actors[:5]):
    print(f"  {i+1}. {actor.get_name()} ({actor.get_class().get_name()})")

if len(actors) > 5:
    print(f"  ... and {len(actors) - 5} more")
"""
    
    success, result = unreal.execute_python(test_code)
    
    if success:
        print("✓ Python code executed successfully!")
        print()
        print("Result:", result)
        print()
        print("=" * 60)
        print("✓ Test passed!")
        print("=" * 60)
        print()
        print("Check Unreal Engine's Output Log for the detailed output.")
        return True
    else:
        print(f"✗ Failed to execute Python code: {result}")
        print()
        if "cannot be accessed remotely" in str(result):
            print("PythonScriptLibrary is not exposed to Remote Control.")
            print("See: reference/unreal/external_control/ENABLE_PYTHON_EXECUTION.md")
        return False


if __name__ == "__main__":
    main()
