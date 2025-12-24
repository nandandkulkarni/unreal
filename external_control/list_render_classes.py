import unreal

# List all classes that might be related to rendering
all_classes = dir(unreal)

render_related = [
    cls for cls in all_classes 
    if any(keyword in cls.lower() for keyword in ['render', 'movie', 'capture', 'sequence', 'output', 'image'])
]

print("Available rendering-related classes in unreal module:")
print("=" * 60)
for cls in sorted(render_related):
    print(f"  {cls}")
print("=" * 60)
print(f"Total: {len(render_related)} classes found")
