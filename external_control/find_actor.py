import requests
import json

class ActorFinder:
    def __init__(self, host='localhost', port=30010):
        self.base_url = f'http://{host}:{port}'
    
    def test_path(self, path):
        """Test if an actor path exists"""
        url = f'{self.base_url}/remote/object/call'
        
        payload = {
            'objectPath': path,
            'functionName': 'K2_GetActorLocation',
            'generateTransaction': False
        }
        
        try:
            response = requests.put(url, json=payload)
            if response.status_code == 200:
                print(f"✓ FOUND: {path}")
                return True
            else:
                print(f"✗ Not found: {path}")
                return False
        except Exception as e:
            print(f"✗ Error testing {path}: {e}")
            return False

if __name__ == "__main__":
    finder = ActorFinder()
    
    print("Searching for your character actor...\n")
    
    # Common level names
    level_names = [
        'Main',
        'ThirdPersonMap', 
        'ThirdPersonExampleMap',
        'Untitled',
        'NewLevel',
        'CinematicPipeline'
    ]
    
    # Common actor names
    actor_names = [
        'BP_ThirdPersonCharacter',
        'BP_ThirdPersonCharacter_0',
        'BP_ThirdPersonCharacter_C_0',
        'ThirdPersonCharacter_0',
        'Character_0'
    ]
    
    found = False
    for level in level_names:
        for actor in actor_names:
            path = f'/Game/{level}.{level}:PersistentLevel.{actor}'
            if finder.test_path(path):
                print(f"\n{'='*60}")
                print(f"SUCCESS! Your actor path is:")
                print(f"{path}")
                print(f"{'='*60}\n")
                found = True
                break
        
        # Also try with ThirdPerson/Maps prefix
        for actor in actor_names:
            path = f'/Game/ThirdPerson/Maps/{level}.{level}:PersistentLevel.{actor}'
            if finder.test_path(path):
                print(f"\n{'='*60}")
                print(f"SUCCESS! Your actor path is:")
                print(f"{path}")
                print(f"{'='*60}\n")
                found = True
                break
                
        if found:
            break
    
    if not found:
        print("\n❌ Could not find character automatically.")
        print("\nPlease check in Unreal:")
        print("1. What is your level name? (check viewport tab)")
        print("2. What is your actor name? (check World Outliner)")
        print("3. Right-click actor in World Outliner → Copy Reference")
