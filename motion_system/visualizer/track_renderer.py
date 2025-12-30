"""
2D Track Renderer for Pygame Visualizer

Renders a 400m standard track with lanes, waypoints, and markers.
"""

import pygame
import math

class TrackRenderer:
    """Renders 400m track geometry"""
    
    def __init__(self, screen_width=1200, screen_height=800):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Track dimensions (in meters, will scale to screen)
        self.straight_length = 84.39  # meters
        self.curve_radius = 36.5      # meters
        self.lane_width = 1.22        # meters
        self.num_lanes = 8
        
        # Colors
        self.track_color = (200, 100, 50)  # Reddish track
        self.lane_color = (255, 255, 255)   # White lane lines
        self.grass_color = (34, 139, 34)    # Green grass
        
        # Calculate scale to fit screen
        total_width = self.straight_length + 2 * self.curve_radius
        total_height = 2 * self.curve_radius + self.num_lanes * self.lane_width
        
        scale_x = (screen_width - 100) / total_width
        scale_y = (screen_height - 100) / total_height
        self.scale = min(scale_x, scale_y)
        
        # Offset to center track
        self.offset_x = (screen_width - total_width * self.scale) / 2
        self.offset_y = (screen_height - total_height * self.scale) / 2
    
    def world_to_screen(self, x, y):
        """Convert world coordinates (meters) to screen coordinates (pixels)"""
        screen_x = self.offset_x + x * self.scale
        screen_y = self.offset_y + y * self.scale
        return (int(screen_x), int(screen_y))
    
    def draw(self, screen):
        """Draw the complete track"""
        # Fill background with grass
        screen.fill(self.grass_color)
        
        # Draw track surface (simplified as rounded rectangle)
        self._draw_track_surface(screen)
        
        # Draw lane lines
        self._draw_lane_lines(screen)
        
        # Draw start/finish line
        self._draw_start_finish_line(screen)
    
    def _draw_track_surface(self, screen):
        """Draw the main track surface"""
        # For simplicity, draw as rounded rectangle
        # In reality, it's two straights connected by semicircles
        
        # Calculate track bounds
        inner_radius = self.curve_radius
        outer_radius = inner_radius + self.num_lanes * self.lane_width
        
        # Draw outer track boundary (simplified)
        # Left straight
        p1 = self.world_to_screen(0, 0)
        p2 = self.world_to_screen(self.straight_length, 0)
        p3 = self.world_to_screen(self.straight_length, outer_radius * 2)
        p4 = self.world_to_screen(0, outer_radius * 2)
        
        pygame.draw.polygon(screen, self.track_color, [p1, p2, p3, p4])
        
        # Draw curves (simplified as arcs)
        # Top curve
        center_top = self.world_to_screen(self.straight_length + inner_radius, inner_radius)
        pygame.draw.circle(screen, self.track_color, center_top, int(outer_radius * self.scale))
        
        # Bottom curve
        center_bottom = self.world_to_screen(-inner_radius, inner_radius)
        pygame.draw.circle(screen, self.track_color, center_bottom, int(outer_radius * self.scale))
    
    def _draw_lane_lines(self, screen):
        """Draw white lane divider lines"""
        for lane in range(1, self.num_lanes):
            y = lane * self.lane_width
            
            # Draw straight sections
            p1 = self.world_to_screen(0, y)
            p2 = self.world_to_screen(self.straight_length, y)
            pygame.draw.line(screen, self.lane_color, p1, p2, 2)
    
    def _draw_start_finish_line(self, screen):
        """Draw start/finish line"""
        # Vertical line at x=0
        p1 = self.world_to_screen(0, 0)
        p2 = self.world_to_screen(0, self.num_lanes * self.lane_width)
        pygame.draw.line(screen, (255, 255, 0), p1, p2, 4)  # Yellow line
        
        # Draw "START/FINISH" text
        font = pygame.font.Font(None, 24)
        text = font.render("START/FINISH", True, (255, 255, 0))
        text_pos = self.world_to_screen(2, -1)
        screen.blit(text, text_pos)
    
    def draw_waypoint(self, screen, x, y, name, color=(255, 0, 0)):
        """Draw a waypoint marker"""
        pos = self.world_to_screen(x, y)
        pygame.draw.circle(screen, color, pos, 5)
        
        # Draw waypoint name
        font = pygame.font.Font(None, 16)
        text = font.render(name, True, color)
        screen.blit(text, (pos[0] + 8, pos[1] - 8))
