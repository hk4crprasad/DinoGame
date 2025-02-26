import pygame
from typing import List, Optional
from genome import Genome
from constants import GROUND_HEIGHT, PLAYER_XPOS
from menu_state import state as menu_state, GameMode

class Player:
    def __init__(self):
        self.fitness = 0
        self.vision = [0.0] * 7  # Initialize with exactly 7 floats for all inputs
        self.decision = [0.0] * 3  # Initialize with exactly 3 floats for outputs
        self.unadjusted_fitness = 0
        self.lifespan = 0
        self.best_score = 0
        self.dead = False
        self.score = 0
        self.gen = 0

        # Neural network settings
        self.genome_inputs = 7
        self.genome_outputs = 3
        self.brain = Genome(self.genome_inputs, self.genome_outputs)

        # Physics properties
        self.pos_y = 0
        self.vel_y = 0
        self.gravity = 1.2
        self.run_count = -5
        self.size = 20

        # Game state
        self.duck = False
        self.replay = False
        self.replay_obstacles = []
        self.replay_birds = []
        self.local_obstacle_history = []
        self.local_random_addition_history = []
        self.history_counter = 0
        self.local_obstacle_timer = 0
        self.local_speed = 10
        self.local_random_addition = 0

        self.vision_history = []  # Store what the AI sees
        self.decision_history = []  # Store what the AI decides to do

    def jump(self, big_jump: bool):
        """Make the player jump"""
        if self.pos_y == 0:
            if big_jump:
                self.gravity = 1
                self.vel_y = 20
            else:
                self.gravity = 1.2
                self.vel_y = 16

    def ducking(self, is_ducking: bool):
        """Make the player duck"""
        if self.pos_y != 0 and is_ducking:
            self.gravity = 3
        self.duck = is_ducking

    def reset_input(self):
        """Reset ducking when key is released"""
        self.ducking(False)

    def update(self):
        """Update player state"""
        # For human player
        if menu_state.current_mode == GameMode.PLAYER:
            keys = pygame.key.get_pressed()
            if not keys[pygame.K_DOWN]:
                self.reset_input()
        # For AI players
        else:
            self.lifespan += 1
            if self.lifespan % 3 == 0:
                self.score += 1

        # Always update physics
        self.move()

    def move(self):
        """Update player position and check collisions"""
        self.pos_y += self.vel_y
        if self.pos_y > 0:
            self.vel_y -= self.gravity
        else:
            self.vel_y = 0
            self.pos_y = 0

        if not self.replay:
            from game_state import state
            game = state.game
            
            for obstacle in game.obstacles:
                if obstacle.collided(PLAYER_XPOS, self.pos_y + game.images["dino_run1"].get_height()/2, 
                                  game.images["dino_run1"].get_width()*0.5, 
                                  game.images["dino_run1"].get_height()):
                    self.dead = True

            for bird in game.birds:
                if self.duck and self.pos_y == 0:
                    if bird.collided(PLAYER_XPOS, self.pos_y + game.images["dino_duck"].get_height()/2,
                                   game.images["dino_duck"].get_width()*0.8,
                                   game.images["dino_duck"].get_height()):
                        self.dead = True
                else:
                    if bird.collided(PLAYER_XPOS, self.pos_y + game.images["dino_run1"].get_height()/2,
                                   game.images["dino_run1"].get_width()*0.5,
                                   game.images["dino_run1"].get_height()):
                        self.dead = True

    def think(self):
        """Process neural network decision"""
        # Get neural network output
        self.decision = self.brain.feed_forward(self.vision)
        
        # Find the highest output
        max_output = max(self.decision)
        max_index = self.decision.index(max_output)
        
        # Reduced threshold and improved decision making
        if max_output > 0.5:  # Lowered threshold to make AI more active
            if max_index == 0:
                self.jump(False)  # Small jump
            elif max_index == 1:
                self.jump(True)   # Big jump
            elif max_index == 2:
                self.ducking(True)  # Duck
        else:
            self.ducking(False)  # Stand up if not ducking

    def calculate_fitness(self):
        """Calculate fitness score"""
        self.fitness = self.score * self.score

    def clone(self):
        """Create a copy of this player"""
        clone = Player()
        clone.brain = self.brain.clone()
        clone.fitness = self.fitness
        clone.brain.generate_network()
        clone.gen = self.gen
        clone.best_score = self.score
        return clone

    def clone_for_replay(self):
        """Create a copy for replay purposes"""
        clone = self.clone()
        clone.replay = True
        if self.replay:
            clone.local_obstacle_history = self.local_obstacle_history.copy()
            clone.local_random_addition_history = self.local_random_addition_history.copy()
        else:
            from game_state import state
            game = state.game
            clone.local_obstacle_history = game.obstacle_history.copy()
            clone.local_random_addition_history = game.random_addition_history.copy()
        return clone

    def crossover(self, parent2: 'Player') -> 'Player':
        """Create a new player from two parents"""
        child = Player()
        # Let the more fit parent's genome handle the crossover
        if self.fitness > parent2.fitness:
            child.brain = self.brain.crossover(parent2.brain)
        else:
            child.brain = parent2.brain.crossover(self.brain)
        
        # Generate the neural network for the child
        child.brain.generate_network()
        return child

    def look(self, obstacles, birds, speed):
        """Update vision inputs based on game state"""
        # Reset vision array first
        self.vision = [0.0] * 7
        
        # Find closest obstacle
        min_dist = 10000
        min_index = -1
        is_bird = False
        
        # Check obstacles first
        for i, obstacle in enumerate(obstacles):
            dist = obstacle.pos_x + obstacle.w/2 - (PLAYER_XPOS - self.size/2)
            if 0 < dist < min_dist:
                min_dist = dist
                min_index = i
                is_bird = False
                
        # Then check birds
        for i, bird in enumerate(birds):
            dist = bird.pos_x + bird.w/2 - (PLAYER_XPOS - self.size/2)
            if 0 < dist < min_dist:
                min_dist = dist
                min_index = i
                is_bird = True
        
        # Set vision inputs with normalized values
        self.vision[4] = speed / 100.0  # Normalize speed
        self.vision[5] = self.pos_y / 200.0  # Normalize position
        
        if min_index == -1:  # No obstacles ahead
            self.vision[0:4] = [0.0] * 4
            self.vision[6] = 0.0
        else:
            self.vision[0] = 1.0/(min_dist/10.0)  # Distance to obstacle
            if is_bird:
                bird = birds[min_index]
                self.vision[1] = bird.h / 100.0  # Normalize height
                self.vision[2] = bird.w / 100.0  # Normalize width
                self.vision[3] = bird.pos_y / 200.0 if bird.type_of_bird != 0 else 0
            else:
                obstacle = obstacles[min_index]
                self.vision[1] = obstacle.h / 100.0  # Normalize height
                self.vision[2] = obstacle.w / 100.0  # Normalize width
                self.vision[3] = 0.0

            # Calculate gap to next obstacle
            next_min_dist = 10000
            for obstacle in obstacles:
                dist = obstacle.pos_x + obstacle.w/2 - (PLAYER_XPOS - self.size/2)
                if min_dist < dist < next_min_dist:
                    next_min_dist = dist
                    
            for bird in birds:
                dist = bird.pos_x + bird.w/2 - (PLAYER_XPOS - self.size/2)
                if min_dist < dist < next_min_dist:
                    next_min_dist = dist

            if next_min_dist == 10000:  # No second obstacle
                self.vision[6] = 0
            else:
                self.vision[6] = 1/(next_min_dist - min_dist)

    def show(self, screen, images):
        """Draw the player"""
        # Calculate ground position
        ground_y = screen.get_height() - GROUND_HEIGHT
        
        # Select correct image based on state
        if self.duck and self.pos_y == 0:
            image = images["dino_duck"] if self.run_count < 0 else images["dino_duck1"]
        elif self.pos_y == 0:
            image = images["dino_run1"] if self.run_count < 0 else images["dino_run2"]
        else:
            image = images["dino_jump"]

        # Calculate draw position
        draw_x = PLAYER_XPOS - image.get_width()/2
        draw_y = ground_y - (self.pos_y + image.get_height())
        
        # Draw the player
        screen.blit(image, (draw_x, draw_y))
        
        self.run_count += 1
        if self.run_count > 5:
            self.run_count = -5

    def reset(self):
        """Reset player state"""
        self.pos_y = 0
        self.vel_y = 0
        self.gravity = 1.2
        self.vision = [0.0] * 7  # Reset vision array with proper size
        self.decision = [0.0] * 3  # Reset decision array with proper size
        self.score = 0
        self.fitness = 0
        self.dead = False
        self.duck = False
        self.run_count = -5
        self.vision_history = []
        self.decision_history = []
