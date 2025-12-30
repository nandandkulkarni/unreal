"""
UI Controls for Pygame Visualizer

Provides play/pause, speed control, and timeline scrubbing.
"""

import pygame

class UIControls:
    """UI controls for simulation playback"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Control state
        self.playing = False
        self.speed_multiplier = 1.0
        self.show_collision_zones = False
        
        # UI layout
        self.control_bar_height = 60
        self.control_bar_y = screen_height - self.control_bar_height
        
        # Fonts
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
    
    def draw(self, screen, current_time, total_time):
        """Draw UI controls
        
        Args:
            screen: Pygame screen
            current_time: Current simulation time
            total_time: Total duration
        """
        # Draw control bar background
        pygame.draw.rect(screen, (40, 40, 40), 
                        (0, self.control_bar_y, self.screen_width, self.control_bar_height))
        
        # Draw time display
        time_text = f"Time: {current_time:.2f}s / {total_time:.1f}s"
        text_surface = self.font.render(time_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, self.control_bar_y + 10))
        
        # Draw play/pause button
        button_x = 10
        button_y = self.control_bar_y + 35
        button_text = "⏸ PAUSE" if self.playing else "▶ PLAY"
        button_surface = self.font.render(button_text, True, (0, 255, 0) if self.playing else (255, 255, 0))
        screen.blit(button_surface, (button_x, button_y))
        
        # Draw speed control
        speed_x = 150
        speed_text = f"Speed: {self.speed_multiplier}x"
        speed_surface = self.font.render(speed_text, True, (255, 255, 255))
        screen.blit(speed_surface, (speed_x, button_y))
        
        # Draw instructions
        instructions = [
            "SPACE: Play/Pause",
            "↑↓: Speed",
            "R: Reset",
            "C: Collision Zones"
        ]
        
        inst_x = 350
        for i, inst in enumerate(instructions):
            inst_surface = self.small_font.render(inst, True, (200, 200, 200))
            screen.blit(inst_surface, (inst_x + i * 150, button_y + 5))
    
    def handle_event(self, event):
        """Handle keyboard/mouse events
        
        Args:
            event: Pygame event
        
        Returns:
            Action string or None
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.playing = not self.playing
                return "toggle_play"
            
            elif event.key == pygame.K_UP:
                self.speed_multiplier = min(10.0, self.speed_multiplier * 2)
                return "speed_up"
            
            elif event.key == pygame.K_DOWN:
                self.speed_multiplier = max(0.1, self.speed_multiplier / 2)
                return "speed_down"
            
            elif event.key == pygame.K_r:
                return "reset"
            
            elif event.key == pygame.K_c:
                self.show_collision_zones = not self.show_collision_zones
                return "toggle_collision"
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = event.pos
                
                # Check play/pause button (approximate area)
                button_rect = pygame.Rect(10, self.control_bar_y + 30, 100, 25)
                if button_rect.collidepoint(mouse_pos):
                    self.playing = not self.playing
                    return "toggle_play"
        
        return None
