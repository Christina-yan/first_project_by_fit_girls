import pygame
import sys
import random
import math
import os

# Импортируем игры как модули
from games import Game_2048, sort_water, para, flappy_bird


def resource_path(relative_path):
    """Ищем ресурсы рядом со скриптом или рядом с exe"""
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        path = os.path.join(exe_dir, "games", relative_path)
        if os.path.exists(path):
            return path
        path = os.path.join(exe_dir, relative_path)
        if os.path.exists(path):
            return path
        try:
            path = os.path.join(sys._MEIPASS, relative_path)
            if os.path.exists(path):
                return path
        except AttributeError:
            pass
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, relative_path)


SOUNDS_DIR = resource_path("sounds-for-menu")

# --- НАСТРОЙКИ ---
WIDTH, HEIGHT = 850, 700

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

# ╔══════════════════════════════════════════════════════════════╗
# ║           ТАЙМИНГИ ПОЯВЛЕНИЯ ЭЛЕМЕНТОВ (мс)                  ║
# ║  Формат: (начало_появления, конец_появления)                 ║
# ╚══════════════════════════════════════════════════════════════╝
FADE_TIMINGS = {
    "snow": (600, 2000),  # 0.6 - 2 сек
    "garland": (2000, 3300),  # 1 - 3.3 сек
    "title": (3700, 4700),  # 3.7 - 4.7 сек
    "credits": (5000, 5500),  # 5.0 - 5.5 сек (Made by Fit girls)
    "buttons": (6700, 7900),  # 6.7 - 7.9 сек
    "footer": (7900, 8000),  # 7.9 - 8.0 сек
}

INTRO_DURATION = 8000  # 8 секунд - длительность интро музыки

# --- АУДИО ---
SOUNDS = {}
MUSIC_PATHS = {}
_music_initialized = False
_intro_played = False
_current_track = "none"


def calculate_alpha(start_time, element_name, current_time):
    """Вычисляет альфу (0-255) для элемента на основе времени"""
    timing = FADE_TIMINGS.get(element_name, (0, 1000))
    fade_start, fade_end = timing

    elapsed = current_time - start_time

    if elapsed < fade_start:
        return 0
    elif elapsed >= fade_end:
        return 255
    else:
        # Плавная интерполяция (ease-out для более приятного эффекта)
        progress = (elapsed - fade_start) / (fade_end - fade_start)
        # Ease-out quad: прогресс ускоряется к концу
        eased = 1 - (1 - progress) ** 2
        return int(255 * eased)


def is_intro_finished(start_time, current_time):
    """Проверяет, закончилось ли интро"""
    return (current_time - start_time) >= INTRO_DURATION


def apply_surface_alpha(surface, alpha):
    """Создает копию поверхности с примененной альфой"""
    result = surface.copy()
    result.set_alpha(alpha)
    return result


def load_sounds_and_music():
    global _music_initialized, MUSIC_PATHS, SOUNDS

    if _music_initialized:
        return

    files_sfx = ["menu.wav", "menu.mp3"]
    for filename in files_sfx:
        path = os.path.join(SOUNDS_DIR, filename)
        if os.path.exists(path):
            try:
                SOUNDS["menu"] = pygame.mixer.Sound(path)
                SOUNDS["menu"].set_volume(0.3)
                break
            except Exception as e:
                print(f"Ошибка sfx: {e}")

    files_music = {
        "intro": ["intro.wav", "intro.mp3", "intro.m4a", "intro.ogg"],
        "loop": ["loop.wav", "loop.mp3", "loop.m4a", "loop.ogg"],
    }

    for name, filenames in files_music.items():
        for filename in filenames:
            path = os.path.join(SOUNDS_DIR, filename)
            if os.path.exists(path):
                MUSIC_PATHS[name] = path
                print(f"Музыка найдена [{name}]: {filename}")
                break

    _music_initialized = True


def start_global_music():
    global _intro_played, _current_track

    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init()
        except:
            pass

    if pygame.mixer.music.get_busy():
        return

    if "intro" in MUSIC_PATHS and not _intro_played:
        print("▶ Запуск: INTRO + очередь LOOP")
        pygame.mixer.music.load(MUSIC_PATHS["intro"])
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play()

        if "loop" in MUSIC_PATHS:
            pygame.mixer.music.queue(MUSIC_PATHS["loop"])

        _intro_played = True
        _current_track = "intro"

    elif "loop" in MUSIC_PATHS:
        print("▶ Запуск: LOOP (бесконечно)")
        pygame.mixer.music.load(MUSIC_PATHS["loop"])
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        _current_track = "loop"


def check_music_loop():
    global _current_track

    if _intro_played and "loop" in MUSIC_PATHS:
        if not pygame.mixer.music.get_busy():
            print("↺ Перезапуск LOOP (бесконечно)")
            pygame.mixer.music.load(MUSIC_PATHS["loop"])
            pygame.mixer.music.play(-1)
            _current_track = "loop"


