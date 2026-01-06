# main.py
import traceback
import pygame
import sys

from constants import SCREEN_HEIGHT, SCREEN_WIDTH, PLAYER_RADIUS, ASTEROID_MIN_RADIUS
from logger import log_state, log_event
from player import Player
from asteroidfield import AsteroidField
from asteroid import Asteroid
from shot import Shot
import hiscores


def draw_centered_text(screen, text, font, y, color="white"):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(SCREEN_WIDTH // 2, y))
    screen.blit(surf, rect)


def draw_hiscore_table(screen, table_font, title_font, hiscore_list, highlight_idx=None, blink_on=False):
    draw_centered_text(screen, "HISCORES", title_font, SCREEN_HEIGHT // 2 - 140, "white")

    start_y = SCREEN_HEIGHT // 2 - 90
    line_h = 30

    for i, (ini, sc) in enumerate(hiscore_list):
        rank = i + 1
        line = f"{rank:2d}.  {ini}   {sc}"
        color = "white"
        if highlight_idx is not None and i == highlight_idx and blink_on:
            color = "red"

        surf = table_font.render(line, True, color)
        rect = surf.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * line_h))
        screen.blit(surf, rect)


def game_loop():
    pygame.init()
    clock = pygame.time.Clock()
    dt = 0.0

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    hud_font = pygame.font.Font(None, 36)

    big_font = pygame.font.Font(None, 72)
    mid_font = pygame.font.Font(None, 40)
    table_font = pygame.font.Font(None, 32)

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

    # gameplay state
    score = 0
    survival_timer = 0.0  # 1 punt per 10s

    overlay_timer = 0.0
    overlay_level = None

    lives = 3
    last_level_seen = asteroid_field.level
    respawn_invuln = 0.0  # seconden

    # ---- HISCORE STATE MACHINE ----
    mode = "PLAY"  # PLAY | HISCORE_CONGRATS | HISCORE_ENTRY | HISCORE_SHOW | GAME_OVER
    freeze_timer = 0.0

    hiscore_list = []
    entered_initials = ""
    new_entry_index = None
    blink_timer = 0.0
    show_timer = 0.0

    while True:
        log_state()

        # -------- EVENTS --------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:
                if mode == "HISCORE_ENTRY":
                    if event.key == pygame.K_BACKSPACE:
                        entered_initials = entered_initials[:-1]
                    elif event.key == pygame.K_RETURN:
                        if len(entered_initials) == 3:
                            hiscore_list = hiscores.add_hiscore(entered_initials, score, hiscore_list)
                            hiscores.save_hiscores(hiscore_list)

                            # index van nieuwe entry bepalen
                            new_entry_index = None
                            for i, (ini, sc) in enumerate(hiscore_list):
                                if ini == entered_initials.upper() and sc == score:
                                    new_entry_index = i
                                    break

                            mode = "HISCORE_SHOW"
                            show_timer = 5.0
                            blink_timer = 0.0
                    else:
                        ch = event.unicode.upper()
                        if ch.isalnum() and len(ch) == 1 and len(entered_initials) < 3:
                            entered_initials += ch

                elif mode in ("GAME_OVER", "HISCORE_SHOW"):
                    # optioneel: laat ESC meteen afsluiten
                    if event.key == pygame.K_ESCAPE:
                        return

        screen.fill("black")

        # -------- GAMEPLAY (alleen in PLAY) --------
        if mode == "PLAY":
            # ---------- UPDATE ----------
            updatable.update(dt)

            # nieuw level gestart → speler centraal
            if asteroid_field.level != last_level_seen:
                last_level_seen = asteroid_field.level
                player.position = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                player.rotation = 0

            # invulnerability timer
            if respawn_invuln > 0:
                respawn_invuln -= dt
                if respawn_invuln < 0:
                    respawn_invuln = 0

            player.color = "green" if respawn_invuln > 0 else "white"
            print("COLOR", player.color, "INVULN", respawn_invuln)


            # survival score: 1 punt per 10 seconden
            survival_timer += dt
            while survival_timer >= 10.0:
                score += 1
                survival_timer -= 10.0

            # level completion bonus
            if asteroid_field.level_completed:
                score += 100
                overlay_timer = 2.0
                overlay_level = asteroid_field.completed_level

                player.position = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                player.rotation = 0

            # overlay timer (level complete)
            if overlay_timer > 0:
                overlay_timer -= dt
                if overlay_timer <= 0:
                    overlay_timer = 0
                    overlay_level = None

            # ---------- PLAYER ↔ ASTEROID ----------
            for a in asteroids:
                if respawn_invuln <= 0 and a.collides_with(player):
                    log_event("player_hit")
                    lives -= 1

                    if lives <= 0:
                        hiscore_list = hiscores.load_hiscores()
                        if hiscores.qualifies(score, hiscore_list):
                            mode = "HISCORE_CONGRATS"
                            freeze_timer = 2.0
                        else:
                            mode = "GAME_OVER"
                    else:
                        # respawn + 2s invulnerability
                        player.position = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                        player.rotation = 0
                        respawn_invuln = 2.0
                        player.color = "green"
                        
                    break  # max 1 hit per frame

            # ---------- SHOT ↔ ASTEROID ----------
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

            # ---------- DRAW WORLD ----------
            invuln = respawn_invuln > 0

            for thing in drawable:
                thing.draw(screen)

            # ---------- HUD ----------
            level_surf = hud_font.render(f"Level: {asteroid_field.level}", True, "white")
            score_surf = hud_font.render(f"Score: {score}", True, "white")
            lives_surf = hud_font.render(f"Lives: {lives}", True, "white")

            screen.blit(level_surf, (10, 10))
            screen.blit(score_surf, (SCREEN_WIDTH - score_surf.get_width() - 10, 10))
            screen.blit(lives_surf, (10, SCREEN_HEIGHT - lives_surf.get_height() - 10))

            # level-complete overlay (tijdens PLAY)
            if overlay_timer > 0 and overlay_level is not None:
                small_font = pygame.font.Font(None, 36)
                text1 = big_font.render(
                    f"Level {overlay_level} successfully completed!", True, "white"
                )
                text2 = small_font.render("Score bonus +100", True, "white")

                rect1 = text1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
                rect2 = text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))

                screen.blit(text1, rect1)
                screen.blit(text2, rect2)
        # -------- HISCORE / END TIMERS (altijd, buiten PLAY) --------
        if mode == "HISCORE_CONGRATS":
            freeze_timer -= dt
            if freeze_timer <= 0:
                freeze_timer = 0
                mode = "HISCORE_ENTRY"
                entered_initials = ""

        elif mode == "HISCORE_SHOW":
            show_timer -= dt
            blink_timer += dt
            if show_timer <= 0:
                return

        # -------- HISCORE / END OVERLAYS --------
        if mode == "HISCORE_CONGRATS":
            draw_centered_text(screen, "Congratulations!", big_font, SCREEN_HEIGHT // 2 - 40, "white")
            draw_centered_text(screen, "You have a highscore!", mid_font, SCREEN_HEIGHT // 2 + 10, "white")

        elif mode == "HISCORE_ENTRY":
            draw_centered_text(screen, "NEW HISCORE", big_font, SCREEN_HEIGHT // 2 - 90, "white")
            draw_centered_text(screen, "Enter your initials (3 chars):", mid_font, SCREEN_HEIGHT // 2 - 20, "white")

            shown = entered_initials.ljust(3, "_")
            draw_centered_text(screen, shown, big_font, SCREEN_HEIGHT // 2 + 50, "white")
            draw_centered_text(screen, "Press ENTER to confirm", table_font, SCREEN_HEIGHT // 2 + 110, "white")

        elif mode == "HISCORE_SHOW":
            blink_on = (int(blink_timer * 2) % 2) == 0  # 2x per sec togglen
            draw_hiscore_table(screen, table_font, mid_font, hiscore_list, new_entry_index, blink_on)

        elif mode == "GAME_OVER":
            draw_centered_text(screen, "GAME OVER", big_font, SCREEN_HEIGHT // 2 - 20, "white")
            draw_centered_text(screen, "Press ESC to quit", mid_font, SCREEN_HEIGHT // 2 + 30, "white")

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
