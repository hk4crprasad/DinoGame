import pygame
import sys
import os
import random
from constants import *
from player import Player
from population import Population
from obstacle import Obstacle
from bird import Bird
from ground import Ground
from game_state import state
from training_data import TrainingData
from menu_state import GameMode, state as menu_state

# Define MAX_SPEED if not in constants
MAX_SPEED = 20  # Adjust this value as needed

class DinoGame:
    def __init__(self):
        pygame.init()
        # Set up fullscreen display
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        SCREEN_WIDTH = self.screen.get_width()
        SCREEN_HEIGHT = self.screen.get_height()
        pygame.display.set_caption("Dino Game AI")
        self.clock = pygame.time.Clock()
        
        self.load_assets()
        state.game = self  # Store game instance in state manager
        self.init_game()
        global game
        game = self  # Make the game instance globally accessible
        self.frame_speed = DEFAULT_FPS
        self.last_time = pygame.time.get_ticks()
        self.accumulated_time = 0
        self.time_step = 1000 / DEFAULT_FPS  # in milliseconds
        self.training_data = TrainingData()
        # Create training_data directory if it doesn't exist
        os.makedirs(os.path.join(os.path.dirname(__file__), 'training_data'), exist_ok=True)
        self.menu_font = pygame.font.Font(None, 64)
        self.menu_buttons = [
            "Play as Human",
            f"Train AI ({GENERATIONS} generations)",
            "Play with Trained AI"
        ]
        self.selected_button = 0

    def load_assets(self):
        self.images = {}
        for key, path in SPRITE_PATHS.items():
            full_path = os.path.join(ASSETS_DIR, path)
            self.images[key] = pygame.image.load(full_path).convert_alpha()

    def init_game(self):
        self.population = Population(500)  # 500 dinosaurs per generation
        self.obstacles = []
        self.birds = []
        self.grounds = []
        self.obstacle_timer = 0
        self.minimum_time_between_obstacles = 60
        self.random_addition = 0
        self.ground_counter = 0
        self.speed = 10
        self.frame_speed = 60
        self.show_best_each_gen = False
        self.show_nothing = False
        self.obstacle_history = []
        self.random_addition_history = []
        self.player = Player()  # Single player for human mode
        menu_state.player = self.player  # Store reference globally

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                self.handle_keypress(event.key)
        return True

    def handle_keypress(self, key):
        if menu_state.current_mode == GameMode.PLAYER:
            if key in (pygame.K_SPACE, pygame.K_UP):
                self.player.jump(True)
            elif key == pygame.K_DOWN:
                self.player.ducking(True)
        else:
            # AI control handling
            if key == pygame.K_PLUS or key == pygame.K_KP_PLUS:
                self.frame_speed = min(MAX_FPS, self.frame_speed + 10)
                self.time_step = 1000 / self.frame_speed
            elif key == pygame.K_MINUS or key == pygame.K_KP_MINUS:
                self.frame_speed = max(MIN_FPS, self.frame_speed - 10)
                self.time_step = 1000 / self.frame_speed
            elif key == pygame.K_r:  # Add reset functionality
                self.reset_game()

    def update(self):
        """Update game state based on mode"""
        if menu_state.current_mode == GameMode.PLAYER:
            self.update_obstacles()
            if not self.player.dead:
                self.player.update()
                # Update score correctly - increment every frame instead of checking frame_speed
                if self.frame_speed % 3 == 0:  # This was incorrectly checking frame_speed divisibility
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
                
                # Explicitly increment score for PLAY_AI mode
                if self.frame_speed % 3 == 0:
                    self.population.pop[0].score += 1
                    
                # Increase speed over time just like in other modes
                if self.frame_speed % 5 == 0 and self.speed < 20:  # Using 20 as MAX_SPEED
                    self.speed += 0.01
            else:
                # When AI dies, just reset the obstacles and position
                self.reset_obstacles()
                self.population.pop[0].reset()
        else:  # TRAIN_AI mode
            if self.population.gen >= GENERATIONS:
                # Save final model and return to menu
                self.training_data.save_to_file()
                print("Training completed! 50 generations reached.")
                menu_state.current_mode = GameMode.MENU
                return
                
            if not self.population_done():
                self.update_obstacles()
                self.population.update_alive()
            else:
                self.population.natural_selection()
                self.reset_obstacles()

    def update_obstacles(self):
        """Update obstacles, birds, and ground"""
        self.obstacle_timer += 1
        self.speed += SPEED_INCREMENT
        
        # Add new obstacle if timer is up
        if self.obstacle_timer > self.minimum_time_between_obstacles + self.random_addition:
            self.add_obstacle()
            
        # Add ground pieces
        self.ground_counter += 1
        if self.ground_counter > 10:
            self.ground_counter = 0
            self.grounds.append(Ground(self.screen.get_width(), self.screen.get_height()))
            
        # Move and show everything
        self.move_obstacles()
        if not self.show_nothing:
            self.show_obstacles()

    def move_obstacles(self):
        """Move obstacles, birds, and ground pieces"""
        # Move and remove off-screen obstacles
        for obstacle in self.obstacles[:]:
            obstacle.move(self.speed)
            if obstacle.pos_x < -PLAYER_XPOS:
                self.obstacles.remove(obstacle)
                
        # Move and remove off-screen birds
        for bird in self.birds[:]:
            bird.move(self.speed)
            if bird.pos_x < -PLAYER_XPOS:
                self.birds.remove(bird)
                
        # Move and remove off-screen ground pieces
        for ground in self.grounds[:]:
            ground.move(self.speed)
            if ground.pos_x < -PLAYER_XPOS:
                self.grounds.remove(ground)

    def add_obstacle(self):
        """Add a new obstacle or bird"""
        lifespan = self.population.population_life
        temp_int = 0
        
        # 15% chance for bird after 1000 lifespan
        if lifespan > 1000 and random.random() < 0.15:
            temp_int = random.randint(0, 2)
            self.birds.append(Bird(temp_int, self.screen.get_width(), self.images["bird"], self.images["bird1"]))
        else:
            temp_int = random.randint(0, 2)
            self.obstacles.append(Obstacle(temp_int, self.screen.get_width(), self.images))
            temp_int += 3
            
        self.obstacle_history.append(temp_int)
        self.random_addition = random.randint(0, 50)
        self.random_addition_history.append(self.random_addition)
        self.obstacle_timer = 0

    def show_obstacles(self):
        """Draw all game objects"""
        # Draw ground, obstacles, and birds
        for ground in self.grounds:
            ground.show(self.screen)
            
        for obstacle in self.obstacles:
            obstacle.show(self.screen, GROUND_HEIGHT)
            
        for bird in self.birds:
            bird.show(self.screen, GROUND_HEIGHT)
            
        # Draw player or AI based on mode
        if menu_state.current_mode == menu_state.GameMode.PLAYER:
            if not self.player.dead:
                self.player.show(self.screen, self.images)
        else:
            for player in self.population.pop:
                if not player.dead:
                    player.show(self.screen, self.images)

    def reset_obstacles(self):
        """Reset all obstacles and game state"""
        self.random_addition_history.clear()
        self.obstacle_history.clear()
        self.obstacles.clear()
        self.birds.clear()
        self.grounds.clear()
        self.obstacle_timer = 0
        self.random_addition = 0
        self.ground_counter = 0
        self.speed = 10

    def draw(self):
        if not self.show_nothing:
            self.screen.fill((250, 250, 250))
            
            # Draw ground line at bottom
            ground_y = self.screen.get_height() - GROUND_HEIGHT
            pygame.draw.line(self.screen, (0, 0, 0), 
                           (0, ground_y),
                           (self.screen.get_width(), ground_y), 
                           2)
                           
            # Draw everything else
            self.show_obstacles()
            self.draw_brain()
            self.draw_info()
            
            # Draw "Game Over" message and restart prompt for human player
            if menu_state.current_mode == GameMode.PLAYER and self.player.dead:
                font = pygame.font.Font(None, 64)
                game_over = font.render("Game Over", True, (255, 0, 0))
                restart = font.render("Press SPACE to restart", True, (0, 0, 0))
                menu_return = font.render("Press BACKSPACE for menu", True, (0, 0, 0))
                
                self.screen.blit(game_over, 
                               (self.screen.get_width()//2 - game_over.get_width()//2, 
                                self.screen.get_height()//3))
                self.screen.blit(restart, 
                               (self.screen.get_width()//2 - restart.get_width()//2, 
                                self.screen.get_height()//2))
                self.screen.blit(menu_return, 
                               (self.screen.get_width()//2 - menu_return.get_width()//2, 
                                self.screen.get_height()//2 + 70))
            
            pygame.display.flip()

    def draw_brain(self):
        """Draw the neural network visualization"""
        # Skip drawing neural network in human player mode
        if menu_state.current_mode == GameMode.PLAYER:
            return
            
        if not self.show_nothing:
            # Position network visualization on right side of screen
            start_x = self.screen.get_width() - NETWORK_WIDTH - 100
            start_y = NETWORK_MARGIN_Y
            
            # Draw background for network
            pygame.draw.rect(self.screen, (240, 240, 240), 
                           (start_x - 10, start_y - 10, 
                            NETWORK_WIDTH + 20, NETWORK_HEIGHT + 20))
            
            # Draw network
            if self.show_best_each_gen:
                self.gen_player_temp.brain.draw_genome(self.screen, 
                    start_x, start_y, NETWORK_WIDTH, NETWORK_HEIGHT)
            else:
                for player in self.population.pop:
                    if not player.dead:
                        player.brain.draw_genome(self.screen, 
                            start_x, start_y, NETWORK_WIDTH, NETWORK_HEIGHT)
                        break

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

        # Draw neural network labels - only for AI modes
        if menu_state.current_mode != GameMode.PLAYER:
            labels = [
                "Distance to next obstacle",
                "Height of obstacle",
                "Width of obstacle",
                "Bird height",
                "Speed",
                "Player's Y position",
                "Gap between obstacles",
                "Bias"
            ]
            
            network_x = self.screen.get_width() - NETWORK_WIDTH - 150
            for i, label in enumerate(labels):
                label_surface = small_font.render(label, True, (100, 100, 100))
                self.screen.blit(label_surface, 
                    (network_x, NETWORK_MARGIN_Y + (i+1)*44))

            # Draw output labels on right side
            output_labels = ["Small Jump", "Big Jump", "Duck"]
            for i, label in enumerate(output_labels):
                label_surface = small_font.render(label, True, (100, 100, 100))
                self.screen.blit(label_surface, 
                    (self.screen.get_width() - 200, 
                     NETWORK_MARGIN_Y + 100 + i*100))

    def run(self):
        running = True
        while running:
            if menu_state.current_mode == GameMode.MENU:
                running = self.handle_menu_input()
                self.draw_menu()
            else:
                # Existing game loop
                current_time = pygame.time.get_ticks()
                delta_time = current_time - self.last_time
                self.last_time = current_time
                self.accumulated_time += delta_time

                # Handle events regardless of accumulated time
                running = self.handle_events()

                # Update game state based on accumulated time
                while self.accumulated_time >= self.time_step:
                    self.update()
                    self.accumulated_time -= self.time_step

                # Always draw
                self.draw()
                
                # Limit FPS
                self.clock.tick(self.frame_speed)

        pygame.quit()
        sys.exit()

    def reset_game(self):
        """Reset the game state"""
        self.speed = 10
        self.obstacle_timer = 0
        self.random_addition = 0
        self.reset_obstacles()
        self.population = Population(500)

    def population_done(self):
        """Save training data when generation is complete"""
        if self.population.done():
            # Find best player of this generation
            best_player = max(self.population.pop, key=lambda p: p.score)
            
            # Save generation data including vision and decision history
            self.training_data.add_generation_data(
                self.population.gen,
                best_player.score,
                sum(p.score for p in self.population.pop) / len(self.population.pop),
                best_player.brain,
                len(self.population.species),
                best_player.vision_history,
                best_player.decision_history
            )
            
            # Save after each generation
            self.training_data.save_to_file()
            return True
        return False

    def load_trained_ai(self):
        """Load the last generation's AI model"""
        try:
            self.training_data.load_from_file()
            
            # Get last generation number
            last_gen = max(self.training_data.data.keys())
            last_gen_data = self.training_data.data[last_gen]
            
            # Initialize AI with last generation's data
            self.reset_obstacles()  # Clear any existing obstacles
            self.population = Population(1)  # Single player for demo
            self.population.gen = last_gen
            self.population.pop[0].brain = last_gen_data['best_genome'].clone()
            self.population.pop[0].brain.generate_network()  # Make sure network is generated
            self.speed = 10  # Reset speed
            
            print(f"Loaded AI from last generation (Gen {last_gen}) with score {last_gen_data['best_score']}")
            
        except FileNotFoundError as e:
            print("Error: No trained AI model found. Please complete AI training first.")
            raise e

    def draw_menu(self):
        self.screen.fill((250, 250, 250))
        
        # Draw title
        title = self.menu_font.render("Dino Game AI", True, (0, 0, 0))
        title_rect = title.get_rect(center=(self.screen.get_width()//2, 200))
        self.screen.blit(title, title_rect)
        
        # Draw buttons
        for i, text in enumerate(self.menu_buttons):
            color = (255, 0, 0) if i == self.selected_button else (0, 0, 0)
            button = self.menu_font.render(text, True, color)
            button_rect = button.get_rect(center=(self.screen.get_width()//2, 400 + i * 100))
            self.screen.blit(button, button_rect)
        
        pygame.display.flip()

    def handle_menu_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_button = (self.selected_button - 1) % len(self.menu_buttons)
                elif event.key == pygame.K_DOWN:
                    self.selected_button = (self.selected_button + 1) % len(self.menu_buttons)
                elif event.key == pygame.K_RETURN:
                    if self.selected_button == 0:
                        menu_state.current_mode = GameMode.PLAYER
                        self.init_human_game()
                    elif self.selected_button == 1:
                        menu_state.current_mode = GameMode.TRAIN_AI
                    else:
                        try:
                            self.load_trained_ai()
                            menu_state.current_mode = GameMode.PLAY_AI
                        except FileNotFoundError:
                            print("No trained AI data found!")
                            return True
        return True

    def init_human_game(self):
        """Initialize game for human player"""
        self.reset_obstacles()
        self.player = Player()
        menu_state.player = self.player
        self.speed = 10

if __name__ == "__main__":
    game = DinoGame()
    game.run()
