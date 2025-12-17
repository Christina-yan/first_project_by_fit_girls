import pygame
import random
import sys
import copy
import math
import os


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


# --- ПУТИ И ЗВУКИ ---
SOUNDS_DIR = resource_path("sounds")
SAVE_FILE = "save_game.txt"

# --- КОНСТАНТЫ ---
WIDTH = 850
HEIGHT = 800
FPS = 60

# Цвета
C_BG_TOP = (30, 20, 40)
C_BG_BOT = (10, 10, 20)
C_GLASS_BORDER = (200, 200, 220)
C_GLASS_FILL = (255, 255, 255, 30)
C_HIGHLIGHT = (255, 255, 255, 100)
C_TEXT = (255, 240, 220)

# Цвета жидкостей
COLORS = {
    0: None,
    1: (150, 20, 30),  # Красный
    2: (65, 95, 55),  # Зеленый
    3: (220, 180, 120),  # Золотой
    4: (105, 120, 150),  # Сиреневый
    5: (150, 150, 120),  # Оливковый
    6: (230, 170, 150),  # Персиковый
    7: (210, 130, 100),  # Оранжевый
    8: (70, 130, 180),  # Стальной синий
    9: (128, 0, 128),  # Пурпурный
}

# Настройки колб
TUBE_WIDTH = 60
TUBE_HEIGHT = 240
BLOCK_HEIGHT = 50
MAX_CAPACITY = 4
GAP = 30

# --- УРОВНИ ---
LEVELS = [
    # Уровень 1
    [[1, 2, 1, 2], [2, 1, 2, 1], []],
    # Уровень 2
    [[1, 3, 2, 3], [2, 3, 1, 2], [1, 1, 2, 3], [], []],
    # Уровень 3
    [[4, 4, 2, 3], [3, 1, 1, 2], [2, 3, 1, 1], [4, 2, 3, 4], []],
    # Уровень 4
    [[1, 5, 2, 3], [5, 3, 3, 1], [5, 2, 2, 1], [5, 1, 2, 3], [], []],
    # Уровень 5
    [[4, 2, 1, 5], [3, 5, 1, 5], [1, 4, 2, 3], [4, 4, 3, 5], [3, 2, 2, 1], [], []],
    # Уровень 6
    [[1, 6, 5, 2], [4, 3, 5, 2], [6, 6, 1, 3], [2, 1, 4, 5], [5, 2, 3, 4], [1, 6, 4, 3], [], []],
    # Уровень 7
    [[1, 7, 3, 4], [5, 2, 6, 1], [7, 4, 2, 5], [3, 6, 1, 7], [4, 5, 3, 2], [6, 1, 7, 5], [2, 3, 4, 6], [], []],
    # Уровень 8
    [[1, 8, 2, 3], [4, 5, 6, 1], [7, 8, 2, 5], [3, 6, 4, 8], [1, 7, 3, 5], [2, 4, 6, 8], [5, 1, 7, 2], [6, 3, 4, 7], [],
     []],
    # Уровень 9
    [[1, 9, 2, 3], [4, 5, 6, 7], [8, 9, 1, 2], [3, 4, 5, 6], [7, 8, 9, 1], [2, 3, 4, 5], [6, 7, 8, 9], [5, 1, 6, 2],
     [7, 3, 8, 4], [], []]
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


# --- СОХРАНЕНИЕ ---
def get_save_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, SAVE_FILE)


def load_progress():
    path = get_save_path()
    if not os.path.exists(path): return 0
    try:
        with open(path, 'r') as f:
            level = int(f.read().strip())
            if level < 0: return 0
            if level >= len(LEVELS): return len(LEVELS) - 1
            return level
    except:
        return 0


def save_progress(level_idx):
    path = get_save_path()
    try:
        with open(path, 'w') as f:
            f.write(str(level_idx))
    except:
        pass


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
            s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, int(self.life)), (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (self.x, self.y))


