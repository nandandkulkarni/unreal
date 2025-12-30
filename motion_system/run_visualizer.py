"""
Motion System 2D Visualizer Launcher

Usage:
    python run_visualizer.py [movie_name]

Examples:
    python run_visualizer.py sprint_100m
    python run_visualizer.py race_400m
"""

import sys
import os

# To allow the shared motion_planner to run outside Unreal, inject a mock
try:
    import unreal
except ImportError:
    import unreal_mock
    sys.modules["unreal"] = unreal_mock

import argparse
import importlib

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from visualizer.main import TrackVisualizer

def main():
    parser = argparse.ArgumentParser(description="Run 2D Motion Visualizer")
    parser.add_argument("movie", nargs="?", default="sprint_100m", help="Name of movie module (e.g., sprint_100m)")
    args = parser.parse_args()
    
    # Load movie module
    try:
        module_name = f"movies.{args.movie}"
        movie_module = importlib.import_module(module_name)
        
        if hasattr(movie_module, "MOVIE"):
            movie_data = movie_module.MOVIE
        elif hasattr(movie_module, "define_movie"):
            movie_data = movie_module.define_movie()
        else:
            print(f"Error: Module {module_name} has no MOVIE or define_movie()")
            return
            
        print(f"Loaded movie: {args.movie}")
        print(f"Commands: {len(movie_data.get('plan', []))}")
        
        # Start visualizer (3000x800, 50% scale of previous run)
        app = TrackVisualizer(movie_data, width=3000, height=800, scale_factor=1.0)
        app.run()
        
    except ImportError as e:
        print(f"Error loading movie '{args.movie}': {e}")
        print("Available movies:")
        for f in os.listdir("movies"):
            if f.endswith(".py") and not f.startswith("__"):
                print(f"  - {f[:-3]}")

if __name__ == "__main__":
    main()
