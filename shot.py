# shot.py

import pygame
from constants import *
from circleshape import CircleShape

class Shot(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        
    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.position, self.radius, LINE_WIDTH)

    def update(self, dt):
        self.position += (self.velocity * dt)
        self.position += (self.velocity * dt)

        margin = self.radius
        if (self.position.x < -margin or self.position.x > SCREEN_WIDTH + margin or
            self.position.y < -margin or self.position.y > SCREEN_HEIGHT + margin):
            self.kill()

