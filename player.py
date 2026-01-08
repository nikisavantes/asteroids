# player.py

import pygame
from constants import *
from circleshape import CircleShape
from shot import Shot

class Player(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.rotation = 0
        self.cooldown_timer = 0
        self.color = "white"

    # in the Player class
    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90)

        nose = self.position + forward * self.radius

        # staart: V/hoekig (roofvogel)
        tail_back = self.radius * 1.15
        tail_w = self.radius * 0.75
        tail_notch = self.radius * 0.55  # hoe diep de inkeping naar voren komt

        left_tail  = self.position - forward * tail_back - right * tail_w
        right_tail = self.position - forward * tail_back + right * tail_w
        tail_center = self.position - forward * (tail_back - tail_notch)  # notch punt

        # volgorde van punten is belangrijk (clockwise of counterclockwise)
        return [nose, right_tail, tail_center, left_tail]
    
    def draw(self, screen):
        pygame.draw.polygon(screen, self.color, self.triangle(), LINE_WIDTH)


    def rotate(self, dt):
        self.rotation += (PLAYER_TURN_SPEED * dt)
        # return self.rotation

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            self.rotate(-dt)
        if keys[pygame.K_d]:
            self.rotate(dt)
        if keys[pygame.K_z]:
            self.move(dt)
        if keys[pygame.K_s]:
            self.move(-dt)

        # cooldown beter altijd laten aflopen
        self.cooldown_timer = max(0, self.cooldown_timer - dt)
        if keys[pygame.K_SPACE]:
            self.shoot()

        self.wrap()

    def wrap(self):
        margin = self.radius
        if self.position.x < -margin:
            self.position.x = SCREEN_WIDTH + margin
        elif self.position.x > SCREEN_WIDTH + margin:
            self.position.x = -margin

        if self.position.y < -margin:
            self.position.y = SCREEN_HEIGHT + margin
        elif self.position.y > SCREEN_HEIGHT + margin:
            self.position.y = -margin

    def move(self, dt):
        unit_vector = pygame.Vector2(0, 1)
        rotated_vector = unit_vector.rotate(self.rotation)
        rotated_with_speed_vector = rotated_vector * PLAYER_SPEED * dt
        self.position += rotated_with_speed_vector

    def shoot(self):
        if self.cooldown_timer > 0:
            return
        self.cooldown_timer = PLAYER_SHOOT_COOLDOWN_SECONDS
        if hasattr(self, "laser_sound"):
            self.laser_sound.play()
        direction = pygame.Vector2(0, 1).rotate(self.rotation)
        shot = Shot(self.position.x, self.position.y, SHOT_RADIUS)
        shot.velocity = direction * PLAYER_SHOOT_SPEED
