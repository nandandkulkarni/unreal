import json
import sys

def compact_json_commands(input_file):
    """Compact JSON file so each command is on one line"""
    
    # Read the file
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Write with compact commands
    with open(input_file, 'w') as f:
        f.write('{\n')
        f.write(f'    "name": "{data["name"]}",\n')
        f.write(f'    "create_new_level": {str(data["create_new_level"]).lower()},\n')
        f.write(f'    "fps": {data["fps"]},\n')
        f.write('    "plan": [\n')
        
        for i, cmd in enumerate(data['plan']):
            comma = ',' if i < len(data['plan']) - 1 else ''
            f.write(f'        {json.dumps(cmd, separators=(",", ":"))}{comma}\n')
        
        f.write('    ]\n')
        f.write('}\n')
    
    print(f"Compacted {input_file}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        compact_json_commands(sys.argv[1])
    else:
        # Default to tandem_run_square.json
        compact_json_commands('movies/tandem_run_square.json')