def ensure_infinite_loop():
    global _current_track

    if _current_track == "loop":
        return


def play_sfx(name):
    if name in SOUNDS:
        SOUNDS[name].play()


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

    def draw(self, surface, global_alpha=255):
        if global_alpha <= 0:
            return
        # Комбинируем локальную и глобальную альфу
        final_alpha = int(self.alpha * (global_alpha / 255))
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(
            s,
            (*COLORS["snow"], final_alpha),
            (self.size // 2, self.size // 2),
            self.size // 2,  # Было self.size, нужно self.size // 2
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

    def draw(self, surface, global_alpha=255):
        if global_alpha <= 0:
            return

        # Создаем отдельную поверхность для гирлянды
        garland_surf = pygame.Surface((WIDTH, 100), pygame.SRCALPHA)

        # Провод
        points = [(b["x"], b["y"] - 5) for b in self.bulbs]
        if len(points) > 1:
            pygame.draw.lines(
                garland_surf, (50, 50, 50, global_alpha), False, points, 3
            )

        t = pygame.time.get_ticks()
        for b in self.bulbs:
            intensity = (math.sin(t * 0.005 + b["phase"]) + 1) / 2

            # Свечение
            glow_alpha = int(50 * intensity * (global_alpha / 255))
            glow = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*b["color"], glow_alpha), (10, 10), 10)
            garland_surf.blit(glow, (b["x"] - 10, b["y"] - 5))

            # Лампочка
            pygame.draw.circle(
                garland_surf,
                (*b["color"], global_alpha),
                (int(b["x"]), int(b["y"]) + 5),
                5,
            )
            # Блик
            pygame.draw.circle(
                garland_surf,
                (255, 255, 255, global_alpha),
                (int(b["x"]) - 2, int(b["y"]) + 3),
                2,
            )

        surface.blit(garland_surf, (0, 0))


class MenuButton:
    def __init__(self, text, rect, game_func):
        self.text = text
        self.rect = rect
        self.game_func = game_func
        self.hovered = False
        self.anim_offset = 0

    def draw(self, surface, font, alpha=255):
        if alpha <= 0:
            return

        target_offset = -4 if self.hovered else 0
        self.anim_offset += (target_offset - self.anim_offset) * 0.2

        bg_col = COLORS["btn_hover"] if self.hovered else COLORS["btn_base"]
        border_col = COLORS["gold"] if self.hovered else COLORS["btn_border"]

        # Создаем поверхность для кнопки
        btn_surf = pygame.Surface((self.rect.w + 10, self.rect.h + 15), pygame.SRCALPHA)

        # Тень
        shadow_alpha = int(100 * (alpha / 255))
        shadow_rect = pygame.Rect(5, 9, self.rect.w, self.rect.h)
        pygame.draw.rect(
            btn_surf, (0, 0, 0, shadow_alpha), shadow_rect, border_radius=15
        )

        # Основная кнопка
        draw_rect = pygame.Rect(5, 5 + self.anim_offset, self.rect.w, self.rect.h)
        pygame.draw.rect(btn_surf, (*bg_col, alpha), draw_rect, border_radius=15)
        pygame.draw.rect(btn_surf, (*border_col, alpha), draw_rect, 3, border_radius=15)

        # Текст
        txt_surf = font.render(self.text, True, COLORS["text_main"])
        txt_surf.set_alpha(alpha)
        txt_rect = txt_surf.get_rect(center=draw_rect.center)
        btn_surf.blit(txt_surf, txt_rect)

        surface.blit(btn_surf, (self.rect.x - 5, self.rect.y - 5))

    def check_hover(self, pos, clickable=True):
        if clickable:
            self.hovered = self.rect.collidepoint(pos)
        else:
            self.hovered = False
        return self.hovered


def draw_gradient_background(surface):
    """Рисует градиентный фон"""
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(COLORS["bg_top"][0] * (1 - ratio) + COLORS["bg_bottom"][0] * ratio)
        g = int(COLORS["bg_top"][1] * (1 - ratio) + COLORS["bg_bottom"][1] * ratio)
        b = int(COLORS["bg_top"][2] * (1 - ratio) + COLORS["bg_bottom"][2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))


