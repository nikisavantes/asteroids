# main.py
import traceback
import pygame
import sys

from constants import SCREEN_HEIGHT, SCREEN_WIDTH, PLAYER_RADIUS
from logger import log_state, log_event
from player import Player
from asteroidfield import AsteroidField
from asteroid import Asteroid
from shot import Shot
from constants import ASTEROID_MIN_RADIUS


def game_loop():
    pygame.init()
    clock = pygame.time.Clock()
    dt = 0.0

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    font = pygame.font.Font(None, 36)

    print("Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")

    # groups
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()

    # containers (auto-add via CircleShape)
    Player.containers = (updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    Shot.containers = (shots, updatable, drawable)
    AsteroidField.containers = (updatable,)

    # objects
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, PLAYER_RADIUS)
    asteroid_field = AsteroidField(asteroids)

    # score / ui state
    score = 0
    survival_timer = 0.0  # 1 punt per 10s
    overlay_timer = 0.0
    overlay_level = None

    lives = 3
    last_level_seen = asteroid_field.level

    respawn_invuln = 0.0  # seconden

    while True:
        log_state()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        screen.fill("black")

        # update all sprites (Player + AsteroidField + Asteroids + Shots)
        updatable.update(dt)

        # detecteer nieuw level start: speler terug centraal
        if asteroid_field.level != last_level_seen:
            last_level_seen = asteroid_field.level
            player.position = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            player.rotation = 0
            # geen invuln nodig voor level-start, maar kan geen kwaad:
            respawn_invuln = max(respawn_invuln, 0.0)

        # invulnerability aftellen
        if respawn_invuln > 0:
            player.color = "green"
            respawn_invuln -= dt
            if respawn_invuln < 0:
                respawn_invuln = 0
        else:
            player.color = "white"

        # survival score: 1 punt per 10 seconden
        survival_timer += dt
        while survival_timer >= 10.0:
            score += 1
            survival_timer -= 10.0

        # level completion bonus + overlay trigger
        if asteroid_field.level_completed:
            score += 100
            overlay_timer = 2.0
            overlay_level = asteroid_field.completed_level

            # speler terug centraal bij level completion (optioneel maar ok)
            player.position = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            player.rotation = 0

        # overlay timer
        if overlay_timer > 0:
            overlay_timer -= dt
            if overlay_timer <= 0:
                overlay_timer = 0
                overlay_level = None

        # player hit detection (met 2s invulnerability na hit)
        for a in asteroids:
            if respawn_invuln <= 0 and a.collides_with(player):
                log_event("player_hit")
                lives -= 1

                if lives <= 0:
                    print("Game over!")
                    sys.exit()

                # respawn centraal + 2s invuln
                player.position = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                player.rotation = 0
                respawn_invuln = 2.0
                break  # max 1 leven per frame

        # asteroid-shot collisions + score
        for a in asteroids:
            for s in shots:
                if a.collides_with(s):
                    log_event("asteroid_shot")
                    s.kill()

                    r = a.radius
                    if r <= ASTEROID_MIN_RADIUS:
                        score += 10
                    elif r <= ASTEROID_MIN_RADIUS * 2:
                        score += 5
                    else:
                        score += 2

                    a.split()

        # draw sprites
        for thing in drawable:
            thing.draw(screen)

        # top overlay
        level_surf = font.render(f"Level: {asteroid_field.level}", True, "white")
        score_surf = font.render(f"Score: {score}", True, "white")
        screen.blit(level_surf, (10, 10))
        screen.blit(score_surf, (SCREEN_WIDTH - score_surf.get_width() - 10, 10))

        # lives bottom-left
        lives_surf = font.render(f"Lives: {lives}", True, "white")
        screen.blit(lives_surf, (10, SCREEN_HEIGHT - lives_surf.get_height() - 10))

        # level complete overlay (center)
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
        dt = clock.tick(60) / 1000.0


def main():
    try:
        game_loop()
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        pygame.time.wait(3000)
        raise


if __name__ == "__main__":
    main()