class SnowManager:
    def __init__(self):
        self.flakes = [{"x": random.randint(0, WIDTH), "y": random.randint(0, HEIGHT), "s": random.randint(2, 4),
                        "v": random.uniform(0.5, 1.5)} for _ in range(100)]

    def update_draw(self, surface):
        for f in self.flakes:
            f["y"] += f["v"]
            f["x"] += math.sin(pygame.time.get_ticks() * 0.001 + f["y"]) * 0.3
            if f["y"] > HEIGHT:
                f["y"] = -10
                f["x"] = random.randint(0, WIDTH)
            s = pygame.Surface((f["s"], f["s"]), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 255, 150), (f["s"] // 2, f["s"] // 2), f["s"] // 2)
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

        if not self.completed and len(self.content) == 4 and len(set(self.content)) == 1:
            self.completed = True
            play_sfx("full")
            for _ in range(30):
                self.particles.append(Particle(self.rect.centerx, self.rect.top, COLORS[self.content[0]]))

        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

    def draw(self, surface):
        draw_y = self.rect.y + self.hover_offset
        for i, color_idx in enumerate(self.content):
            color = COLORS[color_idx]
            block_y = draw_y + TUBE_HEIGHT - (i + 1) * BLOCK_HEIGHT - 10
            liq_rect = pygame.Rect(self.rect.x + 4, block_y, TUBE_WIDTH - 8, BLOCK_HEIGHT)
            pygame.draw.rect(surface, color, liq_rect, border_radius=10)
            pygame.draw.rect(surface, (255, 255, 255, 50), (liq_rect.x, liq_rect.y, 10, BLOCK_HEIGHT), border_radius=10)

        glass_surf = pygame.Surface((TUBE_WIDTH, TUBE_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(glass_surf, C_GLASS_FILL, (0, 0, TUBE_WIDTH, TUBE_HEIGHT), border_radius=20)
        pygame.draw.rect(glass_surf, C_GLASS_BORDER, (0, 0, TUBE_WIDTH, TUBE_HEIGHT), 3, border_radius=20)
        pygame.draw.rect(glass_surf, C_GLASS_BORDER, (0, 0, TUBE_WIDTH, 10), border_radius=5)
        pygame.draw.line(glass_surf, C_HIGHLIGHT, (10, 20), (10, TUBE_HEIGHT - 20), 3)
        surface.blit(glass_surf, (self.rect.x, draw_y))

        if self.completed:
            cork_rect = pygame.Rect(self.rect.x + 5, draw_y - 10, TUBE_WIDTH - 10, 15)
            pygame.draw.rect(surface, (139, 69, 19), cork_rect, border_radius=3)
            for p in self.particles:
                p.draw(surface)


# --- ФУНКЦИЯ ДЛЯ КРАСИВОГО ТЕКСТА ---
def draw_pro_text(surface, text, font, center_pos, color=(255, 255, 255)):
    # 1. Тень (мягкая)
    shadow_surf = font.render(text, True, (0, 0, 0))
    shadow_surf.set_alpha(120)
    shadow_rect = shadow_surf.get_rect(center=(center_pos[0] + 3, center_pos[1] + 3))
    surface.blit(shadow_surf, shadow_rect)

    # 2. Обводка
    offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    for dx, dy in offsets:
        outline = font.render(text, True, (0, 0, 0))
        outline.set_alpha(150)
        r = outline.get_rect(center=(center_pos[0] + dx, center_pos[1] + dy))
        surface.blit(outline, r)

    # 3. Основной текст
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=center_pos)
    surface.blit(text_surf, text_rect)


class GameManager:
    def __init__(self, screen, font_ui, font_title):
        self.screen = screen
        self.font_ui = font_ui
        self.font_title = font_title

        # Доп шрифты для красивого окна
        try:
            self.font_sub = pygame.font.SysFont("georgia", 36)
            self.font_small = pygame.font.SysFont("arial", 22, bold=True)
        except:
            self.font_sub = font_ui
            self.font_small = font_ui

        self.level_idx = load_progress()
        self.moves = 0

        self.load_images()
        self.load_level(self.level_idx)
        self.snow = SnowManager()

        # Состояние игры
        self.game_won = False

        # Анимация
        self.anim_progress = 0.0
        self.blur_bg = None

    def load_images(self):
        self.win_image = None
        self.lose_image = None
        try:
            w_path = resource_path(os.path.join("Win_Lose_screen", "Win.png"))
            if os.path.exists(w_path):
                self.win_image = pygame.image.load(w_path).convert_alpha()

            l_path = resource_path(os.path.join("Win_Lose_screen", "Lose.png"))
            if os.path.exists(l_path):
                self.lose_image = pygame.image.load(l_path).convert_alpha()
        except Exception as e:
            pass

    def load_level(self, idx):
        self.level_idx = idx
        self.tubes = []
        self.moves = 0

        if idx >= len(LEVELS):
            idx = 0
            self.level_idx = 0

        level_data = copy.deepcopy(LEVELS[idx])
        num_tubes = len(level_data)

        if num_tubes > 8:
            row1 = num_tubes // 2 + num_tubes % 2
            total_width1 = row1 * TUBE_WIDTH + (row1 - 1) * GAP
            start_x1 = (WIDTH - total_width1) // 2
            y1 = HEIGHT // 2 - TUBE_HEIGHT + 20

            row2 = num_tubes - row1
            total_width2 = row2 * TUBE_WIDTH + (row2 - 1) * GAP
            start_x2 = (WIDTH - total_width2) // 2
            y2 = HEIGHT // 2 + 50

            for i, content in enumerate(level_data):
                if i < row1:
                    x = start_x1 + i * (TUBE_WIDTH + GAP)
                    self.tubes.append(Tube(x, y1, content))
                else:
                    x = start_x2 + (i - row1) * (TUBE_WIDTH + GAP)
                    self.tubes.append(Tube(x, y2, content))
        else:
            total_width = num_tubes * TUBE_WIDTH + (num_tubes - 1) * GAP
            start_x = (WIDTH - total_width) // 2
            start_y = HEIGHT // 2 - TUBE_HEIGHT // 2 + 50
            for i, content in enumerate(level_data):
                x = start_x + i * (TUBE_WIDTH + GAP)
                self.tubes.append(Tube(x, start_y, content))

        self.selected_idx = None
        self.game_won = False
        self.anim_progress = 0.0
        self.blur_bg = None
        save_progress(self.level_idx)

    def handle_click(self, pos):
        # Если победа и анимация закончилась - клик переходит на след. уровень
        if self.game_won:
            if self.anim_progress >= 1.0:
                self.next_level()
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
                    play_sfx("flip")
            else:
                src = self.selected_idx
                dst = clicked_idx

                if src == dst:
                    self.tubes[src].selected = False
                    self.selected_idx = None
                    play_sfx("flip")
                else:
                    if self.try_pour(src, dst):
                        self.tubes[src].selected = False
                        self.selected_idx = None
                        self.check_win()
                        play_sfx("flip")
                        self.moves += 1
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
        if not src.content: return False
        if len(dst.content) >= MAX_CAPACITY: return False
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
            for _ in range(amount): dst.content.append(src.content.pop())
            return True
        return False

    def check_win(self):
        won = True
        for tube in self.tubes:
            if not tube.content: continue
            if len(tube.content) != MAX_CAPACITY: won = False; break
            if len(set(tube.content)) != 1: won = False; break
        if won:
            self.game_won = True
            # Создаем скриншот для размытия
            try:
                snapshot = self.screen.copy()
                small = pygame.transform.smoothscale(snapshot, (WIDTH // 10, HEIGHT // 10))
                self.blur_bg = pygame.transform.smoothscale(small, (WIDTH, HEIGHT))
            except:
                self.blur_bg = None
            play_sfx("win")

    def next_level(self):
        if self.level_idx < len(LEVELS) - 1:
            self.level_idx += 1
            self.load_level(self.level_idx)
        else:
            self.level_idx = 0
            self.load_level(0)

    def reset_level(self):
        self.load_level(self.level_idx)

    def update(self):
        for tube in self.tubes:
            tube.update()

        # Анимация победы (замедлена с 0.015 до 0.010 для большей плавности)
        if self.game_won:
            if self.anim_progress < 1.0:
                self.anim_progress += 0.010
                if self.anim_progress > 1.0: self.anim_progress = 1.0

    def draw(self):
        surface = self.screen

        if not self.game_won:
            # Обычный фон игры
            for i in range(HEIGHT):
                ratio = i / HEIGHT
                color = [C_BG_TOP[j] * (1 - ratio) + C_BG_BOT[j] * ratio for j in range(3)]
                pygame.draw.line(surface, color, (0, i), (WIDTH, i))
            self.snow.update_draw(surface)
        else:
            # Размытый фон при победе
            if self.blur_bg:
                surface.blit(self.blur_bg, (0, 0))
            else:
                surface.fill(C_BG_TOP)

        # Заголовок
        if not self.game_won:
            title_surf = self.font_title.render(f"Level {self.level_idx + 1}", True, C_TEXT)
            surface.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 50))

            ui_text = "R: Restart | ESC: Menu"
            ui_surf = self.font_ui.render(ui_text, True, (150, 150, 150))
            surface.blit(ui_surf, (WIDTH - 260, 15))

            moves_surf = self.font_ui.render(f"Moves: {self.moves}", True, (200, 200, 100))
            surface.blit(moves_surf, (WIDTH - 260, 45))

        # Колбы (рисуем всегда)
        if not self.game_won or (self.game_won and self.blur_bg is None):
            for i, tube in enumerate(self.tubes):
                tube.draw(surface)

        # Win Screen (Professional Style)
        if self.game_won:
            # 1. Функция плавности (Quartic Ease-Out)
            ease = 1 - math.pow(1 - self.anim_progress, 4)

            # 2. Затемнение (до 160, было 200) - чуть светлее
            dark_alpha = int(ease * 160)
            darkness = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            darkness.fill((0, 0, 0, dark_alpha))
            surface.blit(darkness, (0, 0))

            # 3. Картинка и текст
            if self.win_image:
                # Масштабирование (Pop-up)
                current_scale = 0.6 + 0.4 * ease
                if current_scale > 0.1:
                    img_target_w = 480
                    aspect_ratio = self.win_image.get_height() / self.win_image.get_width()
                    img_target_h = int(img_target_w * aspect_ratio)

                    final_w = int(img_target_w * current_scale)
                    final_h = int(img_target_h * current_scale)
                    final_img = pygame.transform.smoothscale(self.win_image, (final_w, final_h))

                    # Прозрачность при появлении
                    final_img.set_alpha(int(255 * ease))

                    img_rect = final_img.get_rect()
                    img_rect.center = (WIDTH // 2, HEIGHT // 2 - 50)

                    surface.blit(final_img, img_rect)

                    # Текст (появляется только когда картинка почти остановилась)
                    if ease > 0.6:
                        text_alpha = int(255 * ease)
                        y_start = img_rect.bottom + 45

                        moves_text = f"Finished in {self.moves} moves"
                        hint_text = "Click to Continue"
                        if self.level_idx == len(LEVELS) - 1:
                            hint_text = "Game Completed! Click to replay"

                        # Отрисовка с тенью и обводкой
                        draw_pro_text(surface, moves_text, self.font_sub, (WIDTH // 2, y_start), (255, 255, 255))

                        # Разделитель (плавная ширина)
                        line_width = int(300 * ease)
                        if line_width > 0:
                            line_surf = pygame.Surface((line_width, 2), pygame.SRCALPHA)
                            line_surf.fill((255, 255, 255, 180))
                            line_rect = line_surf.get_rect(center=(WIDTH // 2, y_start + 30))
                            surface.blit(line_surf, line_rect)

                        draw_pro_text(surface, hint_text, self.font_small, (WIDTH // 2, y_start + 55), (200, 200, 200))
            else:
                # Фоллбэк
                win_text = self.font_title.render("Level Complete!", True, (230, 190, 120))
                surface.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 50))


# ====== ЗАПУСК ======
def run():
    if not pygame.get_init(): pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Christmas Water Sort Game 🧪🎄")
    load_sounds()
    clock = pygame.time.Clock()
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
                    running = False
                elif event.key == pygame.K_r:
                    game.reset_level()
                elif game.game_won and event.key == pygame.K_SPACE:
                    if game.anim_progress >= 1.0:
                        game.next_level()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # ЛКМ
                    game.handle_click(event.pos)

        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(FPS)
    return


if __name__ == "__main__":
    run()