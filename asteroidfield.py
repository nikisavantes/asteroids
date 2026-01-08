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
    # edges = [
    #     [pygame.Vector2(1, 0),  lambda y: pygame.Vector2(-ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT)],
    #    [pygame.Vector2(-1, 0), lambda y: pygame.Vector2(SCREEN_WIDTH + (ASTEROID_MAX_RADIUS), y * SCREEN_HEIGHT)],
    #    [pygame.Vector2(0, 1),  lambda x: pygame.Vector2(x * SCREEN_WIDTH, -ASTEROID_MAX_RADIUS)],
    #    [pygame.Vector2(0, -1), lambda x: pygame.Vector2(x * SCREEN_WIDTH, SCREEN_HEIGHT + (ASTEROID_MAX_RADIUS))],
    # ]

    def __init__(self, asteroid_group, base_speed_min=40, base_speed_max=100):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.asteroids = asteroid_group
 
        self.level = 1
        self.started = False
        self.level_completed = False
        self.completed_level = None
        self.intermission_timer = 0.0
        self.intermission_duration = 2.0
        self.waiting_for_next_level = False

        # Speed scaling per level
        self.speed_step = ASTEROID_SPEED_STEP
  
        self.base_speed_min = base_speed_min
        self.base_speed_max = base_speed_max

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

        speed_mult = 1.0 + self.speed_step * (level -1)

        # Spawn: big/med/small met vaste radii
        for _ in range(config["big"]):
            self.spawn(ASTEROID_MAX_RADIUS, speed_mult)
        for _ in range(config["med"]):
            self.spawn(ASTEROID_MIN_RADIUS * 2, speed_mult)
        for _ in range(config["small"]):
            self.spawn(ASTEROID_MIN_RADIUS, speed_mult)

    def spawn(self, radius, speed_mult):
        direction, pos_fn = random.choice([
            (pygame.Vector2(1, 0),  lambda y: pygame.Vector2(-radius, y * SCREEN_HEIGHT)),
            (pygame.Vector2(-1, 0), lambda y: pygame.Vector2(SCREEN_WIDTH + radius, y * SCREEN_HEIGHT)),
            (pygame.Vector2(0, 1),  lambda x: pygame.Vector2(x * SCREEN_WIDTH, -radius)),
            (pygame.Vector2(0, -1), lambda x: pygame.Vector2(x * SCREEN_WIDTH, SCREEN_HEIGHT + radius)),
        ])

        speed = random.randint(self.base_speed_min, self.base_speed_max) * speed_mult
        velocity = direction * speed
        velocity = velocity.rotate(random.randint(-30, 30))

        position = pos_fn(random.uniform(0, 1))

        asteroid = Asteroid(position.x, position.y, radius)
        asteroid.velocity = velocity
