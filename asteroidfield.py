# asteroidfield.py
import pygame
import random
from asteroid import Asteroid
from constants import *

LEVELS = [
    {"big": 3, "med": 0, "small": 0},  # 1
    {"big": 4, "med": 0, "small": 0},  # 2
    {"big": 4, "med": 2, "small": 0},  # 3
    {"big": 5, "med": 2, "small": 0},  # 4
    {"big": 5, "med": 3, "small": 0},  # 5
    {"big": 6, "med": 3, "small": 0},  # 6
    {"big": 6, "med": 3, "small": 2},  # 7
    {"big": 7, "med": 3, "small": 2},  # 8
    {"big": 7, "med": 4, "small": 2},  # 9
    {"big": 8, "med": 4, "small": 2},  # 10
]

class AsteroidField(pygame.sprite.Sprite):
    edges = [
        [pygame.Vector2(1, 0),  lambda y: pygame.Vector2(-ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT)],
        [pygame.Vector2(-1, 0), lambda y: pygame.Vector2(SCREEN_WIDTH + ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT)],
        [pygame.Vector2(0, 1),  lambda x: pygame.Vector2(x * SCREEN_WIDTH, -ASTEROID_MAX_RADIUS)],
        [pygame.Vector2(0, -1), lambda x: pygame.Vector2(x * SCREEN_WIDTH, SCREEN_HEIGHT + ASTEROID_MAX_RADIUS)],
    ]

    def __init__(self, asteroid_group):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.asteroids = asteroid_group
        self.speed_step = ASTEROID_SPEED_STEP

        self.level = 1
        self.started = False
        self.level_completed = False

        # Speed scaling per “set van 10 levels”
        self.speed_step = 0.20        # +20% per 10 levels (pas aan)
        self.base_speed_min = 40      # was random(40,100)
        self.base_speed_max = 100
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

        tier = (level - 1) // len(LEVELS)      # 0:1-10, 1:11-20, 2:21-30...
        speed_mult = 1.0 + tier * self.speed_step

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
