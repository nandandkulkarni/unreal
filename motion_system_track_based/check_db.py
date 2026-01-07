import unreal
path = "/Game/MotionMatching/MannyMotionDatabase"
exists = unreal.EditorAssetLibrary.does_asset_exist(path)
msg = f"Database {path} exists: {exists}"
with open(r"C:\UnrealProjects\coding\unreal\motion_system_track_based\db_check.txt", 'w') as f: f.write(msg)
