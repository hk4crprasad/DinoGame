import os

import pygame

from menu_state import GameMode
import menu_state

# Window settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 144
GENERATIONS = 60
# Game settings
GROUND_HEIGHT = 100  # Reduced to keep ground lower
PLAYER_XPOS = 250   # Player position from left

# Neural network visualization
NETWORK_MARGIN_X = 700  # Space from left side
NETWORK_MARGIN_Y = 50   # Space from top
NETWORK_WIDTH = 500    # Width of network display
NETWORK_HEIGHT = 400   # Height of network display

# Performance settings
MIN_FPS = 30
MAX_FPS = 240
DEFAULT_FPS = 60
SPEED_INCREMENT = 0.0008  # Reduced from 0.002 to make speed increase more gradual

# Asset paths
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
SPRITE_PATHS = {
    "dino_run1": "dinorun0000.png",
    "dino_run2": "dinorun0001.png",
    "dino_jump": "dinoJump0000.png",
    "dino_duck": "dinoduck0000.png",
    "dino_duck1": "dinoduck0001.png",
    "small_cactus": "cactusSmall0000.png",
    "big_cactus": "cactusBig0000.png",
    "many_small_cactus": "cactusSmallMany0000.png",
    "bird": "berd.png",
    "bird1": "berd2.png"
}

def update(self):
    """Update game state based on mode"""
    if menu_state.current_mode == GameMode.PLAYER:
        self.update_obstacles()
        if not self.player.dead:
            self.player.update()
            # Update score correctly - increment every frame instead of checking frame_speed
            if self.frame_speed % 3 == 0:
                self.player.score += 1
        else:
            # Handle human player death - wait for spacebar to restart or backspace to return to menu
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_RETURN]:
                self.reset_obstacles()
                self.player.reset()
            elif keys[pygame.K_BACKSPACE]:
                # Return to main menu
                menu_state.current_mode = GameMode.MENU
                self.selected_button = 0
    elif menu_state.current_mode == GameMode.PLAY_AI:
        # Special handling for playing trained AI
        self.update_obstacles()
        if not self.population.pop[0].dead:
            # First look at environment
            self.population.pop[0].look(self.obstacles, self.birds, self.speed)
            # Then think and make decisions
            self.population.pop[0].think()
            # Finally update physics
            self.population.pop[0].update()
            
            # Make sure score gets updated for AI player
            if self.frame_speed % 3 == 0:
                self.population.pop[0].score += 1
        else:
            # When AI dies, just reset the obstacles and position
            self.reset_obstacles()
            self.population.pop[0].reset()

def draw_info(self):
    """Draw game information"""
    font = pygame.font.Font(None, 40)
    small_font = pygame.font.Font(None, 20)
    
    # Draw score with proper handling for all modes
    if menu_state.current_mode == GameMode.PLAYER:
        score_text = f"Score: {self.player.score}"
    elif menu_state.current_mode == GameMode.PLAY_AI:
        # Display the score of the single AI player being shown
        score_text = f"Score: {self.population.pop[0].score}"
    else:
        # For TRAIN_AI mode
        score_text = f"Score: {self.population.population_life//3 if not self.show_best_each_gen else self.gen_player_temp.score}"
    
    score_surface = font.render(score_text, True, (100, 100, 100))
    self.screen.blit(score_surface, (30, self.screen.get_height() - 30))
    
    # Draw generation - only for AI modes
    if menu_state.current_mode != GameMode.PLAYER:
        gen_text = f"Gen: {self.population.gen + 1}"
        gen_surface = font.render(gen_text, True, (100, 100, 100))
        self.screen.blit(gen_surface, (self.screen.get_width() - 40 - gen_surface.get_width(), 
                                     self.screen.get_height() - 30))
        
        # Add Dino Alive counter for TRAIN_AI mode
        if menu_state.current_mode == GameMode.TRAIN_AI:
            alive_count = sum(1 for player in self.population.pop if not player.dead)
            dino_alive_text = f"Dino Alive: {alive_count}/{len(self.population.pop)}"
            dino_alive_surface = font.render(dino_alive_text, True, (100, 100, 100))
            self.screen.blit(dino_alive_surface, (self.screen.get_width() // 2 - dino_alive_surface.get_width() // 2, 
                                              self.screen.get_height() - 30))
