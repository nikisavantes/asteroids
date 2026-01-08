# start.py
import pygame
from main import game_loop

DIFFICULTIES = [
    ("Easy", 40, 100),
    ("Normal", 50, 125),
    ("Hard-core", 60, 200),
]

WIDTH, HEIGHT = 1360, 670

def run_menu():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Asteroids - Choose Difficulty")

    title_font = pygame.font.Font(None, 64)
    font = pygame.font.Font(None, 40)
    small = pygame.font.Font(None, 28)

    selected = 0  # default = Easy
    clock = pygame.time.Clock()

    def make_button_rect(i):
        btn_w, btn_h = 460, 60
        x = (WIDTH - btn_w) // 2
        y0 = 160
        y = y0 + i * (btn_h + 18)
        return pygame.Rect(x, y, btn_w, btn_h)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return None

                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(DIFFICULTIES)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(DIFFICULTIES)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    running = False

            if event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                for i in range(len(DIFFICULTIES)):
                    if make_button_rect(i).collidepoint(mx, my):
                        selected = i

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i in range(len(DIFFICULTIES)):
                    if make_button_rect(i).collidepoint(mx, my):
                        selected = i
                        running = False
                        break

        # draw
        screen.fill("black")

        title = title_font.render("Choose difficulty", True, "white")
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 80)))

        hint = small.render("ENTER to select - ESC to quit", True, "white")
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, 125)))

        for i, (name, mn, mx) in enumerate(DIFFICULTIES):
            rect = make_button_rect(i)

            is_selected = (i == selected)
            if is_selected:
                # inverted colors
                pygame.draw.rect(screen, "white", rect, 0)
                pygame.draw.rect(screen, "white", rect, 3)
                text_color = "black"
            else:
                pygame.draw.rect(screen, "white", rect, 2)
                text_color = "white"

            label = f"{name}"
            txt = font.render(label, True, text_color)
            screen.blit(txt, txt.get_rect(center=rect.center))

        pygame.display.flip()
        clock.tick(60)

    choice = DIFFICULTIES[selected]
    pygame.quit()
    return choice  # (name, mn, mx)


if __name__ == "__main__":
    choice = run_menu()
    if choice is None:
        raise SystemExit

    _, mn, mx = choice
    game_loop(base_speed_min=mn, base_speed_max=mx)