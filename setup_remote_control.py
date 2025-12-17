"""
Setup Remote Control API for Python Script Execution
Run this script to configure Unreal Engine project to allow Python script execution via Remote Control API
"""

import os
import re

def setup_remote_control():
    """Add Remote Control configuration to DefaultEngine.ini"""
    
    config_path = r"C:\U\CinematicPipeline\Config\DefaultEngine.ini"
    
    print("=" * 60)
    print("Remote Control API Setup")
    print("=" * 60)
    print(f"Config file: {config_path}\n")
    
    if not os.path.exists(config_path):
        print(f"ERROR: Config file not found: {config_path}")
        return False
    
    # Read the current config
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already configured
    if 'RemoteControlWebInterfaceAllowedObjects' in content and 'PythonScriptLibrary' in content:
        print("✓ Remote Control already configured for Python script execution")
        print("  PythonScriptLibrary is already in allowed objects")
        return True
    
    # Find where to add the configuration (after WebControl.EnableServerOnStartup)
    pattern = r'(; Enables WebControl API\s*\nWebControl\.EnableServerOnStartup=1)'
    
    if not re.search(pattern, content):
        print("WARNING: Could not find WebControl.EnableServerOnStartup setting")
        print("Adding at the end of file...")
        
        # Add at end
        new_config = """

; Enables WebControl API
WebControl.EnableServerOnStartup=1

; Remote Control API Configuration
[RemoteControl]
+RemoteControlWebInterfaceAllowedObjects=/Script/PythonScriptPlugin.PythonScriptLibrary
"""
        content += new_config
    else:
        # Add after WebControl section
        replacement = r'\1\n\n; Remote Control API Configuration\n[RemoteControl]\nbDeveloperMode=True\nbRemoteExecution=True\nbEnableRemotePythonExecution=True\n+RemoteControlWebInterfaceAllowedObjects=/Script/PythonScriptPlugin.PythonScriptLibrary'
        content = re.sub(pattern, replacement, content)
    
    # Backup original file
    backup_path = config_path + ".backup"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Backup created: {backup_path}")
    
    # Write updated config
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Configuration added to {config_path}")
    print("\nAdded configuration:")
    print("  [RemoteControl]")
    print("  +RemoteControlWebInterfaceAllowedObjects=/Script/PythonScriptPlugin.PythonScriptLibrary")
    print("\n" + "=" * 60)
    print("✓ Setup complete!")
    print("=" * 60)
    print("\nNEXT STEPS:")
    print("1. Restart Unreal Engine for changes to take effect")
    print("2. Start the web server in Unreal console: WebControl.StartServer")
    print("3. Run: python run_cinematic_script.py")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    setup_remote_control()
