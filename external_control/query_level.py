import requests
import json

def get_property(object_path, property_name):
    """Get a property value from an object"""
    url = 'http://localhost:30010/remote/object/property'
    
    payload = {
        'objectPath': object_path,
        'propertyName': property_name,
        'access': 'READ_ACCESS'
    }
    
    try:
        response = requests.put(url, json=payload)
        print(f"\nGetting property '{property_name}' from: {object_path}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
            return data
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def describe_object(object_path):
    """Describe an object"""
    url = 'http://localhost:30010/remote/object/describe'
    
    payload = {
        'objectPath': object_path
    }
    
    try:
        response = requests.put(url, json=payload)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

print("="*60)
print("QUERYING PERSISTENT LEVEL")
print("="*60)

# Describe the PersistentLevel
level_data = describe_object('/Game/Main.Main:PersistentLevel')
if level_data:
    print(f"\nPersistentLevel Object Info:")
    print(f"Name: {level_data.get('Name')}")
    print(f"Class: {level_data.get('Class')}")
    
    print(f"\nProperties ({len(level_data.get('Properties', []))}):")
    for prop in level_data.get('Properties', [])[:10]:  # Show first 10
        print(f"  - {prop.get('Name')} ({prop.get('Type')})")
    
    # Look for Actors property
    for prop in level_data.get('Properties', []):
        if 'actor' in prop.get('Name', '').lower():
            print(f"\n*** Found actor-related property: {prop.get('Name')} ***")

# Try to get Actors property
print("\n" + "="*60)
print("ATTEMPTING TO GET ACTORS FROM LEVEL")
print("="*60)

get_property('/Game/Main.Main:PersistentLevel', 'Actors')
