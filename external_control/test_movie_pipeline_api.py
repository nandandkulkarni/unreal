"""
Test script to check which MoviePipeline classes are available in Unreal Python API
"""

import requests
import json

REMOTE_CONTROL_URL = "http://localhost:30010/remote/object/call"

def execute_python_command(command):
    """Execute Python command in Unreal via Remote Control"""
    payload = {
        "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
        "functionName": "ExecutePythonCommand",
        "parameters": {"PythonCommand": command}
    }
    response = requests.put(REMOTE_CONTROL_URL, headers={'Content-Type': 'application/json'}, json=payload)
    result = response.json()
    return result.get('ReturnValue', result)

def test_movie_pipeline_classes():
    """Test if MoviePipeline classes can be accessed"""
    
    print("\n" + "="*80)
    print("Testing MoviePipeline API Availability")
    print("="*80 + "\n")
    
    # Test 1: Check if unreal module has MoviePipeline classes
    test_classes = [
        'MoviePipelineQueueSubsystem',
        'MoviePipelineExecutorJob',
        'MoviePipelineOutputSetting',
        'MoviePipelineDeferredPassBase',
        'MoviePipelineImageSequenceOutput_PNG',
        'MoviePipelinePIEExecutor',
        'MovieGraphPipeline',
        'MovieSceneCaptureSubsystem',
    ]
    
    for class_name in test_classes:
        try:
            result = execute_python_command(
                f"hasattr(unreal, '{class_name}')"
            )
            print(f"✓ {class_name}: {result}")
        except Exception as e:
            print(f"✗ {class_name}: ERROR - {e}")
    
    print("\n" + "-"*80)
    print("Testing get_editor_subsystem access")
    print("-"*80 + "\n")
    
    # Test 2: Try to get the subsystem
    try:
        result = execute_python_command("""
import unreal
try:
    subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
    'SUCCESS: Got subsystem: ' + str(type(subsystem))
except AttributeError as e:
    'ATTRIBUTE ERROR: ' + str(e)
except Exception as e:
    'ERROR: ' + str(e)
""")
        print(f"Subsystem access result:\n{result}")
    except Exception as e:
        print(f"Failed to execute subsystem test: {e}")
    
    print("\n" + "-"*80)
    print("Testing class instantiation")
    print("-"*80 + "\n")
    
    # Test 3: Try to create instances
    try:
        result = execute_python_command("""
import unreal
results = []

# Test MoviePipelineExecutorJob
try:
    job = unreal.MoviePipelineExecutorJob()
    results.append(f'MoviePipelineExecutorJob: {type(job)}')
except Exception as e:
    results.append(f'MoviePipelineExecutorJob ERROR: {e}')

# Test getting all unreal attributes with 'MoviePipeline' in name
movie_attrs = [attr for attr in dir(unreal) if 'MoviePipeline' in attr]
results.append(f'\\nFound {len(movie_attrs)} MoviePipeline attributes:')
results.append(', '.join(movie_attrs[:10]))  # First 10

'\\n'.join(results)
""")
        print(f"Instantiation test results:\n{result}")
    except Exception as e:
        print(f"Failed instantiation test: {e}")
    
    print("\n" + "-"*80)
    print("Searching for alternative rendering APIs")
    print("-"*80 + "\n")
    
    # Test 4: Search for any rendering-related classes
    try:
        result = execute_python_command("""
import unreal
render_attrs = [attr for attr in dir(unreal) if 'render' in attr.lower() or 'capture' in attr.lower()]
f'Found {len(render_attrs)} render/capture related attributes:\\n' + '\\n'.join(render_attrs[:20])
""")
        print(f"Rendering API search:\n{result}")
    except Exception as e:
        print(f"Failed API search: {e}")
    
    print("\n" + "="*80)
    print("Test Complete")
    print("="*80 + "\n")

if __name__ == "__main__":
    test_movie_pipeline_classes()
