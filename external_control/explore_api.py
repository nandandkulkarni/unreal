import requests
import json
import time

class UnrealController:
    def __init__(self, host='localhost', port=30010):
        self.base_url = f'http://{host}:{port}'

    def describe_object(self, object_path):
        """Get details about an object"""
        url = f'{self.base_url}/remote/object/describe'
        payload = {'objectPath': object_path}
        
        try:
            resp = requests.put(url, json=payload, timeout=2)
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f"Describe failed: {resp.status_code} - {resp.text[:200]}")
                return None
        except Exception as e:
            print(f"Exception: {e}")
            return None

    def search_objects(self, query):
        """Search for objects matching query"""
        url = f'{self.base_url}/remote/search/assets'
        payload = {'Query': query, 'Limit': 20}
        
        try:
            resp = requests.put(url, json=payload, timeout=2)
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f"Search failed: {resp.status_code} - {resp.text[:200]}")
                return None
        except Exception as e:
            print(f"Exception: {e}")
            return None

    def list_presets(self):
        """List all registered remote control presets"""
        url = f'{self.base_url}/remote/presets'
        
        try:
            resp = requests.get(url, timeout=2)
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f"List presets failed: {resp.status_code} - {resp.text[:200]}")
                return None
        except Exception as e:
            print(f"Exception: {e}")
            return None

    def get_info(self):
        """Get remote control info"""
        url = f'{self.base_url}/remote/info'
        
        try:
            resp = requests.get(url, timeout=2)
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f"Info failed: {resp.status_code} - {resp.text[:200]}")
                return None
        except Exception as e:
            print(f"Exception: {e}")
            return None

    def set_actor_location(self, actor_path, x, y, z):
        """Move an actor to a specific location"""
        url = f'{self.base_url}/remote/object/call'
        
        payload = {
            'objectPath': actor_path,
            'functionName': 'K2_SetActorLocation',
            'parameters': {
                'NewLocation': {
                    'X': x,
                    'Y': y,
                    'Z': z
                },
                'bSweep': False,
                'bTeleport': True
            },
            'generateTransaction': True
        }
        
        try:
            response = requests.put(url, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

    def mark_render_state_dirty(self, actor_path):
        """Try to mark the actor's render state as dirty"""
        url = f'{self.base_url}/remote/object/call'
        
        payload = {
            'objectPath': actor_path,
            'functionName': 'MarkComponentsRenderStateDirty',
            'generateTransaction': True
        }
        
        try:
            resp = requests.put(url, json=payload, timeout=2)
            print(f"MarkComponentsRenderStateDirty: {resp.status_code}")
            if resp.status_code != 200:
                print(f"  Response: {resp.text[:200]}")
            return resp.status_code == 200
        except Exception as e:
            print(f"Exception: {e}")
            return False

if __name__ == '__main__':
    c = UnrealController()
    actor = '/Game/Main.Main:PersistentLevel.BP_ThirdPersonCharacter_C_1'
    
    print("="*60)
    print("EXPLORING REMOTE CONTROL API")
    print("="*60)
    
    print("\n1. Getting Remote Control Info...")
    info = c.get_info()
    if info:
        print(json.dumps(info, indent=2)[:500])
    
    print("\n2. Listing Presets...")
    presets = c.list_presets()
    if presets:
        print(json.dumps(presets, indent=2)[:500])
    
    print("\n3. Describing actor...")
    desc = c.describe_object(actor)
    if desc:
        print(json.dumps(desc, indent=2)[:1000])
    
    print("\n4. Moving actor and marking render state dirty...")
    c.set_actor_location(actor, 500, 500, 100)
    time.sleep(0.5)
    c.mark_render_state_dirty(actor)
