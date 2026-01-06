import os

def fix_file():
    file_path = "c:\\UnrealProjects\\coding\\unreal\\motion_system_track_based\\motion_builder.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # Find markers
    idx_movie_start = -1
    idx_command_start = -1
    
    for i, line in enumerate(lines):
        if "# MOVIE BUILDER (Main API)" in line:
            idx_movie_start = i - 1 # Include the separator line above it if possible
            # Check if line above is separator
            if i > 0 and "=====" in lines[i-1]:
                idx_movie_start = i - 1
            else:
                idx_movie_start = i
                
        if "# COMMAND BUILDERS" in line:
            idx_command_start = i - 1
            if i > 0 and "=====" in lines[i-1]:
                idx_command_start = i - 1
            else:
                idx_command_start = i
            break # Found both presumably, as command is after movie
            
    print(f"Movie Start: {idx_movie_start}")
    print(f"Command Start: {idx_command_start}")
    
    if idx_movie_start == -1 or idx_command_start == -1:
        print("Error: Could not find markers")
        return

    # Split parts
    # Part 1: Start -> Movie Start
    part1 = lines[:idx_movie_start]
    
    # Part 2: Movie Builder (Movie Start -> Command Start)
    part_movie = lines[idx_movie_start:idx_command_start]
    
    # Part 3: Command Builders (Command Start -> End)
    part_command = lines[idx_command_start:]
    
    # Construct new file
    new_lines = []
    
    # Add future import if not present
    if "from __future__ import annotations" not in lines[0]:
        new_lines.append("from __future__ import annotations\n")
        
    new_lines.extend(part1)
    new_lines.extend(part_command)
    new_lines.append("\n\n") # Ensure spacing
    new_lines.extend(part_movie)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
        
    print("Successfully reordered motion_builder.py")

if __name__ == "__main__":
    fix_file()
