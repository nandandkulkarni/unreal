"""
Reflect on PCGComponent to find all generation-related methods
"""
import unreal

print("=" * 80)
print("PCG COMPONENT GENERATION METHODS REFLECTION")
print("=" * 80)

# Find a PCG Volume to get its component
all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
pcg_volume = None

for actor in all_actors:
    if actor.get_class().get_name() == "PCGVolume":
        pcg_volume = actor
        break

if not pcg_volume:
    print("No PCG Volume found")
else:
    print(f"\nFound PCG Volume: {pcg_volume.get_actor_label()}")
    
    # Get PCG Component
    pcg_comp = None
    for comp in pcg_volume.get_components_by_class(unreal.PCGComponent):
        pcg_comp = comp
        break
    
    if pcg_comp:
        print(f"Found PCG Component: {pcg_comp}")
        
        # Find all methods
        all_methods = dir(pcg_comp)
        
        # Filter for generation-related methods
        gen_methods = [m for m in all_methods if 'generat' in m.lower() and not m.startswith('_')]
        print(f"\n{'='*80}")
        print("GENERATION-RELATED METHODS:")
        print('='*80)
        for method in gen_methods:
            attr = getattr(pcg_comp, method)
            if callable(attr):
                print(f"\n  {method}")
                print(f"    Type: {type(attr)}")
                try:
                    import inspect
                    sig = inspect.signature(attr)
                    print(f"    Signature: {sig}")
                except:
                    print(f"    (Cannot get signature)")
        
        # Also check for other potentially relevant methods
        print(f"\n{'='*80}")
        print("OTHER POTENTIALLY RELEVANT METHODS:")
        print('='*80)
        
        keywords = ['refresh', 'update', 'execute', 'run', 'trigger', 'force', 'rebuild']
        for keyword in keywords:
            methods = [m for m in all_methods if keyword in m.lower() and not m.startswith('_')]
            if methods:
                print(f"\n  Methods containing '{keyword}':")
                for method in methods:
                    print(f"    - {method}")
        
        # Check current state
        print(f"\n{'='*80}")
        print("CURRENT COMPONENT STATE:")
        print('='*80)
        
        state_props = ['generated', 'is_generated', 'generation_trigger']
        for prop in state_props:
            try:
                value = pcg_comp.get_editor_property(prop)
                print(f"  {prop}: {value}")
            except:
                pass
    else:
        print("No PCG Component found")
