"""
QA Tool - Read QA metadata from movie scripts and run verification

Usage:
    python qa_tool.py sprint_with_camera
    python qa_tool.py sprint_with_camera --frames 0,150,300,600
"""
import sys
import os
import importlib.util

# Add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)


def load_movie_module(movie_name):
    """Dynamically load a movie module by name"""
    movie_path = os.path.join(script_dir, "movies", f"{movie_name}.py")
    
    if not os.path.exists(movie_path):
        print(f"Error: Movie script not found: {movie_path}")
        return None
    
    spec = importlib.util.spec_from_file_location(movie_name, movie_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return module


def run_qa(movie_name, override_frames=None):
    """Run QA verification for a movie"""
    print(f"Loading movie: {movie_name}")
    
    # Load movie module
    module = load_movie_module(movie_name)
    if not module:
        return False
    
    # Check for QA metadata
    if not hasattr(module, 'QA'):
        print(f"Warning: No QA metadata found in {movie_name}.py")
        print("Add a QA dict to enable verification:")
        print('QA = {"frames": [0, 300, 600], "description": "..."}')
        return False
    
    qa_config = module.QA
    frames = override_frames or qa_config.get("frames", [])
    
    if not frames:
        print("Error: No frames specified for verification")
        return False
    
    print(f"\nQA Configuration:")
    print(f"  Description: {qa_config.get('description', 'N/A')}")
    print(f"  Frames: {frames}")
    if "expectations" in qa_config:
        print(f"  Expectations: {qa_config['expectations']}")
    
    # Trigger movie generation with frame capture
    print(f"\nGenerating movie and capturing frames...")
    
    # Update JSON to include verification frames
    import json
    json_path = os.path.join(script_dir, "dist", f"{movie_name}.json")
    
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            movie_data = json.load(f)
        
        movie_data["verification_frames"] = frames
        
        with open(json_path, 'w') as f:
            json.dump(movie_data, f, indent=4)
        
        print(f"Updated {json_path} with verification_frames")
        
        # Trigger Unreal
        from trigger_movie import trigger_movie
        result = trigger_movie(json_path)
        
        if result:
            print(f"\n✓ QA verification complete!")
            print(f"  Frames saved to: dist/frames/{movie_name}/")
            return True
        else:
            print(f"\n✗ QA verification failed")
            return False
    else:
        print(f"Error: Movie JSON not found: {json_path}")
        print(f"Run the movie script first: python movies/{movie_name}.py")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python qa_tool.py <movie_name> [--frames 0,300,600]")
        print("Example: python qa_tool.py sprint_with_camera")
        sys.exit(1)
    
    movie_name = sys.argv[1]
    
    # Parse optional frame override
    override_frames = None
    if "--frames" in sys.argv:
        idx = sys.argv.index("--frames")
        if idx + 1 < len(sys.argv):
            frame_str = sys.argv[idx + 1]
            override_frames = [int(f.strip()) for f in frame_str.split(",")]
    
    success = run_qa(movie_name, override_frames)
    sys.exit(0 if success else 1)
