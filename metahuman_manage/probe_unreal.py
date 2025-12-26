import unreal
import os

log_file = r"C:\UnrealProjects\Coding\unreal\metahuman_manage\probe_log.txt"

with open(log_file, "w") as f:
    f.write("Probing unreal module for IK factories...\n")
    factories = [x for x in dir(unreal) if "Factory" in x and "IK" in x]
    f.write(f"IK Factories: {factories}\n")
    
    classes = [x for x in dir(unreal) if "IKRetargeter" in x]
    f.write(f"IKRetargeter related: {classes}\n")

print("Probe complete. See probe_log.txt")
