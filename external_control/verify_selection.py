import requests
import time

class UnrealController:
    def __init__(self, host='localhost', port=30010):
        self.base_url = f'http://{host}:{port}'

    def set_selected(self, actor_path, selected=True):
        # Try EditorActorSubsystem
        # Note: We need to pass the object path to the subsystem instance. 
        # For subsystems, it's often the class default object or a specific instance path.
        # Let's try the Default object first.
        url = f'{self.base_url}/remote/object/call'
        payload = {
            'objectPath': '/Script/UnrealEd.Default__EditorActorSubsystem',
            'functionName': 'SetActorSelectionState',
            'parameters': {
                'Actor': actor_path,
                'bShouldBeSelected': selected
            },
            'generateTransaction': True
        }
        try:
            resp = requests.put(url, json=payload, timeout=2)
            print(f"Selection response: {resp.status_code}")
            if resp.status_code != 200:
                print(f"Error: {resp.text}")
            return resp.status_code == 200
        except Exception as e:
            print(f"Exception: {e}")
            return False

if __name__ == '__main__':
    c = UnrealController()
    # Using the actor path from previous scripts
    actor = '/Game/Main.Main:PersistentLevel.BP_ThirdPersonCharacter_C_1'
    
    print(f"Attempting to SELECT {actor}...")
    if c.set_selected(actor, True):
        print("Selection Successful!")
    else:
        print("Selection Failed.")
        
    time.sleep(2)
    
    print(f"Attempting to DESELECT {actor}...")
    if c.set_selected(actor, False):
        print("Deselection Successful!")
    else:
        print("Deselection Failed.")
