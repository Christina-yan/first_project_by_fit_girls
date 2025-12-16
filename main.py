import pygame
import sys
import random
import math
import os

# Импортируем игры как модули
from games import Game_2048, sort_water, para, flappy_bird


def resource_path(relative_path):
    """Ищем ресурсы рядом со скриптом или рядом с exe"""

    # 1. Если запущено как exe
    if getattr(sys, "frozen", False):
        # Сначала рядом с exe
        exe_dir = os.path.dirname(sys.executable)
        path = os.path.join(exe_dir, "games", relative_path)
        if os.path.exists(path):
            return path

        # Или просто рядом с exe
        path = os.path.join(exe_dir, relative_path)
        if os.path.exists(path):
            return path

        # Или в _MEIPASS
        try:
            path = os.path.join(sys._MEIPASS, relative_path)
            if os.path.exists(path):
                return path
        except AttributeError:
            pass

    # 2. Рядом со скриптом (обычный запуск)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, relative_path)


SOUNDS_DIR = resource_path("sounds-for-menu")
# Отладка — удалите потом
print(f"Ищу звуки в: {SOUNDS_DIR}")
print(f"Папка существует: {os.path.exists(SOUNDS_DIR)}")
if os.path.exists(SOUNDS_DIR):
    print(f"Файлы в папке: {os.listdir(SOUNDS_DIR)}")


# --- НАСТРОЙКИ И ИНИЦИАЛИЗАЦИЯ ---
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

# --- АУДИО ---
SOUNDS = {}
MUSIC_PATHS = {}  # Пути к музыкальным файлам
MUSIC_END_EVENT = pygame.USEREVENT + 1  # Кастомное событие
music_state = "none"  # Текущее состояние: "none", "intro", "loop"

# ===== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ МУЗЫКИ =====
_music_initialized = False  # Загружены ли пути
_intro_played = False  # Играло ли уже интро в этой сессии
_current_track = "none"  # Что сейчас должно играть: 'intro', 'loop', 'none'


def load_sounds_and_music():
    """Загружает звуки и находит пути к музыке один раз"""
    global _music_initialized, MUSIC_PATHS, SOUNDS

    if _music_initialized:
        return

    # 1. Загрузка SFX
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

    # 2. Поиск путей музыки
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
    """Умный запуск музыки: Intro -> (Queue Loop) -> Loop"""
    global _intro_played, _current_track

    # 1. Если микшер выключен (например, игра сделала pygame.quit), инициализируем его
    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init()
        except:
            pass

    # 2. Если музыка УЖЕ играет, ничего не трогаем (чтобы не было сброса при возврате в меню)
    if pygame.mixer.music.get_busy():
        return

    # 3. Логика выбора трека
    # Если интро есть и мы его еще не играли
    if "intro" in MUSIC_PATHS and not _intro_played:
        print("▶ Запуск: INTRO + очередь LOOP")
        pygame.mixer.music.load(MUSIC_PATHS["intro"])
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play()

        # МАГИЯ: Ставим Loop в очередь сразу же!
        # Когда Intro закончится, Pygame сам запустит Loop, даже если мы внутри игры 2048.
        if "loop" in MUSIC_PATHS:
            pygame.mixer.music.queue(MUSIC_PATHS["loop"])

        _intro_played = True
        _current_track = "intro"

    # Если интро уже было или его нет -> сразу Loop
    elif "loop" in MUSIC_PATHS:
        print("▶ Запуск: LOOP (бесконечно)")
        pygame.mixer.music.load(MUSIC_PATHS["loop"])
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)  # -1 = бесконечный повтор
        _current_track = "loop"


def check_music_loop():
    """
    Эту функцию нужно вызывать в цикле меню.
    Она проверяет, не закончилась ли 'очередь' и включает бесконечный повтор.
    """
    global _current_track

    # Если мы думаем, что играем Intro, но музыка играет (значит, возможно, уже перешло на Loop из очереди),
    # или музыка остановилась (очередь кончилась).
    # Но надежнее всего: если Intro уже сыграло, мы должны убедиться, что играет Loop в режиме бесконечности.

    if _intro_played and "loop" in MUSIC_PATHS:
        # Если музыка вообще затихла (например, Loop из очереди проиграл 1 раз и кончился)
        if not pygame.mixer.music.get_busy():
            print("↺ Перезапуск LOOP (бесконечно)")
            pygame.mixer.music.load(MUSIC_PATHS["loop"])
            pygame.mixer.music.play(-1)
            _current_track = "loop"


def ensure_infinite_loop():
    """
    Если сейчас играет Intro, принудительно включает Loop в бесконечном режиме.
    Это нужно вызывать перед запуском любой игры, чтобы музыка не заглохла.
    """
    global _current_track

    # Если мы уже в режиме loop, ничего делать не надо
    if _current_track == "loop":
        return

    # Если играет Intro (или вообще ничего), включаем Loop бесконечно
    if "loop" in MUSIC_PATHS:
        print("⚡ Принудительный переход на LOOP перед игрой")
        pygame.mixer.music.load(MUSIC_PATHS["loop"])
        pygame.mixer.music.play(-1)  # -1 = Бесконечно
        _current_track = "loop"


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
    global _first_init

    if not pygame.get_init():
        pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("🎄 Christmas games set 🎄")
    # загружаем звкуки
    load_sounds_and_music()

    # Музыку запускаем (функция сама проверит, играет ли уже)
    start_global_music()

    clock = pygame.time.Clock()
    font_title = get_font(60, True)
    font_btn = get_font(36, True)
    font_footer = get_font(20)
    font_credits = get_font(26, True)  # Шрифт для "Made by Fit girls"

    return screen, clock, font_title, font_btn, font_footer, font_credits


def main_menu():
    screen, clock, font_title, font_btn, font_footer, font_credits = init_menu()

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

        check_music_loop()

        # События
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            # Обрабатываем событие окончания музыки
            # handle_music_event(event)

            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for btn in menu_buttons:
                    if btn.check_hover(event.pos):
                        play_sfx("menu")
                        ensure_infinite_loop()
                        btn.game_func()  # Запускаем игру
                        # После выхода из игры — снова открываем меню
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
                        play_sfx("menu")

        # Кнопки
        for btn in menu_buttons:
            btn.check_hover(mouse_pos)
            btn.draw(screen, font_btn)

        # ========== НАДПИСЬ "Made by Fit girls" ==========
        credits_text = "Made by Fit girls"
        # Используем тот же offset_y что и у заголовка (полная синхронизация)
        c_shadow = font_credits.render(credits_text, True, (0, 0, 0))
        c_main = font_credits.render(credits_text, True, COLORS["gold"])
        credits_rect = c_main.get_rect(center=(WIDTH // 2, HEIGHT - 70 + offset_y))
        screen.blit(c_shadow, (credits_rect.x + 2, credits_rect.y + 2))
        screen.blit(c_main, credits_rect)

        # Футер (подсказка)
        ft = font_footer.render(
            "Select a game to start playing | ESC - exit", True, (150, 160, 180)
        )
        screen.blit(ft, ft.get_rect(center=(WIDTH // 2, HEIGHT - 30)))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main_menu()
