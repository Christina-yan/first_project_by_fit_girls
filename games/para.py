import pygame
import random
import sys
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


SOUNDS_DIR = resource_path("sounds")
IMG_DIR = resource_path("img")

# --- КОНСТАНТЫ И НАСТРОЙКИ ---
SCREEN_WIDTH = 850
SCREEN_HEIGHT = 800
FPS = 60

# --- ПАЛИТРА ---
COLOR_TOP = (180, 210, 240)
COLOR_BOTTOM = (255, 255, 255)
COLOR_UI_BAR = (40, 50, 80)
COLOR_TEXT_MAIN = (255, 255, 255)
COLOR_TEXT_ACCENT = (255, 215, 0)
COLOR_TIMER_WARN = (255, 100, 100)

COLOR_CARD_BACK = (200, 40, 50)
COLOR_CARD_BORDER = (255, 255, 255)
COLOR_SHADOW = (150, 160, 180)

LIGHT_COLORS = [
    (255, 60, 60),
    (60, 255, 60),
    (255, 220, 50),
    (50, 150, 255),
    (255, 100, 255),
]

# --- УРОВНИ ---
LEVELS = [
    {"level": 1, "rows": 2, "cols": 2, "time": 15},
    {"level": 2, "rows": 2, "cols": 4, "time": 30},
    {"level": 3, "rows": 3, "cols": 4, "time": 50},
    {"level": 4, "rows": 4, "cols": 4, "time": 70},
    {"level": 5, "rows": 3, "cols": 6, "time": 90},
]

GRID_OFFSET_Y = 130
GRID_MARGIN_BOTTOM = 100
CARD_W = 0
CARD_H = 0
GAP = 15
START_X = 0
START_Y = 0

# --- АУДИО ---
SOUNDS = {}


def load_sounds():
    files = {
        "flip": ["flip.wav", "flip.mp3"],
        "win": ["hoho (win).wav", "hoho (win).mp3"],
        "lose": ["break (lose).wav", "break (lose).mp3"],
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
                    pass


def play_sfx(name):
    if name in SOUNDS:
        SOUNDS[name].play()


# --- КАРТИНКИ ---
def load_all_images():
    images = []
    if not os.path.exists(IMG_DIR):
        return images

    for i in range(1, 16):
        for ext in [".png", ".jpg"]:
            img_path = os.path.join(IMG_DIR, f"{i}{ext}")
            if os.path.exists(img_path):
                try:
                    img = pygame.image.load(img_path).convert_alpha()
                    images.append(img)
                    break
                except Exception as e:
                    pass

    if len(images) < 9:
        for k in range(len(images), 15):
            s = pygame.Surface((200, 200))
            s.fill((random.randint(200, 250), 100, 100))
            pygame.draw.rect(s, (255, 255, 255), (0, 0, 200, 200), 5)
            images.append(s)
    return images


ORIGINAL_IMAGES = []


# --- ДЕКОР ---
def draw_decorations(screen):
    pygame.draw.ellipse(screen, (245, 250, 255), (-100, SCREEN_HEIGHT - 120, SCREEN_WIDTH + 200, 200))
    pygame.draw.ellipse(screen, (255, 255, 255), (SCREEN_WIDTH - 400, SCREEN_HEIGHT - 150, 500, 200))

    tree_x = SCREEN_WIDTH - 100
    tree_y = SCREEN_HEIGHT - 40
    pygame.draw.rect(screen, (100, 60, 30), (tree_x - 10, tree_y - 40, 20, 40))
    green = (34, 139, 34)
    pygame.draw.polygon(screen, green, [(tree_x, tree_y - 110), (tree_x - 60, tree_y - 30), (tree_x + 60, tree_y - 30)])
    pygame.draw.polygon(screen, green, [(tree_x, tree_y - 160), (tree_x - 50, tree_y - 70), (tree_x + 50, tree_y - 70)])
    pygame.draw.polygon(screen, green,
                        [(tree_x, tree_y - 200), (tree_x - 35, tree_y - 120), (tree_x + 35, tree_y - 120)])
    pygame.draw.circle(screen, (255, 0, 0), (tree_x - 20, tree_y - 60), 5)
    pygame.draw.circle(screen, (255, 215, 0), (tree_x + 15, tree_y - 90), 5)
    pygame.draw.circle(screen, (50, 100, 255), (tree_x - 10, tree_y - 130), 5)
    pygame.draw.circle(screen, (255, 215, 0), (tree_x, tree_y - 200), 8)


class Garland:
    def __init__(self):
        self.bulbs = []
        count = 18
        step = SCREEN_WIDTH / count
        for i in range(count + 1):
            x = i * step
            offset_y = abs(math.sin(i * 0.8)) * 20
            base_y = 100
            color = random.choice(LIGHT_COLORS)
            self.bulbs.append({"x": x, "y": base_y + offset_y, "color": color, "phase": random.uniform(0, 6.28)})

    def draw(self, screen, time_now):
        if len(self.bulbs) > 1:
            points = [(b["x"], b["y"] - 4) for b in self.bulbs]
            pygame.draw.lines(screen, (40, 50, 60), False, points, 2)

        for b in self.bulbs:
            brightness = (math.sin(time_now * 0.003 + b["phase"]) + 1) / 2
            brightness = 0.5 + (brightness * 0.5)
            r, g, bl = b["color"]
            glow_r = 6 + int(brightness * 5)
            glow_s = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_s, (r, g, bl, int(80 * brightness)), (glow_r, glow_r), glow_r)
            screen.blit(glow_s, (b["x"] - glow_r, b["y"] - glow_r))
            pygame.draw.rect(screen, (30, 30, 40), (b["x"] - 2, b["y"] - 6, 4, 4))
            final_col = (
            min(255, int(r * brightness + 50)), min(255, int(g * brightness + 50)), min(255, int(bl * brightness + 50)))
            pygame.draw.circle(screen, final_col, (b["x"], b["y"]), 4)


