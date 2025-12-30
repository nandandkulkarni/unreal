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
    
    def __init__(self, movie_data, width=1920, height=1920, scale_factor=1.0):
        """Initialize visualizer
        
        Args:
            movie_data: Dictionary from MovieBuilder.build()
            width: Screen width (default 1920 for ~20 inch display)
            height: Screen height (default 1920 for ~20 inch display)
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
        
        self.total_time = 60.0  # 60 second race
        self.running = True
    
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0  # Delta time in seconds
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                action = self.ui.handle_event(event)
                if action == "reset":
                    self.simulation.reset()
                elif action == "toggle_play":
                    pass  # UI handles this internally
            
            # Update simulation
            if self.ui.playing:
                self.simulation.update(dt * self.ui.speed_multiplier)
            
            # Render
            self.render()
        
        pygame.quit()
    
    def render(self):
        """Render one frame"""
        # Draw track
        self.track_renderer.draw(self.screen)
        
        # Draw runners
        for runner_name, runner_state in self.simulation.get_all_runners().items():
            pos = runner_state["position"]
            speed = runner_state["speed"]
            runner_id = runner_state["id"]
            
            self.runner_renderer.draw_runner(
                self.screen,
                runner_id,
                pos["x"],
                pos["y"],
                speed,
                runner_name
            )
            
            # Draw collision zones if enabled
            if self.ui.show_collision_zones:
                self.runner_renderer.draw_collision_zone(
                    self.screen,
                    pos["x"],
                    pos["y"],
                    0.5  # 0.5m collision radius
                )
        
        # Draw UI
        self.ui.draw(self.screen, self.simulation.current_time, self.total_time)
        
        pygame.display.flip()


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
