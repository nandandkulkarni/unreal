"""
2D Track Visualizer - Main Entry Point

Pygame-based 2D simulation of 400m dash choreography.
"""

import pygame
import sys

from visualizer.track_renderer import TrackRenderer
from visualizer.runner_renderer import RunnerRenderer
from visualizer.simulation_engine import SimulationEngine
from visualizer.ui_controls import UIControls

class TrackVisualizer:
    """Main visualizer application"""
    
    def __init__(self, movie_data, width=3000, height=800, scale_factor=1.0):
        """Initialize visualizer
        
        Args:
            movie_data: Dictionary from MovieBuilder.build()
            width: Screen width (default 3000)
            height: Screen height (default 800)
            scale_factor: Scale multiplier for track (1.0 = fit to screen)
        """
        pygame.init()
        
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("400m Dash - 2D Visualizer")
        
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Initialize components
        self.track_renderer = TrackRenderer(width, height, scale_factor)
        self.runner_renderer = RunnerRenderer(self.track_renderer)
        self.simulation = SimulationEngine(movie_data)
        self.ui = UIControls(width, height)
        
        self.total_time = 60.0 # 60 second race
        self.running = True
    
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                action = self.ui.handle_event(event)
                if action == "reset":
                    self.simulation.reset()
            
            # Update simulation
            if self.ui.playing:
                self.simulation.update(dt * self.ui.speed_multiplier)
            
            # Render
            self.render()
        
        pygame.quit()
    
    def render(self):
        """Render one frame to screen"""
        # Create a surface for the frame
        frame_surface = pygame.Surface((self.width, self.height))
        # Fixed camera at x=0 to show the whole wide track
        self.draw_to_surface(frame_surface, 0)
        self.screen.blit(frame_surface, (0, 0))
        pygame.display.flip()

    def draw_to_surface(self, surface, camera_offset_x=0):
        """Draw simulation state to any surface with optional offset"""
        # Offset all rendering by camera_offset_x
        # We manually apply offset to renderers or use a temporary subsurface/transformation
        # For simplicity, we'll temporarily adjust track_renderer offset
        original_offset_x = self.track_renderer.offset_x
        self.track_renderer.offset_x -= camera_offset_x
        
        # Draw track
        self.track_renderer.draw(surface)
        
        # Draw runners
        for runner_name, runner_state in self.simulation.get_all_runners().items():
            pos = runner_state["position"]
            speed = runner_state["speed"]
            runner_id = runner_state["id"]
            
            self.runner_renderer.draw_runner(
                surface, runner_id, pos["x"], pos["y"], speed, runner_name
            )
            
            if self.ui.show_collision_zones:
                self.runner_renderer.draw_collision_zone(surface, pos["x"], pos["y"], 0.5)
        
        # Draw UI (don't offset UI)
        self.track_renderer.offset_x = original_offset_x
        self.ui.draw(surface, self.simulation.current_time, self.total_time)


def main():
    """Entry point"""
    # For now, use dummy movie data
    # TODO: Load from actual race_400m.py
    movie_data = {
        "name": "400m Dash",
        "fps": 30,
        "plan": []
    }
    
    visualizer = TrackVisualizer(movie_data)
    visualizer.run()


if __name__ == "__main__":
    main()
