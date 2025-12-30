"""
Runner Renderer for Pygame Visualizer

Renders runners as colored circles with labels and speed indicators.
"""

import pygame
import math

class RunnerRenderer:
    """Renders individual runners on the track"""
    
    # Runner colors (distinct for each runner)
    COLORS = [
        (255, 0, 0),      # Red
        (0, 0, 255),      # Blue
        (0, 255, 0),      # Green
        (255, 255, 0),    # Yellow
        (255, 0, 255),    # Magenta
        (0, 255, 255),    # Cyan
    ]
    
    def __init__(self, track_renderer):
        self.track = track_renderer
        # Scale radius based on track scale but cap it at a reasonable pixel size
        lane_width_px = 1.22 * self.track.scale
        # Cap runner radius at 30 pixels so they don't look like giants at 5x scale
        self.runner_radius = min(30, max(5, int(lane_width_px * 0.4)))
    
    def draw_runner(self, screen, runner_id, x, y, speed, name):
        """Draw a single runner"""
        pos = self.track.world_to_screen(x, y)
        color = self.COLORS[runner_id % len(self.COLORS)]
        
        # Draw runner circle
        pygame.draw.circle(screen, color, pos, self.runner_radius)
        
        # Keep outline at fixed 2px thickness
        pygame.draw.circle(screen, (0, 0, 0), pos, self.runner_radius, 2)
        
        # Draw runner name with slightly larger font than default
        font = pygame.font.Font(None, 24)
        text = font.render(name, True, (255, 255, 255))
        text_rect = text.get_rect(center=(pos[0], pos[1] - self.runner_radius - 15))
        
        # Draw background for text
        bg_rect = text_rect.inflate(6, 4)
        pygame.draw.rect(screen, (0, 0, 0), bg_rect)
        screen.blit(text, text_rect)
        
        # Draw speed indicator (arrow)
        if speed > 0.1:
            self._draw_speed_arrow(screen, pos, speed, color)
    
    def _draw_speed_arrow(self, screen, pos, speed, color):
        """Draw arrow indicating speed and direction"""
        # Arrow length proportional to speed
        arrow_length = min(30, speed * 3)
        
        # For now, assume forward direction (right)
        end_x = pos[0] + arrow_length
        end_y = pos[1]
        
        # Draw arrow line
        pygame.draw.line(screen, color, pos, (end_x, end_y), 3)
        
        # Draw arrowhead
        arrow_size = 5
        pygame.draw.polygon(screen, color, [
            (end_x, end_y),
            (end_x - arrow_size, end_y - arrow_size),
            (end_x - arrow_size, end_y + arrow_size)
        ])
    
    def draw_collision_zone(self, screen, x, y, radius_meters):
        """Draw collision detection radius around runner"""
        pos = self.track.world_to_screen(x, y)
        radius_pixels = int(radius_meters * self.track.scale)
        pygame.draw.circle(screen, (255, 0, 0), pos, radius_pixels, 1)