def draw_title(surface, font, alpha):
    """Рисует заголовок с альфой"""
    if alpha <= 0:
        return

    title_text = "Christmas minigames"
    offset_y = math.sin(pygame.time.get_ticks() * 0.002) * 5

    # Рендерим текст
    t_shadow = font.render(title_text, True, (0, 0, 0))
    t_main = font.render(title_text, True, COLORS["gold"])

    # Применяем альфу
    t_shadow.set_alpha(alpha)
    t_main.set_alpha(alpha)

    title_rect = t_main.get_rect(center=(WIDTH // 2, 100 + offset_y))
    surface.blit(t_shadow, (title_rect.x + 4, title_rect.y + 4))
    surface.blit(t_main, title_rect)


def draw_credits(surface, font, alpha):
    """Рисует 'Made by Fit girls' с альфой"""
    if alpha <= 0:
        return

    credits_text = "Made by Fit girls"
    offset_y = math.sin(pygame.time.get_ticks() * 0.002) * 5

    c_shadow = font.render(credits_text, True, (0, 0, 0))
    c_main = font.render(credits_text, True, COLORS["gold"])

    c_shadow.set_alpha(alpha)
    c_main.set_alpha(alpha)

    credits_rect = c_main.get_rect(center=(WIDTH // 2, HEIGHT - 70 + offset_y))
    surface.blit(c_shadow, (credits_rect.x + 2, credits_rect.y + 2))
    surface.blit(c_main, credits_rect)


def draw_footer(surface, font, alpha):
    """Рисует футер с альфой"""
    if alpha <= 0:
        return

    ft = font.render(
        "Select a game to start playing | ESC - exit", True, (150, 160, 180)
    )
    ft.set_alpha(alpha)
    surface.blit(ft, ft.get_rect(center=(WIDTH // 2, HEIGHT - 30)))


def init_menu():
    """Инициализация меню"""
    if not pygame.get_init():
        pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("🎄 Christmas games set 🎄")
    load_sounds_and_music()
    start_global_music()

    clock = pygame.time.Clock()
    font_title = get_font(60, True)
    font_btn = get_font(36, True)
    font_footer = get_font(20)
    font_credits = get_font(26, True)

    return screen, clock, font_title, font_btn, font_footer, font_credits


def main_menu():
    screen, clock, font_title, font_btn, font_footer, font_credits = init_menu()

    # ⏱️ Запоминаем время старта для анимации появления
    menu_start_time = pygame.time.get_ticks()
    is_first_launch = True  # Первый запуск = показываем анимацию

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
        current_time = pygame.time.get_ticks()

        # ═══════════════════════════════════════════════════════
        # 🎨 ВЫЧИСЛЯЕМ АЛЬФУ ДЛЯ КАЖДОГО ЭЛЕМЕНТА
        # ═══════════════════════════════════════════════════════
        if is_first_launch:
            alpha_snow = calculate_alpha(menu_start_time, "snow", current_time)
            alpha_garland = calculate_alpha(menu_start_time, "garland", current_time)
            alpha_title = calculate_alpha(menu_start_time, "title", current_time)
            alpha_credits = calculate_alpha(menu_start_time, "credits", current_time)
            alpha_buttons = calculate_alpha(menu_start_time, "buttons", current_time)
            alpha_footer = calculate_alpha(menu_start_time, "footer", current_time)

        else:
            # После возврата из игры - все сразу видно
            alpha_snow = 255
            alpha_garland = 255
            alpha_title = 255
            alpha_credits = 255
            alpha_buttons = 255
            alpha_footer = 255

        # Кнопки кликабельны только после окончания интро
        buttons_clickable = (
            is_intro_finished(menu_start_time, current_time) or not is_first_launch
        )

        # ═══════════════════════════════════════════════════════
        # 🖼️ ОТРИСОВКА
        # ═══════════════════════════════════════════════════════

        # 1. Градиентный фон (всегда виден)
        draw_gradient_background(screen)

        # 2. Снежинки
        for flake in snow_system:
            flake.update()
            flake.draw(screen, alpha_snow)

        # 3. Гирлянда
        garland.draw(screen, alpha_garland)

        # 4. Заголовок
        draw_title(screen, font_title, alpha_title)

        # 5. Credits ("Made by Fit girls")
        draw_credits(screen, font_credits, alpha_credits)

        # 6. Кнопки
        for btn in menu_buttons:
            btn.check_hover(pygame.mouse.get_pos(), buttons_clickable)
            btn.draw(screen, font_btn, alpha_buttons)

        # 7. Футер
        draw_footer(screen, font_footer, alpha_footer)

        # Проверка музыки
        check_music_loop()

        # ═══════════════════════════════════════════════════════
        # ⌨️ СОБЫТИЯ
        # ═══════════════════════════════════════════════════════
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Клик работает только если кнопки активны
                if buttons_clickable:
                    for btn in menu_buttons:
                        if btn.check_hover(event.pos, True):
                            play_sfx("menu")
                            ensure_infinite_loop()

                            # 🎮 Запускаем игру
                            btn.game_func()

                            # После выхода из игры - переинициализация
                            screen = pygame.display.set_mode((WIDTH, HEIGHT))
                            (
                                screen,
                                clock,
                                font_title,
                                font_btn,
                                font_footer,
                                font_credits,
                            ) = init_menu()
                            snow_system = [SnowFlake() for _ in range(100)]
                            garland = Garland()

                            # После возврата из игры анимация не нужна
                            is_first_launch = False
                            play_sfx("menu")

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main_menu()
