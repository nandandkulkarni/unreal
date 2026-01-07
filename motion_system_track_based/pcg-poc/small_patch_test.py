"""
Create Small 10m x 10m PCG Grass Test Patch
Based on final_descriptor_config.py but creates a small test volume
"""
import unreal
import sys

LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\small_patch_test.log"

class FileLogger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, 'w', encoding='utf-8')
        
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = FileLogger(LOG_FILE_PATH)

print("=" * 80)
print("CREATE 10m x 10m PCG GRASS TEST PATCH")
print("=" * 80)

GRASS_MESH_PATH = "/Game/Fab/Megascans/Plants/Ribbon_Grass_tbdpec3r/High/tbdpec3r_tier_1/StaticMeshes/SM_tbdpec3r_VarA"
TEST_SIZE = 10.0  # 10 meters
TEST_DENSITY = 25.0  # 25 points/m²

try:
    # ==============================================================================
    # 1. LOAD PCG GRAPH
    # ==============================================================================
    print("\n1. Loading PCG Graph...")
    
    pcg_assets = unreal.EditorAssetLibrary.list_assets("/Game/PCG", recursive=False)
    pcg_graphs = [a for a in pcg_assets if "PCG_StadiumGrass" in a]
    latest_graph_path = sorted(pcg_graphs)[-1]

    print(f"   Loading: {latest_graph_path}")
    pcg_graph = unreal.load_asset(latest_graph_path)
    
    if not pcg_graph:
        print("   ✗ Failed to load graph")
        sys.exit(1)
    
    print(f"   ✓ Loaded: {pcg_graph.get_name()}")

    # ==============================================================================
    # 2. CLEANUP OLD TEST ACTORS
    # ==============================================================================
    print("\n2. Cleaning up old test actors...")
    
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    deleted = 0
    
    cleanup_labels = ["PCG_Test_", "Test_Grass_Patch"]
    for actor in all_actors:
        label = actor.get_actor_label()
        if any(key in label for key in cleanup_labels):
            unreal.EditorLevelLibrary.destroy_actor(actor)
            deleted += 1
    
    print(f"   ✓ Removed {deleted} old test actors")

    # ==============================================================================
    # 3. UPDATE SURFACE SAMPLER DENSITY
    # ==============================================================================
    print(f"\n3. Setting Surface Sampler density to {TEST_DENSITY} points/m²...")
    
    nodes = pcg_graph.nodes
    surface_sampler = None
    
    for node in nodes:
        settings = node.get_settings()
        if "SurfaceSampler" in type(settings).__name__:
            surface_sampler = settings
            break
    
    if surface_sampler:
        current_density = surface_sampler.get_editor_property("points_per_squared_meter")
        print(f"   Current density: {current_density} points/m²")
        
        surface_sampler.set_editor_property("points_per_squared_meter", TEST_DENSITY)
        print(f"   ✓ Set to {TEST_DENSITY} points/m²")
        
        # Set to unbounded mode so it doesn't need to find specific actors
        surface_sampler.set_editor_property("unbounded", True)
        print(f"   ✓ Set to unbounded mode (generates points everywhere in volume)")
        
        # Save graph
        unreal.EditorAssetLibrary.save_loaded_asset(pcg_graph)
        print(f"   ✓ Saved graph")
    else:
        print(f"   ✗ No Surface Sampler found")

    # ==============================================================================
    # 4. CREATE TEST GROUND PLANE
    # ==============================================================================
    print(f"\n4. Creating test ground plane (20m x 20m)...")
    
    # Create a simple cube as ground
    cube_mesh = unreal.load_object(None, "/Engine/BasicShapes/Cube.Cube")
    
    ground_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,
        unreal.Vector(0, 0, -5)  # Slightly below origin
    )
    
    ground_actor.set_actor_label("PCG_Test_Ground")
    ground_actor.set_folder_path(unreal.Name("OvalTrack/PCG"))
    ground_actor.tags = ["PCG_Ground"]  # TAG THE ACTOR for PCG to find
    ground_actor.static_mesh_component.set_static_mesh(cube_mesh)
    
    # Scale to 20m x 20m x 0.1m (flat ground plane)
    ground_actor.set_actor_scale3d(unreal.Vector(20.0, 20.0, 0.1))
    
    # CRITICAL: Tag the COMPONENT too, because GetActorData needs to select the component!
    # ground_actor.tags is for Actor Selector
    # ground_actor.static_mesh_component.component_tags is for Component Selector
    ground_actor.static_mesh_component.component_tags = ["PCG_Ground_Comp"]
    
    print(f"   ✓ Created ground plane at (0, 0, -5)")
    print(f"   ✓ Size: 20m x 20m (covers test area)")
    print(f"   ✓ Added Actor tag: 'PCG_Ground'")
    print(f"   ✓ Added Component tag: 'PCG_Ground_Comp'")

    # ==============================================================================
    # 5. REBUILD GRAPH FOR TEST (ENSURE CLEAN STATE)
    # ==============================================================================
    print(f"\n5. Rebuilding PCG Graph...")
    
    # Remove existing nodes to start fresh
    start_node_count = len(pcg_graph.nodes)
    if start_node_count > 0:
        print(f"   Clearing {start_node_count} existing nodes...")
        # Note: remove_node might require loop
        for node in list(pcg_graph.nodes): # Iterate over a copy as we modify the list
            pcg_graph.remove_node(node)
            
    # 1. Add Mesh Spawner
    print(f"   Adding Static Mesh Spawner...")
    spawner_settings_cls = unreal.load_class(None, "/Script/PCG.PCGStaticMeshSpawnerSettings")
    spawner_node = pcg_graph.add_node_of_type(spawner_settings_cls)
    if isinstance(spawner_node, tuple): spawner_node = spawner_node[0]
    
    # Configure Spawner (Mesh)
    spawner_settings = spawner_node.get_settings()
    # (We could configure mesh here, but for now assuming we set it via property later or it retains defaults if it reused settings object - wait, new node = new settings)
    # We need to set the mesh on the new spawner!
    # I will paste the mesh configuration logic here.
    
    print(f"   Re-configuring Mesh...")
    # Hardcoded path to be absolutely sure
    grass_path = "/Game/Fab/Megascans/Plants/Ribbon_Grass_tbdpec3r/High/tbdpec3r_tier_1/StaticMeshes/SM_tbdpec3r_VarA"
    grass_mesh = unreal.load_asset(grass_path)
    
    if grass_mesh:
        try:
            print(f"   ✓ Loaded mesh: {grass_mesh.get_name()}")
            # Create descriptor
            descriptor = unreal.PCGSoftISMComponentDescriptor()
            
            # Robustly set mesh
            mesh_prop_set = False
            for prop_name in ["static_mesh", "mesh", "soft_static_mesh", "template"]:
                try:
                    descriptor.set_editor_property(prop_name, grass_mesh)
                    print(f"   ✓ Set '{prop_name}' on descriptor")
                    mesh_prop_set = True
                    break
                except:
                    continue
            
            if not mesh_prop_set:
                 print(f"   ⚠ Could not set mesh on descriptor (tried static_mesh, mesh, etc)")

            # Create entry
            entry = unreal.PCGMeshSelectorWeightedEntry()
            entry.set_editor_property("descriptor", descriptor)
            entry.set_editor_property("weight", 1)
            
            # Assign to spawner
            mesh_selector = spawner_settings.mesh_selector_instance
            
            # Clear existing entries and add the new one
            # Use set_editor_property for array properties
            mesh_selector.set_editor_property("mesh_entries", [entry])
            
            spawner_settings.debug = True # ENABLE DEBUG
            
            print(f"   ✓ Configured Spawner with mesh entry (weight=1), DEBUG=True")
        except Exception as e:
            print(f"   ⚠ Mesh re-config warning: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"   ✗ Grass mesh not found at {grass_path}")


    # 2. Add Surface Sampler
    print(f"   Adding Surface Sampler...")
    sampler_settings_cls = unreal.load_class(None, "/Script/PCG.PCGSurfaceSamplerSettings")
    sampler_node = pcg_graph.add_node_of_type(sampler_settings_cls)
    if isinstance(sampler_node, tuple): sampler_node = sampler_node[0]
    
    # Configure Sampler
    sampler_settings = sampler_node.get_settings()
    sampler_settings.points_per_squared_meter = TEST_DENSITY
    sampler_settings.unbounded = True
    sampler_settings.debug = True  # ENABLE DEBUG
    print(f"   ✓ Configured Sampler: {TEST_DENSITY} pts/m², Unbounded, DEBUG=True")

    # 3. Add Input Node (GetActorData)
    print(f"   Adding Input Node...")
    get_data_cls_name = "PCGGetActorDataSettings" # Correct class name
    get_data_cls = getattr(unreal, get_data_cls_name, None)
    if not get_data_cls:
        # Fallback search
        candidates = [c for c in dir(unreal) if c.startswith("PCG") and "Settings" in c and "Actor" in c and "Data" in c]
        if candidates: get_data_cls = getattr(unreal, candidates[0])
        
    input_node = pcg_graph.add_node_of_type(get_data_cls)
    if isinstance(input_node, tuple): input_node = input_node[0]
    
    # Configure Input
    input_settings = input_node.get_settings()
    if hasattr(input_settings, 'actor_selector'):
        # Structs are value types, must modify and set back!
        selector = input_settings.actor_selector
        
        # 1. Select by TAG
        selector.set_editor_property("actor_selection", unreal.PCGActorSelection.BY_TAG)
        selector.set_editor_property("actor_selection_tag", "PCG_Ground")
        
        # 2. Filter: Must be All World Actors (2)
        print("     Setting actor_filter to ALL_WORLD_ACTORS (2)...")
        try:
            # Try Direct Attribute Assignment first (for structs this is often better)
            selector.actor_filter = unreal.PCGActorFilter.ALL_WORLD_ACTORS
            print("     ✓ Set via attribute assignment (Enum)")
        except Exception as e1:
            print(f"     Note: Attribute assignment failed: {e1}")
            try:
                selector.set_editor_property("actor_filter", unreal.PCGActorFilter.ALL_WORLD_ACTORS)
                print("     ✓ Set via set_editor_property (Enum)")
            except Exception as e2:
                print(f"     Note: set_editor_property (Enum) failed: {e2}")
                try:
                    # Force Integer 2
                    selector.set_editor_property("actor_filter", 2)
                    print("     ✓ Set via set_editor_property (Int 2)")
                except Exception as e3:
                    print(f"     ✗ ALL ATTEMPTS FAILED to set actor_filter: {e3}")

        # KEY STEP: Set the struct back (Actor Selector)!
        input_settings.set_editor_property("actor_selector", selector)
        
        # 3. COMPONENT SELECTOR
        # We must also ensure it picks up the StaticMeshComponent
        comp_selector = input_settings.component_selector
        # Attempt to set to By Tag if possible, or just ignore (default might be ByTag with empty=All?)
        # Let's be explicit: Select "PCG_Ground_Comp"
        try:
             comp_selector.set_editor_property("component_selection", unreal.PCGComponentSelection.BY_TAG)
             comp_selector.set_editor_property("component_selection_tag", "PCG_Ground_Comp")
             input_settings.set_editor_property("component_selector", comp_selector)
             print(f"   ✓ Configured Component Selector: Tag 'PCG_Ground_Comp'")
        except:
             print("   Note: Could not set component selection tag (might be defaulting to All)")

        # Disable bounds check to ensure it finds the actor anywhere in the world (if filtered to AllWorldActors)
        input_settings.set_editor_property("track_actors_only_within_bounds", False)
        
        # Enable Debug to visualize if it found something
        input_settings.set_editor_property("debug", True)
        
        print(f"   ✓ Configured Input: ActorTag='PCG_Ground', Filter=AllWorldActors")
        print(f"   ✓ Disabled 'Track Actors Only Within Bounds'")
        print(f"   ✓ Disabled 'Track Actors Only Within Bounds'")
        print(f"   ✓ Enabled 'Debug' on Input Node (Look for wireframes!)")
    else:
        print(f"   ✗ Could not configure input node (no actor_selector property)")

    # 4. Connect Nodes
    print(f"   Connecting Nodes...")
    def print_pins(node, name):
        try:
            # Pins are properties, not methods
            inputs = [p.properties.label for p in node.input_pins]
            outputs = [p.properties.label for p in node.output_pins]
            print(f"     {name} Pins -> In: {inputs}, Out: {outputs}")
            return inputs, outputs
        except Exception as e:
            print(f"     {name} Pins inspection failed: {e}")
            return [], []

    in_pins, out_pins = print_pins(input_node, "InputNode")
    samp_in, samp_out = print_pins(sampler_node, "SamplerNode")
    spawn_in, spawn_out = print_pins(spawner_node, "SpawnerNode")
    
    # Determine correct pin names dynamically
    src_pin = "Out"
    if out_pins: src_pin = str(out_pins[0])
    
    dst_pin = "Surface"
    if samp_in: dst_pin = str(samp_in[0])
    
    print(f"   Connecting Input({src_pin}) -> Sampler({dst_pin})")
    pcg_graph.add_edge(input_node, src_pin, sampler_node, dst_pin)
    
    # Sampler -> Spawner
    samp_src = "Out"
    if samp_out: samp_src = str(samp_out[0])
    
    spawn_dst = "In"
    if spawn_in: spawn_dst = str(spawn_in[0])
    
    print(f"   Connecting Sampler({samp_src}) -> Spawner({spawn_dst})")
    pcg_graph.add_edge(sampler_node, samp_src, spawner_node, spawn_dst)

    # Save graph after rebuilding
    unreal.EditorAssetLibrary.save_loaded_asset(pcg_graph)
    print(f"   ✓ Saved graph after rebuild")

    # ==============================================================================
    # 6. CREATE SMALL TEST PCG VOLUME
    # ==============================================================================
    print(f"\n6. Creating {TEST_SIZE}m x {TEST_SIZE}m test volume...")
    
    pcg_vol_cls = unreal.load_class(None, "/Script/PCG.PCGVolume")
    if not pcg_vol_cls:
        print("   ✗ Could not load PCGVolume class")
        sys.exit(1)
    
    # Spawn at center of stadium ground (0, 0, 0)
    test_volume = unreal.EditorLevelLibrary.spawn_actor_from_class(
        pcg_vol_cls,
        unreal.Vector(0, 0, 0)
    )
    
    if not test_volume:
        print("   ✗ Failed to spawn volume")
        sys.exit(1)
    
    test_volume.set_actor_label("PCG_Test_Patch_10x10")
    test_volume.set_folder_path(unreal.Name("OvalTrack/PCG"))
    
    # Scale to 10m x 10m x 5m (height doesn't matter much)
    test_volume.set_actor_scale3d(unreal.Vector(TEST_SIZE, TEST_SIZE, 5.0))
    
    print(f"   ✓ Created volume at (0, 0, 0)")
    print(f"   ✓ Size: {TEST_SIZE}m x {TEST_SIZE}m x 5m")

    # ==============================================================================
    # 7. ASSIGN GRAPH AND GENERATE
    # ==============================================================================
    print(f"\n7. Assigning graph and generating...")
    
    test_comp = None
    for comp in test_volume.get_components_by_class(unreal.PCGComponent):
        test_comp = comp
        break
    
    if test_comp:
        test_comp.set_graph(pcg_graph)
        print(f"   ✓ Assigned graph")
        
        # Set generation trigger to GENERATE_ON_LOAD (Auto-generate!)
        print(f"\n   Setting generation trigger...")
        try:
            test_comp.set_editor_property("generation_trigger", unreal.PCGComponentGenerationTrigger.GENERATE_ON_LOAD)
            trigger = test_comp.get_editor_property("generation_trigger")
            print(f"   ✓ Set to: {trigger} (Auto-generate)")
        except Exception as e:
            print(f"   ✗ Could not set trigger: {e}")
        except Exception as e:
            print(f"   ✗ Could not set trigger: {e}")
        
        # Cleanup any previous generation
        print(f"\n   Cleaning up previous generation...")
        test_comp.cleanup_local(True)
        print(f"   ✓ Cleaned up")
        
        # Generate using both methods
        print(f"\n   Generating PCG...")
        test_comp.generate_local(True)
        print(f"   ✓ generate_local(True) called")
        
        # Also try the non-local generate method with force parameter
        try:
            test_comp.generate(force=True)
            print(f"   ✓ generate(force=True) called")
        except Exception as e:
            print(f"   Note: generate(force=True) - {e}")
        
        # Calculate expected instances
        area = TEST_SIZE * TEST_SIZE
        expected = int(area * TEST_DENSITY)
        print(f"\n   Expected grass instances: ~{expected:,}")
        print(f"   (Area: {area}m² × Density: {TEST_DENSITY} points/m²)")
        
        # Check generation status immediately
        print(f"\n   Checking PCG execution status...")
        is_generated = test_comp.get_editor_property("generated")
        print(f"     Generated (immediate): {is_generated}")
        
        # Check if there's a way to force synchronous generation
        print(f"\n   Checking generation trigger setting...")
        trigger = test_comp.get_editor_property("generation_trigger")
        print(f"     Current trigger: {trigger}")
        
        if not is_generated:
            print(f"     ⚠ Generation not complete - may still be processing")
            print(f"     Check viewport in a few seconds")
        
        # Try to get more info about the PCG state
        try:
            # Check if there are any generated resources
            print(f"\n   Checking for generated output...")
            print(f"     Component class: {test_comp.get_class().get_name()}")
            
            # List all properties to see what we can inspect
            comp_props = [p for p in dir(test_comp) if not p.startswith('_') and 'get' in p.lower()]
            print(f"     Available get methods: {len(comp_props)}")
            
        except Exception as e:
            print(f"     Error inspecting component: {e}")
    else:
        print("   ✗ No PCG Component found")

    # ==============================================================================
    # 8. DEBUGGING - CHECK WHY NO GRASS
    # ==============================================================================
    print(f"\n8. Debugging - checking configuration...")
    
    # Check if stadium ground actors exist
    print(f"\n   Checking for stadium ground actors...")
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    stadium_actors = []
    for actor in all_actors:
        if "Stadium_Ground" in actor.get_actor_label():
            stadium_actors.append(actor)
            loc = actor.get_actor_location()
            print(f"     ✓ {actor.get_actor_label()} at ({loc.x}, {loc.y}, {loc.z})")
    
    if not stadium_actors:
        print(f"     ✗ NO STADIUM GROUND ACTORS FOUND!")
        print(f"     This is the problem - PCG needs ground to sample!")
    
    # Check volume position vs ground
    print(f"\n   Volume position check:")
    vol_loc = test_volume.get_actor_location()
    vol_bounds = test_volume.get_actor_bounds(False)
    print(f"     Volume location: ({vol_loc.x}, {vol_loc.y}, {vol_loc.z})")
    print(f"     Volume bounds: Origin {vol_bounds[0]}, Extent {vol_bounds[1]}")
    
    # Check mesh spawner configuration
    print(f"\n   Checking mesh spawner configuration...")
    for node in nodes:
        settings = node.get_settings()
        if "StaticMeshSpawner" in type(settings).__name__:
            mesh_selector = settings.mesh_selector_instance
            entries = mesh_selector.mesh_entries
            print(f"     Mesh entries count: {len(entries)}")
            
            if len(entries) > 0:
                entry = entries[0]
                try:
                    descriptor = entry.get_editor_property("descriptor")
                    mesh = descriptor.get_editor_property("static_mesh")
                    if mesh:
                        print(f"     ✓ Mesh configured: {mesh.get_name()}")
                    else:
                        print(f"     ✗ NO MESH SET IN DESCRIPTOR!")
                except Exception as e:
                    print(f"     ✗ Error reading mesh: {e}")
            else:
                print(f"     ✗ NO MESH ENTRIES!")
    
    # Check Surface Sampler settings in detail
    print(f"\n   Checking Surface Sampler settings...")
    for node in nodes:
        settings = node.get_settings()
        if "SurfaceSampler" in type(settings).__name__:
            print(f"     Surface Sampler found")
            
            # Check all relevant properties
            props_to_check = [
                "points_per_squared_meter",
                "unbounded", 
                "point_extent_min",
                "point_extent_max"
            ]
            
            for prop in props_to_check:
                try:
                    value = settings.get_editor_property(prop)
                    print(f"       {prop}: {value}")
                except Exception as e:
                    print(f"       {prop}: (cannot read)")
            
            break

    print(f"\n" + "=" * 80)
    print("SUCCESS!")
    print("=" * 80)
    print(f"\n✅ Test patch created at stadium center (0, 0, 0)")
    print(f"🌱 Check your viewport for grass!")
    print(f"\nExpected: ~{expected:,} grass instances in a {TEST_SIZE}m x {TEST_SIZE}m area")
    print(f"\nIf you see grass:")
    print(f"  - Success! PCG is working")
    print(f"  - Adjust density if needed (currently {TEST_DENSITY} points/m²)")
    print(f"  - Scale up to full stadium by increasing volume size")
    print(f"\nIf no grass:")
    print(f"  - Check debug output above for issues")
    print(f"  - Most likely: Volume doesn't overlap stadium ground")
    print(f"  - Or: Mesh not configured in spawner")

except Exception as e:
    print(f"\n" + "=" * 80)
    print("ERROR!")
    print("=" * 80)
    print(f"\n✗ Exception: {e}")
    import traceback
    traceback.print_exc()
