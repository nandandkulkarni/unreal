"""
List EVERY single method on MovieSceneSectionExtensions
We might have missed a direct keyframe manipulation method
"""
import requests

BASE_URL = "http://localhost:30010/remote"

def describe_object(object_path):
    response = requests.put(
        f"{BASE_URL}/object/describe",
        json={"objectPath": object_path}
    )
    if response.status_code == 200:
        return response.json()
    return None

def main():
    print("=" * 80)
    print("ALL METHODS ON MovieSceneSectionExtensions")
    print("=" * 80)
    
    info = describe_object("/Script/SequencerScripting.Default__MovieSceneSectionExtensions")
    
    if not info:
        print("Failed to get info")
        return
    
    functions = info.get('Functions', [])
    print(f"\nTotal functions: {len(functions)}\n")
    
    for i, func in enumerate(functions, 1):
        print(f"{i}. {func['Name']}")
        params = func.get('Parameters', [])
        if params:
            for p in params:
                print(f"     - {p['Name']}: {p['Type']}")
        returns = func.get('ReturnType', 'void')
        if returns != 'void':
            print(f"     Returns: {returns}")
        print()

if __name__ == "__main__":
    main()
