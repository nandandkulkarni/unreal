import requests
import time

class UnrealController:
    def __init__(self, host='localhost', port=30010):
        self.base_url = f'http://{host}:{port}'

    def invalidate_viewports(self):
        """Call EditorLevelLibrary.EditorInvalidateViewports to force viewport redraw"""
        url = f'{self.base_url}/remote/object/call'
        
        # Try the static function on the EditorLevelLibrary CDO
        payload = {
            'objectPath': '/Script/UnrealEd.Default__EditorLevelLibrary',
            'functionName': 'EditorInvalidateViewports',
            'generateTransaction': False
        }
        
        try:
            resp = requests.put(url, json=payload, timeout=2)
            print(f"EditorInvalidateViewports response: {resp.status_code}")
            if resp.status_code != 200:
                print(f"Response: {resp.text}")
            return resp.status_code == 200
        except Exception as e:
            print(f"Exception: {e}")
            return False

    def redraw_all_viewports(self):
        """Try calling GEditor->RedrawAllViewports via EditorEngine"""
        url = f'{self.base_url}/remote/object/call'
        
        payload = {
            'objectPath': '/Engine/Transient.UnrealEdEngine_0',
            'functionName': 'RedrawAllViewports',
            'generateTransaction': False
        }
        
        try:
            resp = requests.put(url, json=payload, timeout=2)
            print(f"RedrawAllViewports response: {resp.status_code}")
            if resp.status_code != 200:
                print(f"Response: {resp.text}")
            return resp.status_code == 200
        except Exception as e:
            print(f"Exception: {e}")
            return False

if __name__ == '__main__':
    c = UnrealController()
    
    print("Testing EditorInvalidateViewports...")
    c.invalidate_viewports()
    
    time.sleep(1)
    
    print("\nTesting RedrawAllViewports...")
    c.redraw_all_viewports()
