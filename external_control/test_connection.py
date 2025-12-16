import requests
import json

class UnrealRemoteControl:
    def __init__(self, host='localhost', port=30010):
        self.host = host
        self.port = port
        self.base_url = f'http://{host}:{port}'
        
    def test_connection(self):
        """Test if we can reach Unreal"""
        try:
            response = requests.get(f'{self.base_url}/remote/info')
            print(f"✓ Connected to Unreal Engine")
            print(f"Response: {response.json()}")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False

if __name__ == "__main__":
    controller = UnrealRemoteControl()
    controller.test_connection()
