"""
Check if Unreal Engine supports PCG (Procedural Content Generation) via Python API
"""
import unreal

print("Checking for PCG (Procedural Content Generation) support in Unreal Python API...")
print("=" * 70)

# Check for PCG-related modules and classes
pcg_classes = []
pcg_modules = []

try:
    # Try to access common PCG classes
    potential_classes = [
        "PCGComponent",
        "PCGGraph",
        "PCGSettings",
        "PCGNode",
        "PCGElement",
        "PCGData",
        "PCGPointData",
        "PCGSpatialData",
        "PCGVolumeData",
        "PCGMetadata",
        "PCGSubsystem",
        "PCGGraphInstance",
        "PCGEditorSettings",
    ]
    
    for class_name in potential_classes:
        if hasattr(unreal, class_name):
            cls = getattr(unreal, class_name)
            pcg_classes.append(class_name)
            print(f"✓ Found: unreal.{class_name}")
            
    if not pcg_classes:
        print("✗ No direct PCG classes found in unreal module")
        
except Exception as e:
    print(f"Error checking classes: {e}")

print("\n" + "=" * 70)
print("Searching for PCG-related classes by introspection...")
print("=" * 70)

# Search through all unreal module attributes
all_attrs = dir(unreal)
pcg_related = [attr for attr in all_attrs if 'pcg' in attr.lower() or 'procedural' in attr.lower()]

if pcg_related:
    print(f"\nFound {len(pcg_related)} PCG-related attributes:")
    for attr in sorted(pcg_related)[:20]:  # Show first 20
        print(f"  - {attr}")
    if len(pcg_related) > 20:
        print(f"  ... and {len(pcg_related) - 20} more")
else:
    print("✗ No PCG-related attributes found")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

if pcg_classes or pcg_related:
    print("✓ PCG Python API appears to be available in this Unreal Engine version")
    print(f"  Found {len(pcg_classes)} direct PCG classes")
    print(f"  Found {len(pcg_related)} PCG-related attributes")
    print("\nYou can create and manipulate PCG graphs using Python!")
else:
    print("✗ PCG Python API does not appear to be available")
    print("  This could mean:")
    print("  1. PCG plugin is not enabled")
    print("  2. This Unreal Engine version doesn't support PCG")
    print("  3. PCG Python bindings are not exposed")
    
print("\nNote: PCG (Procedural Content Generation) was introduced in UE 5.0+")
print("and Python API support may vary by version.")
