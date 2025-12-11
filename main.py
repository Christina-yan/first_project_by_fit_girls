import pygame
import sys
import random
import math

# Импортируем игры как модули
from games import Game_2048, sort_water, para, flappy_bird

# --- НАСТРОЙКИ И ИНИЦИАЛИЗАЦИЯ ---
WIDTH, HEIGHT = 800, 600

# --- ПАЛИТРА ---
COLORS = {
    "bg_top": (10, 15, 30),
    "bg_bottom": (45, 55, 85),
    "snow": (240, 245, 255),
    "gold": (255, 215, 0),
    "text_main": (255, 255, 255),
    "btn_base": (160, 40, 40),
    "btn_hover": (200, 60, 60),
    "btn_border": (255, 200, 100),
    "shadow": (0, 0, 0, 100),
}


def get_font(size, bold=False):
    try:
        return pygame.font.SysFont("georgia, arial", size, bold=bold)
    except:
        return pygame.font.Font(None, size)


class SnowFlake:
    def __init__(self):
        self.reset(random_y=True)

    def reset(self, random_y=False):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT) if random_y else -10
        self.size = random.randint(2, 5)
        self.speed = random.uniform(1, 3)
        self.alpha = random.randint(100, 255)
        self.wobble = random.uniform(0, 6.28)

    def update(self):
        self.y += self.speed
        self.x += math.sin(self.wobble) * 0.5
        self.wobble += 0.05
        if self.y > HEIGHT:
            self.reset()

    def draw(self, surface):
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(
            s,
            (*COLORS["snow"], self.alpha),
            (self.size // 2, self.size // 2),
            self.size // 2,
        )
        surface.blit(s, (self.x, self.y))


class Garland:
    def __init__(self):
        self.bulbs = []
        colors = [(255, 60, 60), (60, 255, 60), (60, 100, 255), (255, 220, 50)]
        for i in range(25):
            x = (WIDTH / 24) * i
            y = 30 + math.sin(i * 0.5) * 15
            self.bulbs.append(
                {
                    "x": x,
                    "y": y,
                    "color": colors[i % 4],
                    "phase": random.uniform(0, 6.28),
                }
            )

    def draw(self, surface):
        points = [(b["x"], b["y"] - 5) for b in self.bulbs]
        if len(points) > 1:
            pygame.draw.lines(surface, (50, 50, 50), False, points, 3)

        t = pygame.time.get_ticks()
        for b in self.bulbs:
            intensity = (math.sin(t * 0.005 + b["phase"]) + 1) / 2
            glow = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*b["color"], int(50 * intensity)), (10, 10), 10)
            surface.blit(glow, (b["x"] - 10, b["y"] - 5))
            pygame.draw.circle(surface, b["color"], (b["x"], b["y"] + 5), 5)
            pygame.draw.circle(surface, (255, 255, 255), (b["x"] - 2, b["y"] + 3), 2)


class MenuButton:
    def __init__(self, text, rect, game_func):
        self.text = text
        self.rect = rect
        self.game_func = game_func  # Теперь это функция, а не файл
        self.hovered = False
        self.anim_offset = 0

    def draw(self, surface, font):
        target_offset = -4 if self.hovered else 0
        self.anim_offset += (target_offset - self.anim_offset) * 0.2

        bg_col = COLORS["btn_hover"] if self.hovered else COLORS["btn_base"]
        border_col = COLORS["gold"] if self.hovered else COLORS["btn_border"]

        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        s_surf = pygame.Surface((shadow_rect.w, shadow_rect.h), pygame.SRCALPHA)
        pygame.draw.rect(
            s_surf,
            COLORS["shadow"],
            (0, 0, shadow_rect.w, shadow_rect.h),
            border_radius=15,
        )
        surface.blit(s_surf, shadow_rect)

        draw_rect = self.rect.copy()
        draw_rect.y += self.anim_offset

        pygame.draw.rect(surface, bg_col, draw_rect, border_radius=15)
        pygame.draw.rect(surface, border_col, draw_rect, 3, border_radius=15)

        txt_surf = font.render(self.text, True, COLORS["text_main"])
        txt_rect = txt_surf.get_rect(center=draw_rect.center)
        surface.blit(txt_surf, txt_rect)

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered


def init_menu():
    """Инициализация/реинициализация меню после возврата из игры"""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("🎄 Новогодний сборник игр 🎄")
    clock = pygame.time.Clock()

    font_title = get_font(60, True)
    font_btn = get_font(36, True)
    font_footer = get_font(20)

    return screen, clock, font_title, font_btn, font_footer


def main_menu():
    screen, clock, font_title, font_btn, font_footer = init_menu()

    # Кнопки с функциями игр
    buttons_data = [
        ("2048", Game_2048.run),
        ("Santa's Ride", flappy_bird.run),
        ("Pairs", para.run),
        ("Sort Water", sort_water.run),
    ]

    menu_buttons = []
    start_y = 200
    gap = 80
    for i, (text, func) in enumerate(buttons_data):
        rect = pygame.Rect(0, 0, 360, 65)
        rect.centerx = WIDTH // 2
        rect.y = start_y + i * gap
        menu_buttons.append(MenuButton(text, rect, func))

    snow_system = [SnowFlake() for _ in range(100)]
    garland = Garland()

    running = True
    while running:
        # Градиентный фон
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = COLORS["bg_top"][0] * (1 - ratio) + COLORS["bg_bottom"][0] * ratio
            g = COLORS["bg_top"][1] * (1 - ratio) + COLORS["bg_bottom"][1] * ratio
            b = COLORS["bg_top"][2] * (1 - ratio) + COLORS["bg_bottom"][2] * ratio
            pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

        # Декор
        for flake in snow_system:
            flake.update()
            flake.draw(screen)
        garland.draw(screen)

        # Заголовок
        title_text = "Christmas minigames"
        offset_y = math.sin(pygame.time.get_ticks() * 0.002) * 5
        t_shadow = font_title.render(title_text, True, (0, 0, 0))
        t_main = font_title.render(title_text, True, COLORS["gold"])
        title_rect = t_main.get_rect(center=(WIDTH // 2, 100 + offset_y))
        screen.blit(t_shadow, (title_rect.x + 4, title_rect.y + 4))
        screen.blit(t_main, title_rect)

        # События
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for btn in menu_buttons:
                    if btn.check_hover(event.pos):
                        # pygame.quit()  # Закрываем меню
                        btn.game_func()  # Запускаем игру
                        # После выхода из игры — снова открываем меню
                        screen = pygame.display.set_mode((WIDTH, HEIGHT))
                        screen, clock, font_title, font_btn, font_footer = init_menu()
                        snow_system = [SnowFlake() for _ in range(100)]
                        garland = Garland()

        # Кнопки
        for btn in menu_buttons:
            btn.check_hover(mouse_pos)
            btn.draw(screen, font_btn)

        # Футер
        ft = font_footer.render(
            "Select a game to start playing | ESC - exit", True, (150, 160, 180)
        )
        screen.blit(ft, ft.get_rect(center=(WIDTH // 2, HEIGHT - 30)))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main_menu()
