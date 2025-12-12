import pygame
import random
import sys
import copy
import math
import os

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


SOUNDS_DIR = resource_path("sounds")
# Отладка — удалите потом
print(f"Ищу звуки в: {SOUNDS_DIR}")
print(f"Папка существует: {os.path.exists(SOUNDS_DIR)}")
if os.path.exists(SOUNDS_DIR):
    print(f"Файлы в папке: {os.listdir(SOUNDS_DIR)}")

# --- КОНСТАНТЫ ---
WIDTH = 850
HEIGHT = 800
FPS = 60

# Цвета (Winter/Christmas Palette)
C_BG_TOP = (30, 20, 40)
C_BG_BOT = (10, 10, 20)
C_GLASS_BORDER = (200, 200, 220)
C_GLASS_FILL = (255, 255, 255, 30)
C_HIGHLIGHT = (255, 255, 255, 100)
C_TEXT = (255, 240, 220)

# Цвета жидкостей
COLORS = {
    0: None,
    1: (150, 20, 30),
    2: (65, 95, 55),
    3: (220, 180, 120),
    4: (105, 120, 150),
    5: (150, 150, 120),
    6: (190, 105, 100),
    7: (200, 130, 100),
}

# Настройки колб
TUBE_WIDTH = 60
TUBE_HEIGHT = 240
BLOCK_HEIGHT = 50
MAX_CAPACITY = 4
GAP = 30

# --- УРОВНИ ---
LEVELS = [
    [[1, 2, 1, 2], [2, 1, 2, 1], []],
    [[1, 3, 2, 3], [2, 3, 1, 2], [1, 1, 2, 3], [], []],
    [[4, 4, 2, 3], [3, 1, 1, 2], [2, 3, 1, 1], [4, 2, 3, 4], []],
    [[1, 5, 2, 3], [5, 3, 3, 1], [5, 2, 2, 1], [5, 1, 2, 3], [], []],
    [[4, 2, 1, 5], [3, 5, 1, 5], [1, 4, 2, 3], [4, 4, 3, 5], [3, 2, 2, 1], [], []],
    [
        [1, 6, 5, 2],
        [4, 3, 5, 2],
        [6, 6, 1, 3],
        [2, 1, 4, 5],
        [5, 2, 3, 4],
        [1, 6, 4, 3],
        [],
        [],
    ],
]

# --- АУДИО ---
SOUNDS = {}


def load_sounds():
    files = {
        "flip": ["flip.wav", "flip.mp3"],
        "win": ["hoho (win).wav", "hoho (win).mp3"],
        "lose": ["break (lose).wav", "break (lose).mp3"],
        "full": ["full glass.wav", "full glass.mp3"],
    }

    for name, filenames in files.items():
        for filename in filenames:
            # Используем абсолютный путь
            sound_path = os.path.join(SOUNDS_DIR, filename)
            if os.path.exists(sound_path):
                try:
                    SOUNDS[name] = pygame.mixer.Sound(sound_path)
                    SOUNDS[name].set_volume(0.5)
                    break
                except Exception as e:
                    print(f"Ошибка загрузки звука {sound_path}: {e}")


def play_sfx(name):
    if name in SOUNDS:
        SOUNDS[name].play()


