import requests

REMOTE_CONTROL_URL = "http://localhost:30010/remote/object/call"

diag_script = """
import unreal
subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
methods = dir(subsystem)
print(f"DIAG: new_level exists: {'new_level' in methods}")
print(f"DIAG: new_level_from_template exists: {'new_level_from_template' in methods}")

# Let's also check for common template paths
templates = [
    '/Engine/Maps/Templates/Template_Default',
    '/Engine/Maps/Templates/Basic',
    '/Engine/Maps/Templates/Template_Basic'
]
for t in templates:
    print(f"DIAG: Template {t} exists: {unreal.EditorAssetLibrary.does_asset_exist(t)}")
"""

payload = {
    "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
    "functionName": "ExecutePythonCommand",
    "parameters": {"PythonCommand": diag_script}
}

response = requests.put(REMOTE_CONTROL_URL, json=payload)
print(response.json())
