# asteroid.py
# attempting to have asteroids collide

import pygame
import random
from constants import *
from circleshape import CircleShape
from logger import log_event

def generate_rock_shape(radius, points=12, jitter=0.35):
        shape = []
        for i in range(points):
            angle = i * 360 / points
            r = radius * (1 + random.uniform(-jitter, jitter))
            v = pygame.Vector2(0, -r).rotate(angle)
            shape.append(v)
        return shape

class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.rotation = random.uniform(0, 360)
        self.spin = random.uniform(-40, 40)  # graden per seconde
        sides = random.randint(8, 12)
        self.shape = generate_rock_shape(radius, sides)

    def draw(self, screen):
        points = []
        for p in self.shape:
            rp = p.rotate(self.rotation)
            points.append(self.position + rp)
        pygame.draw.polygon(screen, "white", points, LINE_WIDTH)

    def update(self, dt):
        self.position += self.velocity * dt
        self.rotation += self.spin * dt
        margin = self.radius
        if self.position.x < -margin:
            self.position.x = SCREEN_WIDTH + margin
        elif self.position.x > SCREEN_WIDTH + margin:
            self.position.x = -margin
        if self.position.y < -margin:
            self.position.y = SCREEN_HEIGHT + margin
        elif self.position.y > SCREEN_HEIGHT + margin:
            self.position.y = -margin

    def split(self):
        self.kill()
        if self.radius <= ASTEROID_MIN_RADIUS:
            return

        log_event("asteroid_split")
        angle = random.uniform(20, 50)
        new_radius = self.radius - ASTEROID_MIN_RADIUS

        a1 = Asteroid(self.position.x, self.position.y, new_radius)
        a1.velocity = self.velocity.rotate(angle)

        a2 = Asteroid(self.position.x, self.position.y, new_radius)
        a2.velocity = self.velocity.rotate(-angle)
