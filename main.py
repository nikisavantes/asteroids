# main.py

import pygame
import sys
from constants import SCREEN_HEIGHT, SCREEN_WIDTH, PLAYER_RADIUS, PLAYER_TURN_SPEED
from logger import log_state, log_event
from circleshape import *
from player import Player
from asteroidfield import AsteroidField
from asteroid import *
from shot import Shot


def main():
    pygame.init()
    clock = pygame.time.Clock()
    dt = 0
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    font = pygame.font.Font(None, 36)
    score = 0
    survival_timer = 0.0  # telt seconden op om 1 punt per 10s te geven
    print("Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    Player.containers = (updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = (updatable,)
    asteroid_field = AsteroidField(asteroids)
    Shot.containers = (shots, updatable, drawable)
    x = SCREEN_WIDTH / 2
    y = SCREEN_HEIGHT / 2
    player = Player(x, y, PLAYER_RADIUS)

    while True:
        log_state()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        screen.fill("black")
        updatable.update(dt)
        # 1 punt per 10 seconden overleven
        survival_timer += dt
        while survival_timer >= 10.0:
            score += 1
            survival_timer -= 10.0

        # 100 punten per afgerond level
        if asteroid_field.level_completed:
            score += 100

        for thing in asteroids:
            if thing.collides_with(player):
                log_event("player_hit")
                print("Game over!")
                sys.exit()
        for thing in asteroids:
            for shot in shots:
                if thing.collides_with(shot):
                    log_event("asteroid_shot")
                    shot.kill()
                    # score op basis van radius (voor split!)
                    r = thing.radius
                    if r <= ASTEROID_MIN_RADIUS:
                        score += 10          # klein
                    elif r <= ASTEROID_MIN_RADIUS * 2:
                        score += 5           # middel
                    else:
                        score += 2           # groot
                    thing.split()
        for thing in drawable:
            thing.draw(screen)
        level_surf = font.render(f"Level: {asteroid_field.level}", True, "white")
        score_surf = font.render(f"Score: {score}", True, "white")
        screen.blit(level_surf, (10, 10))
        screen.blit(score_surf, (SCREEN_WIDTH - score_surf.get_width() - 10, 10))
        pygame.display.flip()
        # clock.tick(60)
        dt = clock.tick(60) / 1000
        # print(dt)


if __name__ == "__main__":
    main()
