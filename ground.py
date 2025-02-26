import random
import pygame
from constants import GROUND_HEIGHT

class Ground:
    def __init__(self, width, height):
        self.pos_x = width
        self.pos_y = height - GROUND_HEIGHT + random.randint(-20, 30)
        self.w = random.randint(1, 10)

    def show(self, screen):
        pygame.draw.line(screen, (0, 0, 0), 
                        (self.pos_x, self.pos_y),
                        (self.pos_x + self.w, self.pos_y),
                        3)

    def move(self, speed):
        self.pos_x -= speed
