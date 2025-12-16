import requests
import json
import time

class UnrealController:
    def __init__(self, host='localhost', port=30010):
        self.base_url = f'http://{host}:{port}'
    
    def call_function(self, actor_path, function_name, parameters=None):
        """Call a function on an actor"""
        url = f'{self.base_url}/remote/object/call'
        
        payload = {
            'objectPath': actor_path,
            'functionName': function_name,
            'generateTransaction': True
        }
        
        if parameters:
            payload['parameters'] = parameters
        
        try:
            response = requests.put(url, json=payload)
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, response.text
        except Exception as e:
            return False, str(e)

if __name__ == "__main__":
    controller = UnrealController()
    cube_path = '/Game/Main.Main:PersistentLevel.StaticMeshActor_0'
    
    print("="*60)
    print("CHANGING CUBE TO RED MATERIAL")
    print("="*60)
    
    # Create a red material instance dynamically
    print("\nApproach: Setting vector parameter to red...")
    
    # Try to set the mesh to use a red color
    success, result = controller.call_function(
        cube_path,
        'SetVectorParameterValueOnMaterials',
        {
            'ParameterName': 'BaseColor',
            'ParameterValue': {
                'R': 1.0,
                'G': 0.0,
                'B': 0.0,
                'A': 1.0
            }
        }
    )
    
    if success:
        print("✓ Changed cube to red!")
    else:
        print(f"Method 1 failed: {result}")
        
        # Try another approach - set material scalar/color
        print("\nTrying alternate method...")
        success, result = controller.call_function(
            cube_path + '.StaticMeshComponent',
            'SetCustomPrimitiveDataVector4',
            {
                'DataIndex': 0,
                'Value': {
                    'X': 1.0,
                    'Y': 0.0,
                    'Z': 0.0,
                    'W': 1.0
                }
            }
        )
        
        if success:
            print("✓ Set custom data!")
        else:
            print(f"Method 2 failed: {result}")
    
    print("\n" + "="*60)
    print("NOTE: The cube should now appear red in the viewport")
    print("(May require clicking on it to refresh the view)")
    print("="*60)
