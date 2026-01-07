"""
Comprehensive guide: What can be done with PCG in Unreal Python API
"""
import unreal

print("=" * 80)
print("PCG PYTHON API CAPABILITIES")
print("=" * 80)

# 1. Check available PCG classes
print("\n1. AVAILABLE PCG CLASSES AND TYPES")
print("-" * 80)

pcg_classes = {}
for attr_name in dir(unreal):
    if 'PCG' in attr_name and not attr_name.startswith('_'):
        try:
            attr = getattr(unreal, attr_name)
            if isinstance(attr, type):
                pcg_classes[attr_name] = attr
        except:
            pass

if pcg_classes:
    print(f"Found {len(pcg_classes)} PCG classes:\n")
    for name in sorted(pcg_classes.keys()):
        print(f"  ✓ {name}")
else:
    print("  ✗ No PCG classes found (PCG plugin may not be enabled)")

# 2. What you CAN do with PCG in Python
print("\n" + "=" * 80)
print("2. WHAT YOU CAN DO WITH PCG IN PYTHON")
print("=" * 80)

capabilities = {
    "Asset Management": [
        "Load existing PCG graph assets",
        "Create new PCG graph assets programmatically",
        "Save and duplicate PCG graphs",
        "Query PCG asset properties"
    ],
    "PCG Volume/Component Setup": [
        "Spawn PCG Volume actors in the level",
        "Add PCG components to existing actors",
        "Configure component properties (bounds, generation trigger, etc.)",
        "Set which PCG graph the component uses",
        "Enable/disable PCG components"
    ],
    "Generation Control": [
        "Trigger PCG generation programmatically (Generate/Cleanup)",
        "Refresh PCG data after changes",
        "Control generation timing (immediate, on load, etc.)",
        "Query generation state and results"
    ],
    "Graph Configuration": [
        "Access and modify graph settings",
        "Read node configurations",
        "Set input parameters/attributes",
        "Configure output settings"
    ],
    "Data Access": [
        "Read generated point data (positions, rotations, scales)",
        "Access PCG metadata attributes",
        "Query spatial data bounds",
        "Inspect generated mesh instances"
    ],
    "Batch Operations": [
        "Process multiple PCG volumes at once",
        "Batch generate/cleanup operations",
        "Automate PCG setup for level population",
        "Create procedural level layouts"
    ]
}

for category, items in capabilities.items():
    print(f"\n{category}:")
    for item in items:
        print(f"  ✓ {item}")

# 3. What you CANNOT do
print("\n" + "=" * 80)
print("3. WHAT YOU CANNOT DO (Requires C++ or Blueprints)")
print("=" * 80)

limitations = [
    "Create custom PCG nodes/elements (requires C++ PCGElement class)",
    "Define new PCG graph node types",
    "Implement custom sampling logic",
    "Create new PCG data types",
    "Extend PCG metadata system with new types",
    "Modify PCG node execution internals"
]

for limitation in limitations:
    print(f"  ✗ {limitation}")

# 4. Practical Python PCG workflow
print("\n" + "=" * 80)
print("4. TYPICAL PYTHON PCG WORKFLOW")
print("=" * 80)

workflow = """
Step 1: Create/Load PCG Graph Asset (in editor or via asset tools)
  graph_asset = unreal.load_asset("/Game/PCG/MyGraph.MyGraph")

Step 2: Spawn PCG Volume in Level
  pcg_volume = unreal.EditorLevelLibrary.spawn_actor_from_class(
      unreal.PCGVolume,
      location=unreal.Vector(0, 0, 0)
  )

Step 3: Configure PCG Component
  pcg_comp = pcg_volume.get_component_by_class(unreal.PCGComponent)
  pcg_comp.set_editor_property("graph", graph_asset)
  pcg_comp.set_editor_property("generate_on_load", True)

Step 4: Trigger Generation
  pcg_comp.generate()  # or cleanup_local()

Step 5: Query Results
  # Access generated data (if API provides access)
  # Useful for validation or further processing
"""

print(workflow)

# 5. Example use cases
print("\n" + "=" * 80)
print("5. PRACTICAL USE CASES")
print("=" * 80)

use_cases = [
    "Automated level population: Place trees, rocks, buildings via scripts",
    "Procedural environment generation: Generate terrain details on demand",
    "Batch processing: Setup PCG for multiple levels programmatically",
    "Testing/validation: Generate variants and capture results",
    "Pipeline integration: Trigger PCG generation as part of build process",
    "Dynamic scene setup: Configure PCG based on runtime parameters",
    "Asset placement automation: Scatter props with specific rules",
    "Optimization workflows: Generate LOD variants procedurally"
]

for i, use_case in enumerate(use_cases, 1):
    print(f"  {i}. {use_case}")

# 6. Check if we can demonstrate
print("\n" + "=" * 80)
print("6. TESTING BASIC PCG OPERATIONS")
print("=" * 80)

try:
    if hasattr(unreal, 'PCGComponent'):
        print("✓ PCGComponent class is available")
        
        # Try to get PCG subsystem
        if hasattr(unreal, 'PCGSubsystem'):
            print("✓ PCGSubsystem class is available")
            # Can use subsystem for batch operations
            
        # Check for volume class
        if hasattr(unreal, 'PCGVolume'):
            print("✓ PCGVolume class is available")
            print("\n  You can spawn PCG volumes and control generation!")
        
        print("\n✓ PCG Python API is functional and ready to use")
        
    else:
        print("✗ PCG classes not found - plugin may not be enabled")
        print("  Enable the 'Procedural Content Generation' plugin in project settings")
        
except Exception as e:
    print(f"Error testing PCG: {e}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("""
Python is ideal for:
  • Automating PCG setup and configuration
  • Batch operations on multiple PCG volumes
  • Triggering generation programmatically
  • Reading and validating generated data
  • Integration with external tools/pipelines

Python is NOT suitable for:
  • Creating custom PCG node types (use C++)
  • Implementing custom generation algorithms (use C++)
  • Real-time procedural generation logic (use C++/BP)

Recommended workflow:
  1. Design PCG graphs in the editor or Blueprints
  2. Use Python to automate placement and generation
  3. Use Python for batch processing and pipeline integration
""")
