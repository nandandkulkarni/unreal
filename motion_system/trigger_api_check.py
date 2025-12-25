import requests
import json
import time

REMOTE_CONTROL_URL = "http://localhost:30010/remote/object/call"
LOG_FILE = r"C:\\UnrealProjects\\Coding\\unreal\\direct\\api_check.log"

# Note: We double brace {{}} for f-string escaping
INSPECTION_SCRIPT = f"""
import unreal
import logging

LOG_FILE = r'{LOG_FILE}'
logger = logging.getLogger('api_inspector')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(LOG_FILE, mode='w')
formatter = logging.Formatter('%(message)s')
file_handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(file_handler)

logger.info("--- UNREAL PYTHON API INSPECTION V2 ---")

target = "ConstraintsScriptingLibrary"
logger.info("-" * 40)
if hasattr(unreal, target):
    logger.info(f"[SUCCESS] {{target}} EXISTS.")
    cls = getattr(unreal, target)
    logger.info(f"Members of {{target}}:")
    for member in dir(cls):
        if not member.startswith("_"):
            logger.info(f"    .{{member}}")
else:
    logger.info(f"[FAILURE] {{target}} does NOT exist.")

logger.info("--- END INSPECTION ---")
"""

def run_check():
    payload = {
        "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
        "functionName": "ExecutePythonCommand",
        "parameters": {"PythonCommand": INSPECTION_SCRIPT}
    }
    
    print(f"--- Triggering API Check ---")
    try:
        response = requests.put(REMOTE_CONTROL_URL, json=payload, timeout=10)
        print(f"Response: {response.status_code} - {response.text}")
        print("Check completed. Inspect logs.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_check()
