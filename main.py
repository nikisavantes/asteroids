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
    overlay_timer = 0.0 # for end of level message
    overlay_level = None
    last_scored_level = 0

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
        if overlay_timer > 0:
            overlay_timer -= dt
            if overlay_timer <= 0:
                overlay_timer = 0
                overlay_level = None

        # level completion bonus (eenmalig per level)
        if asteroid_field.level_completed:
            score += 100
            overlay_timer = 2.0
            overlay_level = asteroid_field.completed_level

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
        if overlay_timer > 0 and overlay_level is not None:
            big_font = pygame.font.Font(None, 72)
            small_font = pygame.font.Font(None, 36)

            text1 = big_font.render(
                f"Level {overlay_level} successfully completed!",
                True,
                "white",
            )
            text2 = small_font.render(
                "Score bonus +100",
                True,
                "white",
            )

            rect1 = text1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            rect2 = text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))

            screen.blit(text1, rect1)
            screen.blit(text2, rect2)

        pygame.display.flip()
        # clock.tick(60)
        dt = clock.tick(60) / 1000
        # print(dt)


if __name__ == "__main__":
    main()