# --- КЛАССЫ ---


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.life = 255
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-2, -0.5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 4
        self.size *= 0.95

    def draw(self, surface):
        if self.life > 0:
            s = pygame.Surface(
                (int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA
            )
            pygame.draw.circle(
                s,
                (*self.color, int(self.life)),
                (int(self.size), int(self.size)),
                int(self.size),
            )
            surface.blit(s, (self.x, self.y))


class SnowManager:
    def __init__(self):
        self.flakes = [
            {
                "x": random.randint(0, WIDTH),
                "y": random.randint(0, HEIGHT),
                "s": random.randint(2, 4),
                "v": random.uniform(0.5, 1.5),
            }
            for _ in range(100)
        ]

    def update_draw(self, surface):
        for f in self.flakes:
            f["y"] += f["v"]
            f["x"] += math.sin(pygame.time.get_ticks() * 0.001 + f["y"]) * 0.3
            if f["y"] > HEIGHT:
                f["y"] = -10
                f["x"] = random.randint(0, WIDTH)
            s = pygame.Surface((f["s"], f["s"]), pygame.SRCALPHA)
            pygame.draw.circle(
                s, (255, 255, 255, 150), (f["s"] // 2, f["s"] // 2), f["s"] // 2
            )
            surface.blit(s, (f["x"], f["y"]))


class Tube:
    def __init__(self, x, y, content):
        self.rect = pygame.Rect(x, y, TUBE_WIDTH, TUBE_HEIGHT)
        self.content = list(content)
        self.selected = False
        self.hover_offset = 0
        self.completed = False
        self.particles = []

    def update(self):
        target_offset = -20 if self.selected else 0
        self.hover_offset += (target_offset - self.hover_offset) * 0.2

        if (
            not self.completed
            and len(self.content) == 4
            and len(set(self.content)) == 1
        ):
            self.completed = True

            # --- Звук заполненной колбы ---
            play_sfx("full")

            for _ in range(30):
                self.particles.append(
                    Particle(self.rect.centerx, self.rect.top, COLORS[self.content[0]])
                )

        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

    def draw(self, surface):
        draw_y = self.rect.y + self.hover_offset

        for i, color_idx in enumerate(self.content):
            color = COLORS[color_idx]
            block_y = draw_y + TUBE_HEIGHT - (i + 1) * BLOCK_HEIGHT - 10
            liq_rect = pygame.Rect(
                self.rect.x + 4, block_y, TUBE_WIDTH - 8, BLOCK_HEIGHT
            )
            pygame.draw.rect(surface, color, liq_rect, border_radius=10)
            pygame.draw.rect(
                surface,
                (255, 255, 255, 50),
                (liq_rect.x, liq_rect.y, 10, BLOCK_HEIGHT),
                border_radius=10,
            )

        glass_surf = pygame.Surface((TUBE_WIDTH, TUBE_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(
            glass_surf, C_GLASS_FILL, (0, 0, TUBE_WIDTH, TUBE_HEIGHT), border_radius=20
        )
        pygame.draw.rect(
            glass_surf,
            C_GLASS_BORDER,
            (0, 0, TUBE_WIDTH, TUBE_HEIGHT),
            3,
            border_radius=20,
        )
        pygame.draw.rect(
            glass_surf, C_GLASS_BORDER, (0, 0, TUBE_WIDTH, 10), border_radius=5
        )
        pygame.draw.line(glass_surf, C_HIGHLIGHT, (10, 20), (10, TUBE_HEIGHT - 20), 3)
        surface.blit(glass_surf, (self.rect.x, draw_y))

        if self.completed:
            cork_rect = pygame.Rect(self.rect.x + 5, draw_y - 10, TUBE_WIDTH - 10, 15)
            pygame.draw.rect(surface, (139, 69, 19), cork_rect, border_radius=3)
            for p in self.particles:
                p.draw(surface)


class GameManager:
    def __init__(self, screen, font_ui, font_title):
        self.screen = screen
        self.font_ui = font_ui
        self.font_title = font_title
        self.level_idx = 0
        self.load_level(self.level_idx)
        self.snow = SnowManager()
        self.game_won = False

    def load_level(self, idx):
        self.level_idx = idx
        self.tubes = []
        level_data = copy.deepcopy(LEVELS[idx])
        num_tubes = len(level_data)
        total_width = num_tubes * TUBE_WIDTH + (num_tubes - 1) * GAP
        start_x = (WIDTH - total_width) // 2
        start_y = HEIGHT // 2 - TUBE_HEIGHT // 2 + 50

        for i, content in enumerate(level_data):
            x = start_x + i * (TUBE_WIDTH + GAP)
            self.tubes.append(Tube(x, start_y, content))

        self.selected_idx = None
        self.game_won = False

    def handle_click(self, pos):
        if self.game_won:
            return

        clicked_idx = None
        for i, tube in enumerate(self.tubes):
            hitbox = tube.rect.inflate(0, 40)
            if hitbox.collidepoint(pos):
                clicked_idx = i
                break

        if clicked_idx is not None:
            if self.selected_idx is None:
                if self.tubes[clicked_idx].content:
                    self.selected_idx = clicked_idx
                    self.tubes[clicked_idx].selected = True
                    # --- Звук выбора/поднятия колбы ---
                    play_sfx("flip")
            else:
                src = self.selected_idx
                dst = clicked_idx

                if src == dst:
                    self.tubes[src].selected = False
                    self.selected_idx = None
                    # --- Звук опускания колбы ---
                    play_sfx("flip")
                else:
                    if self.try_pour(src, dst):
                        self.tubes[src].selected = False
                        self.selected_idx = None
                        self.check_win()
                        play_sfx("flip") #переливание
                    else:
                        self.tubes[src].selected = False
                        if self.tubes[dst].content:
                            self.selected_idx = dst
                            self.tubes[dst].selected = True
                            play_sfx("flip")
                        else:
                            self.selected_idx = None

    def try_pour(self, src_idx, dst_idx):
        src = self.tubes[src_idx]
        dst = self.tubes[dst_idx]

        if not src.content:
            return False
        if len(dst.content) >= MAX_CAPACITY:
            return False

        color_to_move = src.content[-1]

        if not dst.content or dst.content[-1] == color_to_move:
            count = 0
            for color in reversed(src.content):
                if color == color_to_move:
                    count += 1
                else:
                    break

            space = MAX_CAPACITY - len(dst.content)
            amount = min(count, space)

            for _ in range(amount):
                dst.content.append(src.content.pop())
            return True
        return False

    def check_win(self):
        won = True
        for tube in self.tubes:
            if not tube.content:
                continue
            if len(tube.content) != MAX_CAPACITY:
                won = False
                break
            if len(set(tube.content)) != 1:
                won = False
                break
        if won:
            self.game_won = True
            play_sfx("win")

    def next_level(self):
        if self.level_idx < len(LEVELS) - 1:
            self.load_level(self.level_idx + 1)
        else:
            self.level_idx = 0
            self.load_level(0)

    def reset_level(self):
        self.load_level(self.level_idx)

    def update(self):
        for tube in self.tubes:
            tube.update()

    def draw(self):
        surface = self.screen

        # Фон
        for i in range(HEIGHT):
            ratio = i / HEIGHT
            color = [C_BG_TOP[j] * (1 - ratio) + C_BG_BOT[j] * ratio for j in range(3)]
            pygame.draw.line(surface, color, (0, i), (WIDTH, i))

        self.snow.update_draw(surface)

        # Заголовок
        title_surf = self.font_title.render(f"Level {self.level_idx + 1}", True, C_TEXT)
        surface.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 50))

        # UI подсказки                                                                                       !!!!
        ui_surf = self.font_ui.render("R: Restart | ESC: Menu", True, (150, 150, 150))
        surface.blit(ui_surf, (WIDTH - 260, 15))

        # Колбы
        for tube in self.tubes:
            tube.draw(surface)

        # Win Screen                                                                                      !!!!
        if self.game_won:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            surface.blit(overlay, (0, 0))

            win_text = self.font_title.render("Level Complete!", True, (230, 190, 120))
            next_hint = "Press SPACE for next level"
            if self.level_idx == len(LEVELS) - 1:
                next_hint = "You finished the game! SPACE to replay"
            hint_text = self.font_ui.render(next_hint, True, C_TEXT)

            surface.blit(
                win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 50)
            )
            surface.blit(
                hint_text, (WIDTH // 2 - hint_text.get_width() // 2, HEIGHT // 2 + 20)
            )


# ====== ФУНКЦИЯ ЗАПУСКА ДЛЯ МЕНЮ ======
def run():
    """Точка входа для вызова из главного меню"""
    if not pygame.get_init():
        pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Christmas Water Sort Game 🧪🎄")
    # --- ЗВУКИ ---
    load_sounds()
    clock = pygame.time.Clock()

    # Шрифты
    font_ui = pygame.font.SysFont("Georgia", 24)
    font_title = pygame.font.SysFont("Georgia", 50, bold=True)

    game = GameManager(screen, font_ui, font_title)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False  # Выход в меню
                if event.key == pygame.K_r:
                    game.reset_level()
                if game.game_won and event.key == pygame.K_SPACE:
                    game.next_level()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.handle_click(event.pos)

        game.update()
        game.draw()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


# Для запуска файла напрямую
if __name__ == "__main__":
    run()
