# asteroidfield.py
import pygame
import random
from asteroid import Asteroid
from constants import *

LEVELS = [
    {"big": 4, "med": 2, "small": 1},  # 1
    {"big": 4, "med": 4, "small": 2},  # 2
    {"big": 5, "med": 2, "small": 3},  # 3
    {"big": 5, "med": 4, "small": 4},  # 4
    {"big": 6, "med": 3, "small": 5},  # 5
    {"big": 6, "med": 5, "small": 6},  # 6
    {"big": 7, "med": 3, "small": 7},  # 7
    {"big": 7, "med": 5, "small": 8},  # 8
    {"big": 8, "med": 4, "small": 9},  # 9
    {"big": 8, "med": 6, "small": 10},  # 10
]

class AsteroidField(pygame.sprite.Sprite):
    edges = [
        [pygame.Vector2(1, 0),  lambda y: pygame.Vector2(-ASTEROID_MAX_RADIUS/2, y * SCREEN_HEIGHT)],
        [pygame.Vector2(-1, 0), lambda y: pygame.Vector2(SCREEN_WIDTH + (ASTEROID_MAX_RADIUS/2), y * SCREEN_HEIGHT)],
        [pygame.Vector2(0, 1),  lambda x: pygame.Vector2(x * SCREEN_WIDTH, -ASTEROID_MAX_RADIUS/2)],
        [pygame.Vector2(0, -1), lambda x: pygame.Vector2(x * SCREEN_WIDTH, SCREEN_HEIGHT + (ASTEROID_MAX_RADIUS/2))],
    ]

    def __init__(self, asteroid_group):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.asteroids = asteroid_group
        self.speed_step = ASTEROID_SPEED_STEP

        self.level = 1
        self.started = False
        self.level_completed = False

        # Speed scaling per level
        self.speed_step = 0.50        # +50% snelheidswinst
        self.base_speed_min = 60      # was random(40,100)
        self.base_speed_max = 80
        self.level_completed = False
        self.completed_level = None
        self.intermission_timer = 0.0
        self.intermission_duration = 2.0
        self.waiting_for_next_level = False

    def update(self, dt):
        # default: geen nieuw completion event deze frame
        self.level_completed = False

        # start level 1
        if not self.started:
            self.start_level(self.level)
            self.started = True
            return

        # als we in intermission zitten: aftellen, nog NIET spawnen
        if self.waiting_for_next_level:
            self.intermission_timer -= dt
            if self.intermission_timer <= 0:
                self.waiting_for_next_level = False
                self.level += 1
                self.start_level(self.level)
            return

        # als alle asteroids op zijn: completion event + start intermission
        if len(self.asteroids) == 0:
            self.level_completed = True
            self.completed_level = self.level
            self.waiting_for_next_level = True
            self.intermission_timer = self.intermission_duration

    def start_level(self, level):
        config = LEVELS[(level - 1) % len(LEVELS)]

        # tier = (level - 1) // len(LEVELS)      # 0:1-10, 1:11-20, 2:21-30...
        # speed_mult = 1.0 + tier * self.speed_step
        speed_mult = 1.0 + self.speed_step

        # Spawn: big/med/small met vaste radii
        for _ in range(config["big"]):
            self.spawn(ASTEROID_MAX_RADIUS, speed_mult)
        for _ in range(config["med"]):
            self.spawn(ASTEROID_MIN_RADIUS * 2, speed_mult)
        for _ in range(config["small"]):
            self.spawn(ASTEROID_MIN_RADIUS, speed_mult)

    def spawn(self, radius, speed_mult):
        edge = random.choice(self.edges)

        speed = random.randint(self.base_speed_min, self.base_speed_max)
        speed = speed * speed_mult

        velocity = edge[0] * speed
        velocity = velocity.rotate(random.randint(-30, 30))
        position = edge[1](random.uniform(0, 1))

        asteroid = Asteroid(position.x, position.y, radius)
        asteroid.velocity = velocity
        # Geen .add nodig: Asteroid gaat via containers automatisch in groepen
