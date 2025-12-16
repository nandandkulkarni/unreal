import requests
import json

class UnrealExplorer:
    def __init__(self, host='localhost', port=30010):
        self.base_url = f'http://{host}:{port}'
    
    def search_assets(self, query="", asset_class=""):
        """Search for assets in the project"""
        url = f'{self.base_url}/remote/search/assets'
        
        payload = {
            'Query': query,
            'Filter': {
                'ClassNames': [asset_class] if asset_class else [],
                'PackagePaths': [],
                'RecursivePaths': True
            },
            'Limit': 100
        }
        
        try:
            response = requests.put(url, json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Search failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def get_level_actors(self):
        """Try to get actors from the level using object path patterns"""
        print("Attempting to enumerate level actors...\n")
        
        # Try to get world info
        world_paths = [
            '/Game/Main',
            '/Game/ThirdPersonMap',
            '/Game/ThirdPerson/Maps/ThirdPersonMap'
        ]
        
        for world_path in world_paths:
            print(f"Trying world path: {world_path}")
            # Try to describe the world
            url = f'{self.base_url}/remote/object/describe'
            payload = {'objectPath': world_path}
            
            try:
                response = requests.put(url, json=payload)
                if response.status_code == 200:
                    print(f"✓ Found world: {world_path}")
                    print(json.dumps(response.json(), indent=2))
                    print("\n" + "="*60 + "\n")
            except:
                pass

if __name__ == "__main__":
    explorer = UnrealExplorer()
    
    print("="*60)
    print("UNREAL ENGINE PROJECT EXPLORER")
    print("="*60)
    print()
    
    # Search for Blueprint actors
    print("Searching for Blueprint classes in project...\n")
    results = explorer.search_assets(query="BP_", asset_class="Blueprint")
    
    if results and 'Assets' in results:
        print(f"Found {len(results['Assets'])} Blueprint assets:\n")
        for asset in results['Assets']:
            print(f"  - {asset.get('Name', 'Unknown')}")
            print(f"    Path: {asset.get('Path', 'Unknown')}")
            print(f"    Class: {asset.get('Class', 'Unknown')}")
            print()
    
    # Search for Character classes
    print("\n" + "="*60)
    print("Searching for Character-related assets...\n")
    results = explorer.search_assets(query="Character", asset_class="")
    
    if results and 'Assets' in results:
        print(f"Found {len(results['Assets'])} Character-related assets:\n")
        for asset in results['Assets']:
            print(f"  - {asset.get('Name', 'Unknown')}")
            print(f"    Path: {asset.get('Path', 'Unknown')}")
            print()
    
    # Try to get level info
    print("\n" + "="*60)
    explorer.get_level_actors()
    
    print("\n" + "="*60)
    print("\nHINT: Look for your character in the results above.")
    print("The actor path format is: /Game/LevelName.LevelName:PersistentLevel.ActorName")
    print("="*60)
