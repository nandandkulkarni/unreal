"""
2D Track Renderer for Pygame Visualizer

Renders a 400m standard track with lanes, waypoints, and markers.
"""

import pygame
import math

class TrackRenderer:
    """Renders 400m track geometry"""
    
    def __init__(self, screen_width=1920, screen_height=1920, scale_factor=1.0):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scale_factor = scale_factor
        
        # Track dimensions (100m straight)
        self.track_length = 100.0     # meters
        self.lane_width = 1.22        # meters
        self.num_lanes = 6
        
        # Calculate scale to fit 120m (100m + 10m margin each side) into the window
        # This ensures the "image is wider than the track end"
        world_width_to_view = self.track_length + 20.0
        self.base_scale = self.screen_width / world_width_to_view
        
        # Apply user scale_factor (default 5x makes it massive/scrollable)
        self.scale = self.base_scale * scale_factor
        
        # Colors
        self.track_color = (180, 80, 40)    # Reddish track
        self.lane_color = (255, 255, 255)   # White
        self.marker_color = (255, 255, 0)   # Yellow
        self.grass_color = (20, 80, 20)     # Dark green
        
        # Center vertically and start from left margin
        self.offset_x = 10.0 * self.scale
        total_height_px = self.num_lanes * self.lane_width * self.scale
        self.offset_y = (screen_height - total_height_px) / 2
    
    def world_to_screen(self, x, y):
        """Convert world coordinates (meters) to screen coordinates (pixels)"""
        screen_x = self.offset_x + x * self.scale
        screen_y = self.offset_y + y * self.scale
        return (int(screen_x), int(screen_y))
    
    def draw(self, screen):
        """Draw the 100m straight track"""
        screen.fill(self.grass_color)
        
        # Draw track surface
        p1 = self.world_to_screen(0, 0)
        p2 = self.world_to_screen(self.track_length, 0)
        p3 = self.world_to_screen(self.track_length, self.num_lanes * self.lane_width)
        p4 = self.world_to_screen(0, self.num_lanes * self.lane_width)
        pygame.draw.polygon(screen, self.track_color, [p1, p2, p3, p4])
        
        # Draw lane lines
        for i in range(self.num_lanes + 1):
            y = i * self.lane_width
            start = self.world_to_screen(0, y)
            end = self.world_to_screen(self.track_length, y)
            # Keep lane thickness at 2-3 pixels regardless of scale
            pygame.draw.line(screen, self.lane_color, start, end, 2)
            
        # Draw Start Marker (0m)
        self._draw_marker(screen, 0, "START (0m)")
        
        # Draw Finish Marker (95m)
        self._draw_marker(screen, 95, "FINISH (95m)")
        
    def _draw_marker(self, screen, x, label):
        """Draw vertical marker line and label"""
        # Marker lines should span slightly beyond lanes
        p1 = self.world_to_screen(x, -0.3)
        p2 = self.world_to_screen(x, self.num_lanes * self.lane_width + 0.3)
        
        # Keep thickness at 6 pixels (don't scale thickness)
        pygame.draw.line(screen, self.marker_color, p1, p2, 6)
        
        # Keep font size reasonable (40-48 shifted by scale?)
        # Actually fixed 40 is good
        font = pygame.font.Font(None, 40)
        text = font.render(label, True, self.marker_color)
        screen.blit(text, (p1[0] - 10, p1[1] - 50))
    
    def draw_waypoint(self, screen, x, y, name, color=(255, 0, 0)):
        """Draw a waypoint marker"""
        pos = self.world_to_screen(x, y)
        pygame.draw.circle(screen, color, pos, 5)
        
        # Draw waypoint name
        font = pygame.font.Font(None, 16)
        text = font.render(name, True, color)
        screen.blit(text, (pos[0] + 8, pos[1] - 8))
