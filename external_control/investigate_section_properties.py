"""
Investigate section properties - maybe we can SET keyframe data directly via properties
"""
import requests

BASE_URL = "http://localhost:30010/remote"

def describe_object(object_path):
    """Get detailed info about object including properties"""
    response = requests.put(
        f"{BASE_URL}/object/describe",
        json={"objectPath": object_path}
    )
    
    if response.status_code == 200:
        return response.json()
    return None

def get_object_property(object_path, property_name):
    """Get a property value from an object"""
    response = requests.put(
        f"{BASE_URL}/object/property",
        json={
            "objectPath": object_path,
            "propertyName": property_name,
            "access": "READ_ACCESS"
        }
    )
    
    if response.status_code == 200:
        return True, response.json()
    return False, response.text

def set_object_property(object_path, property_name, value):
    """Set a property value on an object"""
    response = requests.put(
        f"{BASE_URL}/object/property",
        json={
            "objectPath": object_path,
            "propertyName": property_name,
            "propertyValue": value,
            "access": "WRITE_ACCESS"
        }
    )
    
    if response.status_code == 200:
        return True, response.json()
    return False, response.text

def main():
    print("=" * 80)
    print("INVESTIGATE SECTION PROPERTIES")
    print("=" * 80)
    
    # Use the section from previous run
    section_path = "/Game/Sequences/TestSequence.TestSequence:MovieScene_0.MovieScene3DTransformTrack_11.MovieScene3DTransformSection_0"
    
    print(f"\n[1] Describing section object...")
    print(f"    Path: {section_path}")
    
    info = describe_object(section_path)
    
    if not info:
        print("    [X] Failed to describe section")
        return
    
    print(f"\n[2] Available Properties:")
    properties = info.get('Properties', [])
    for prop in properties:
        print(f"    - {prop['Name']} ({prop['Type']})")
        if 'Description' in prop:
            print(f"      {prop['Description']}")
    
    print(f"\n[3] Available Functions:")
    functions = info.get('Functions', [])
    for func in functions[:20]:  # First 20
        print(f"    - {func['Name']}")
        params = func.get('Parameters', [])
        if params:
            param_str = ", ".join([f"{p['Name']}: {p['Type']}" for p in params])
            print(f"      ({param_str})")

if __name__ == "__main__":
    main()
