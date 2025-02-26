import pygame
from constants import GROUND_HEIGHT

class Obstacle:
    def __init__(self, type_num, width, obstacle_images):
        self.pos_x = width
        self.type = type_num
        
        if type_num == 0:    # small cactus
            self.w = 40
            self.h = 80
            self.image = obstacle_images["small_cactus"]
        elif type_num == 1:  # big cactus
            self.w = 60
            self.h = 120
            self.image = obstacle_images["big_cactus"]
        else:               # many small cacti
            self.w = 120
            self.h = 80
            self.image = obstacle_images["many_small_cactus"]

    def show(self, screen, ground_height):
        # Calculate ground position
        ground_y = screen.get_height() - ground_height
        
        # Calculate draw position
        draw_y = ground_y - self.image.get_height()
        
        # Draw obstacle
        screen.blit(self.image, (self.pos_x - self.image.get_width()/2, draw_y))

    def move(self, speed):
        self.pos_x -= speed

    def collided(self, player_x, player_y, player_width, player_height):
        player_left = player_x - player_width/2
        player_right = player_x + player_width/2
        this_left = self.pos_x - self.w/2
        this_right = self.pos_x + self.w/2

        if ((player_left <= this_right and player_right >= this_left) or 
            (this_left <= player_right and this_right >= player_left)):
            
            player_down = player_y - player_height/2
            if player_down <= self.h:
                return True
        return False
