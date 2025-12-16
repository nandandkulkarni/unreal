import requests
import json

class UnrealController:
    def __init__(self, host='localhost', port=30010):
        self.base_url = f'http://{host}:{port}'
    
    def set_property(self, actor_path, property_name, value):
        """Set a property on an actor"""
        url = f'{self.base_url}/remote/object/property'
        
        payload = {
            'objectPath': actor_path,
            'propertyName': property_name,
            'propertyValue': value,
            'generateTransaction': True
        }
        
        try:
            response = requests.put(url, json=payload)
            if response.status_code == 200:
                print(f"✓ Set {property_name} successfully")
                return True
            else:
                print(f"✗ Failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

if __name__ == "__main__":
    controller = UnrealController()
    
    # Try different possible cube paths
    cube_paths = [
        '/Game/Main.Main:PersistentLevel.Cube',
        '/Game/Main.Main:PersistentLevel.StaticMeshActor',
        '/Game/Main.Main:PersistentLevel.StaticMeshActor_0',
        '/Game/Main.Main:PersistentLevel.Cube_0'
    ]
    
    print("="*60)
    print("CHANGING CUBE COLOR TO RED")
    print("="*60)
    
    # Try to set the color to red (R=1, G=0, B=0)
    for cube_path in cube_paths:
        print(f"\nTrying path: {cube_path}")
        
        # Try setting a color override
        result = controller.set_property(
            cube_path,
            'CustomPrimitiveData',
            {'R': 1.0, 'G': 0.0, 'B': 0.0, 'A': 1.0}
        )
        
        if result:
            print(f"✓ Successfully changed color using path: {cube_path}")
            break
    else:
        print("\n✗ Could not find cube with any of the tested paths")
        print("Please check the cube name in World Outliner")
    
    print("\n" + "="*60)