class SnowFlake:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(-50, SCREEN_HEIGHT)
        self.size = random.randint(4, 8)
        self.speed = random.uniform(0.8, 2.0)
        self.alpha = random.randint(150, 255)

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = -10
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self, screen):
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, self.alpha), (self.size // 2, self.size // 2), self.size // 2)
        screen.blit(s, (self.x, self.y))


class Sparkle:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.life = 255
        self.size = random.randint(4, 8)
        self.vx, self.vy = random.uniform(-4, 4), random.uniform(-4, 4)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 8
        self.size -= 0.1

    def draw(self, screen):
        if self.life > 0:
            s = pygame.Surface((int(self.size) * 2, int(self.size) * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 215, 0, self.life), (int(self.size), int(self.size)), int(self.size))
            screen.blit(s, (self.x - self.size, self.y - self.size))


class Card:
    def __init__(self, r, c, img_idx, image_surface):
        self.r, self.c = r, c
        self.img_idx = img_idx
        self.image = image_surface
        self.target_x = START_X + c * (CARD_W + GAP)
        self.target_y = START_Y + r * (CARD_H + GAP)
        self.x = self.target_x
        self.y = -300
        self.rect = pygame.Rect(self.x, self.y, CARD_W, CARD_H)
        self.is_flipped = False
        self.is_solved = False
        self.hovered = False

    def update(self, mouse_pos):
        self.y += (self.target_y - self.y) * 0.12
        self.rect.y = int(self.y)
        self.rect.x = int(self.target_x)
        if self.rect.collidepoint(mouse_pos) and not self.is_flipped and not self.is_solved:
            self.hovered = True
        else:
            self.hovered = False

    def draw(self, screen):
        dy = self.y - 8 if self.hovered else self.y
        draw_rect = pygame.Rect(self.x, dy, CARD_W, CARD_H)
        s_surf = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
        pygame.draw.rect(s_surf, (*COLOR_SHADOW, 100), (0, 0, CARD_W, CARD_H), border_radius=12)
        screen.blit(s_surf, (self.x + 5, dy + 5))

        if self.is_flipped or self.is_solved:
            pygame.draw.rect(screen, (255, 255, 255), draw_rect, border_radius=12)
            if self.image:
                ir = self.image.get_rect(center=draw_rect.center)
                screen.blit(self.image, ir)
            if self.is_solved:
                pygame.draw.rect(screen, (255, 215, 0), draw_rect, width=5, border_radius=12)
            else:
                pygame.draw.rect(screen, (200, 200, 200), draw_rect, width=2, border_radius=12)
        else:
            col = (220, 50, 60) if self.hovered else COLOR_CARD_BACK
            pygame.draw.rect(screen, col, draw_rect, border_radius=12)
            cx, cy = draw_rect.centerx, draw_rect.centery
            pygame.draw.rect(screen, (255, 215, 0), (cx - CARD_W * 0.08, dy, CARD_W * 0.16, CARD_H))
            pygame.draw.rect(screen, (255, 215, 0), (self.x, cy - CARD_H * 0.08, CARD_W, CARD_H * 0.16))
            pygame.draw.rect(screen, (255, 255, 255), draw_rect, width=2, border_radius=12)


# --- SETUP ---
def setup_level(level_index):
    global CARD_W, CARD_H, START_X, START_Y, GAP
    lvl = LEVELS[level_index]
    rows, cols = lvl["rows"], lvl["cols"]
    avail_w = SCREEN_WIDTH - 60
    avail_h = SCREEN_HEIGHT - GRID_OFFSET_Y - GRID_MARGIN_BOTTOM
    opt_w = (avail_w - GAP * (cols - 1)) // cols
    opt_h = (avail_h - GAP * (rows - 1)) // rows
    size = min(opt_w, opt_h)
    size = min(size, 140)
    CARD_W, CARD_H = size, size
    grid_w = cols * CARD_W + (cols - 1) * GAP
    grid_h = rows * CARD_H + (rows - 1) * GAP
    START_X = (SCREEN_WIDTH - grid_w) // 2
    START_Y = GRID_OFFSET_Y + (avail_h - grid_h) // 2
    num_pairs = (rows * cols) // 2
    deck = list(range(num_pairs)) * 2
    random.shuffle(deck)
    cards = []
    cache = {}
    for r in range(rows):
        for c in range(cols):
            idx = deck.pop()
            if idx not in cache:
                orig = ORIGINAL_IMAGES[idx % len(ORIGINAL_IMAGES)]
                s_sz = int(size * 0.85)
                cache[idx] = pygame.transform.scale(orig, (s_sz, s_sz))
            cards.append(Card(r, c, idx, cache[idx]))
    return cards, lvl["time"]


# --- ФУНКЦИЯ ДЛЯ КРАСИВОГО ТЕКСТА (ПРОФЕССИОНАЛЬНЫЙ ВИД) ---
def draw_pro_text(surface, text, font, center_pos, color=(255, 255, 255)):
    # 1. Тень (мягкая)
    shadow_surf = font.render(text, True, (0, 0, 0))
    shadow_surf.set_alpha(120)
    shadow_rect = shadow_surf.get_rect(center=(center_pos[0] + 3, center_pos[1] + 3))
    surface.blit(shadow_surf, shadow_rect)

    # 2. Обводка (легкая, для читаемости)
    # Рисуем текст черным цветом со смещением на 1 пиксель во все стороны
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


# --- MAIN ---
def run():
    global ORIGINAL_IMAGES
    if not pygame.get_init():
        pygame.init()
    load_sounds()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Winter Memory")
    clock = pygame.time.Clock()

    ORIGINAL_IMAGES = load_all_images()
    garland = Garland()

    try:
        f_ui = pygame.font.SysFont("arial", 28, bold=True)
        f_big = pygame.font.SysFont("georgia", 70, bold=True)
        f_sub = pygame.font.SysFont("georgia", 36)  # Чуть крупнее для счета
        f_small = pygame.font.SysFont("arial", 22, bold=True)
    except:
        f_ui = pygame.font.Font(None, 30)
        f_big = pygame.font.Font(None, 70)
        f_sub = pygame.font.Font(None, 36)
        f_small = pygame.font.Font(None, 24)

    lose_image = None
    win_image = None

    try:
        l_path = resource_path(os.path.join("Win_Lose_screen", "Lose.png"))
        if os.path.exists(l_path):
            lose_image = pygame.image.load(l_path).convert_alpha()

        w_path = resource_path(os.path.join("Win_Lose_screen", "Win.png"))
        if os.path.exists(w_path):
            win_image = pygame.image.load(w_path).convert_alpha()
    except Exception as e:
        pass

    curr_lvl = 0
    cards = []
    time_left = 0
    score = 0
    state = "START"
    sel = []
    parts = []
    snow = [SnowFlake() for _ in range(180)]
    block = False
    timer_check = 0
    last_time = pygame.time.get_ticks()

    # Анимация
    blur_bg = None
    # Используем float для очень плавной анимации (0.0 -> 1.0)
    anim_progress = 0.0

    running = True
    while running:
        now = pygame.time.get_ticks()
        dt = (now - last_time) / 1000.0
        last_time = now
        mpos = pygame.mouse.get_pos()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False

            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                # В конце анимации можно кликать
                animation_done = (anim_progress >= 1.0) if (state in ["LEVEL_DONE", "GAME_OVER", "WIN"]) else True

                if state == "START":
                    curr_lvl, score = 0, 0
                    cards, time_left = setup_level(curr_lvl)
                    state = "PLAY"
                elif state == "LEVEL_DONE" and animation_done:
                    curr_lvl += 1
                    if curr_lvl >= len(LEVELS):
                        state = "START"
                    else:
                        cards, time_left = setup_level(curr_lvl)
                        state = "PLAY"
                elif state == "GAME_OVER" and animation_done:
                    state = "START"
                elif state == "PLAY" and not block:
                    for c in cards:
                        if c.rect.collidepoint(mpos) and not c.is_flipped and not c.is_solved:
                            c.is_flipped = True
                            play_sfx("flip")
                            sel.append(c)
                            if len(sel) == 2:
                                block = True
                                timer_check = now

        for s in snow:
            s.update()

        if state == "PLAY":
            time_left -= dt
            if time_left <= 0:
                time_left = 0
                state = "GAME_OVER"
                anim_progress = 0.0  # Сброс анимации
                try:
                    snapshot = screen.copy()
                    small = pygame.transform.smoothscale(snapshot, (SCREEN_WIDTH // 10, SCREEN_HEIGHT // 10))
                    blur_bg = pygame.transform.smoothscale(small, (SCREEN_WIDTH, SCREEN_HEIGHT))
                except:
                    blur_bg = None
                play_sfx("lose")

            if block and (now - timer_check > 700):
                c1, c2 = sel
                if c1.img_idx == c2.img_idx:
                    c1.is_solved = True
                    c2.is_solved = True
                    score += 100 + int(time_left * 2)
                    for _ in range(25):
                        parts.append(Sparkle(c1.rect.centerx, c1.rect.centery))
                        parts.append(Sparkle(c2.rect.centerx, c2.rect.centery))
                else:
                    c1.is_flipped = False
                    c2.is_flipped = False
                    score = max(0, score - 15)
                sel = []
                block = False

            if all(c.is_solved for c in cards):
                state = "LEVEL_DONE"
                anim_progress = 0.0  # Сброс анимации
                try:
                    snapshot = screen.copy()
                    small = pygame.transform.smoothscale(snapshot, (SCREEN_WIDTH // 10, SCREEN_HEIGHT // 10))
                    blur_bg = pygame.transform.smoothscale(small, (SCREEN_WIDTH, SCREEN_HEIGHT))
                except:
                    blur_bg = None
                play_sfx("win")

        for c in cards:
            c.update(mpos)
        for p in parts[:]:
            p.update()
            if p.life <= 0:
                parts.remove(p)

        # --- ОТРИСОВКА ---

        if state == "PLAY":
            for i in range(SCREEN_HEIGHT):
                r = COLOR_TOP[0] + (COLOR_BOTTOM[0] - COLOR_TOP[0]) * i / SCREEN_HEIGHT
                g = COLOR_TOP[1] + (COLOR_BOTTOM[1] - COLOR_TOP[1]) * i / SCREEN_HEIGHT
                b = COLOR_TOP[2] + (COLOR_BOTTOM[2] - COLOR_TOP[2]) * i / SCREEN_HEIGHT
                pygame.draw.line(screen, (r, g, b), (0, i), (SCREEN_WIDTH, i))
            for s in snow: s.draw(screen)
            draw_decorations(screen)
            pygame.draw.rect(screen, COLOR_UI_BAR, (0, 0, SCREEN_WIDTH, 100))
            pygame.draw.line(screen, (255, 215, 0), (0, 100), (SCREEN_WIDTH, 100), 4)
            txt_lvl = f_ui.render(f"LEVEL {curr_lvl + 1}/{len(LEVELS)}", True, COLOR_TEXT_MAIN)
            txt_score = f_ui.render(f"SCORE: {int(score)}", True, COLOR_TEXT_ACCENT)
            col_t = COLOR_TIMER_WARN if time_left < 10 else COLOR_TEXT_MAIN
            txt_time = f_ui.render(f"TIME: {int(time_left)}", True, col_t)
            screen.blit(txt_lvl, (30, 35))
            screen.blit(txt_score, (SCREEN_WIDTH // 2 - txt_score.get_width() // 2, 35))
            screen.blit(txt_time, (SCREEN_WIDTH - 130, 35))
            garland.draw(screen, now)
            for c in cards: c.draw(screen)
            for p in parts: p.draw(screen)

        # 7. Оверлеи и меню
        if state != "PLAY":
            cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

            def draw_text_center(txt, font, y, color):
                r = txt.get_rect(center=(cx, cy + y))
                screen.blit(txt, r)

            if state == "START":
                for i in range(SCREEN_HEIGHT):
                    r = COLOR_TOP[0] + (COLOR_BOTTOM[0] - COLOR_TOP[0]) * i / SCREEN_HEIGHT
                    g = COLOR_TOP[1] + (COLOR_BOTTOM[1] - COLOR_TOP[1]) * i / SCREEN_HEIGHT
                    b = COLOR_TOP[2] + (COLOR_BOTTOM[2] - COLOR_TOP[2]) * i / SCREEN_HEIGHT
                    pygame.draw.line(screen, (r, g, b), (0, i), (SCREEN_WIDTH, i))
                for s in snow: s.draw(screen)
                draw_decorations(screen)
                garland.draw(screen, now)
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((20, 30, 60, 200))
                screen.blit(overlay, (0, 0))
                t1 = f_big.render("WINTER MEMORY", True, (255, 255, 255))
                t2 = f_sub.render("Click to Start", True, (200, 220, 255))
                draw_text_center(t1, f_big, -50, (255, 255, 255))
                draw_text_center(t2, f_sub, 50, (200, 200, 200))

            # --- GAME OVER / LEVEL DONE ---
            elif state == "GAME_OVER" or state == "LEVEL_DONE":
                # 1. Фон
                if blur_bg:
                    screen.blit(blur_bg, (0, 0))
                else:
                    screen.fill(COLOR_TOP)

                # 2. Плавная анимация (float)
                # Используем Quartic Ease-Out для очень плавного торможения
                if anim_progress < 1.0:
                    anim_progress += 0.015  # Скорость анимации (меньше = плавнее)
                    if anim_progress > 1.0: anim_progress = 1.0

                # Функция плавности: 1 - (1-t)^4
                ease = 1 - math.pow(1 - anim_progress, 4)

                # 3. Затемнение фона (до 200, синхронно с анимацией)
                dark_alpha = int(ease * 200)
                darkness = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                darkness.fill((0, 0, 0, dark_alpha))
                screen.blit(darkness, (0, 0))

                current_img = win_image if state == "LEVEL_DONE" else lose_image

                if state == "LEVEL_DONE":
                    if curr_lvl == len(LEVELS) - 1:
                        sub_text = f"Total Score: {int(score)}"
                        hint_text = "Click to Finish"
                    else:
                        sub_text = f"Level Score: {int(score)}"
                        hint_text = "Click for Next Level"
                else:
                    sub_text = f"Final Score: {int(score)}"
                    hint_text = "Click to Restart"

                if current_img:
                    # 4. Pop-up Картинки (Масштаб от 0.6 до 1.0)
                    current_scale = 0.6 + 0.4 * ease

                    if current_scale > 0.1:
                        img_target_w = 480
                        aspect_ratio = current_img.get_height() / current_img.get_width()
                        img_target_h = int(img_target_w * aspect_ratio)

                        final_w = int(img_target_w * current_scale)
                        final_h = int(img_target_h * current_scale)
                        final_img = pygame.transform.smoothscale(current_img, (final_w, final_h))

                        # Делаем картинку полупрозрачной в начале вылета
                        final_img.set_alpha(int(255 * ease))

                        img_rect = final_img.get_rect()
                        # Центрируем выше середины
                        img_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)

                        screen.blit(final_img, img_rect)

                        # 5. Текст (появляется снизу вверх, с прозрачностью)
                        if ease > 0.5:
                            text_alpha = int(255 * ease)

                            # Позиция текста чуть ниже картинки
                            y_start = img_rect.bottom + 45

                            # Счет (Крупно)
                            draw_pro_text(screen, sub_text, f_sub, (SCREEN_WIDTH // 2, y_start), (255, 255, 255))

                            # Разделительная линия (анимация ширины)
                            line_width = int(300 * ease)
                            if line_width > 0:
                                line_surf = pygame.Surface((line_width, 2), pygame.SRCALPHA)
                                line_surf.fill((255, 255, 255, 180))  # Полупрозрачная белая линия
                                line_rect = line_surf.get_rect(center=(SCREEN_WIDTH // 2, y_start + 30))
                                screen.blit(line_surf, line_rect)

                            # Подсказка (Мелко)
                            draw_pro_text(screen, hint_text, f_small, (SCREEN_WIDTH // 2, y_start + 55),
                                          (200, 200, 200))

                else:
                    # Резервный текст (если нет картинок)
                    t1_text = "VICTORY!" if state == "LEVEL_DONE" else "GAME OVER"
                    col = (255, 215, 0) if state == "LEVEL_DONE" else (255, 100, 100)
                    draw_text_center(f_big.render(t1_text, True, col), f_big, -60, col)
                    draw_text_center(f_sub.render(sub_text, True, (255, 255, 255)), f_sub, 20, (255, 255, 255))
                    draw_text_center(f_ui.render(hint_text, True, (200, 200, 200)), f_ui, 80, (200, 200, 200))

        pygame.display.flip()
    return


if __name__ == "__main__":
    run()