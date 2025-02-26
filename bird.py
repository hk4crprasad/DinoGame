import pygame

class Bird:
    def __init__(self, type_of_bird, width, bird_img, bird_img2):
        self.w = 60
        self.h = 50
        self.pos_x = width
        self.type_of_bird = type_of_bird
        self.flap_count = 0
        
        # Load bird images
        self.bird = bird_img
        self.bird1 = bird_img2
        
        # Set vertical position based on type
        if type_of_bird == 0:    # flying low
            self.pos_y = 10 + self.h/2
        elif type_of_bird == 1:  # flying middle
            self.pos_y = 100
        else:                    # flying high
            self.pos_y = 180

    def show(self, screen, ground_height):
        self.flap_count += 1
        
        # Calculate position for drawing
        draw_y = screen.get_height() - ground_height - (self.pos_y + self.bird.get_height() - 20)
        
        # Flap animation
        if self.flap_count < 0:
            screen.blit(self.bird, (self.pos_x - self.bird.get_width()/2, draw_y))
        else:
            screen.blit(self.bird1, (self.pos_x - self.bird1.get_width()/2, draw_y))
            
        if self.flap_count > 15:
            self.flap_count = -15

    def move(self, speed):
        self.pos_x -= speed

    def collided(self, player_x, player_y, player_width, player_height):
        player_left = player_x - player_width/2
        player_right = player_x + player_width/2
        this_left = self.pos_x - self.w/2
        this_right = self.pos_x + self.w/2

        if ((player_left <= this_right and player_right >= this_left) or 
            (this_left <= player_right and this_right >= player_left)):
            
            player_up = player_y + player_height/2
            player_down = player_y - player_height/2
            this_up = self.pos_y + self.h/2
            this_down = self.pos_y - self.h/2
            
            if player_down <= this_up and player_up >= this_down:
                return True
        return False
