import unreal

sequences = unreal.EditorAssetLibrary.list_assets("/Game/Sequences", recursive=False)
test_sequences = [s.split("/")[-1].split(".")[0] for s in sequences if "Test" in s]

print("\nTest Sequences Found:")
print("=" * 60)
for seq in test_sequences:
    print(f"  {seq}")
print(f"\nTotal: {len(test_sequences)} test sequence(s)")
print("=" * 60)
