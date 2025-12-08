import pygame
import random
import sys
import math
import os

# --- КОНСТАНТЫ И НАСТРОЙКИ ---
# Уменьшил размер окна, чтобы всё влезало
SCREEN_WIDTH = 850
SCREEN_HEIGHT = 800 
FPS = 60

# --- ПАЛИТРА "WINTER MORNING" ---
COLOR_TOP = (180, 210, 240)    # Голубой
COLOR_BOTTOM = (255, 255, 255) # Белый
COLOR_UI_BAR = (40, 50, 80)    # Темно-синяя панель
COLOR_TEXT_MAIN = (255, 255, 255)
COLOR_TEXT_ACCENT = (255, 215, 0)
COLOR_TIMER_WARN = (255, 100, 100)

COLOR_CARD_BACK = (200, 40, 50)
COLOR_CARD_BORDER = (255, 255, 255)
COLOR_SHADOW = (150, 160, 180)

LIGHT_COLORS = [
    (255, 60, 60), (60, 255, 60), (255, 220, 50), 
    (50, 150, 255), (255, 100, 255)
]

# --- УРОВНИ ---
LEVELS = [
    {"level": 1, "rows": 2, "cols": 2, "time": 15},
    {"level": 2, "rows": 2, "cols": 4, "time": 30},
    {"level": 3, "rows": 3, "cols": 4, "time": 50},
    {"level": 4, "rows": 4, "cols": 4, "time": 70},
    {"level": 5, "rows": 3, "cols": 6, "time": 90},
]

# Отступы для сетки
GRID_OFFSET_Y = 130 # Место под UI сверху
GRID_MARGIN_BOTTOM = 100 # Место под елку снизу
CARD_W = 0
CARD_H = 0
GAP = 15
START_X = 0
START_Y = 0

# --- АУДИО ---
SOUNDS = {}
def load_sounds():
    pygame.mixer.init()
    files = {
        "flip": ["sounds/flip.wav", "sounds/flip.mp3"],
        "win": ["sounds/win.wav", "sounds/win.mp3"],
        "lose": ["sounds/lose.wav", "sounds/lose.mp3"]
    }
    for name, paths in files.items():
        for path in paths:
            if os.path.exists(path):
                try:
                    SOUNDS[name] = pygame.mixer.Sound(path)
                    SOUNDS[name].set_volume(0.5)
                    break
                except: pass

def play_sfx(name):
    if name in SOUNDS: SOUNDS[name].play()

# --- КАРТИНКИ ---
def load_all_images():
    images = []
    for i in range(1, 16):
        fname = None
        if os.path.exists(f"img/{i}.png"): fname = f"img/{i}.png"
        elif os.path.exists(f"img/{i}.jpg"): fname = f"img/{i}.jpg"
        if fname:
            try: images.append(pygame.image.load(fname))
            except: pass
    
    if len(images) < 9:
        for k in range(len(images), 15):
            s = pygame.Surface((200,200))
            s.fill((random.randint(200,250), 100, 100)) 
            pygame.draw.rect(s, (255,255,255), (0,0,200,200), 5)
            images.append(s)
    return images

ORIGINAL_IMAGES = []

# --- ДЕКОР: ЕЛКА И СУГРОБЫ ---
def draw_decorations(screen):
    # 1. Сугробы (Белые овалы внизу)
    pygame.draw.ellipse(screen, (245, 250, 255), (-100, SCREEN_HEIGHT - 120, SCREEN_WIDTH + 200, 200))
    pygame.draw.ellipse(screen, (255, 255, 255), (SCREEN_WIDTH - 400, SCREEN_HEIGHT - 150, 500, 200))

    # 2. Елочка (Справа внизу)
    tree_x = SCREEN_WIDTH - 100
    tree_y = SCREEN_HEIGHT - 40
    
    # Ствол
    pygame.draw.rect(screen, (100, 60, 30), (tree_x - 10, tree_y - 40, 20, 40))
    
    # Ветки (3 треугольника)
    green = (34, 139, 34)
    # Нижний ярус
    pygame.draw.polygon(screen, green, [(tree_x, tree_y - 110), (tree_x - 60, tree_y - 30), (tree_x + 60, tree_y - 30)])
    # Средний ярус
    pygame.draw.polygon(screen, green, [(tree_x, tree_y - 160), (tree_x - 50, tree_y - 70), (tree_x + 50, tree_y - 70)])
    # Верхний ярус
    pygame.draw.polygon(screen, green, [(tree_x, tree_y - 200), (tree_x - 35, tree_y - 120), (tree_x + 35, tree_y - 120)])
    
    # Шарики на елке
    pygame.draw.circle(screen, (255, 0, 0), (tree_x - 20, tree_y - 60), 5)
    pygame.draw.circle(screen, (255, 215, 0), (tree_x + 15, tree_y - 90), 5)
    pygame.draw.circle(screen, (50, 100, 255), (tree_x - 10, tree_y - 130), 5)
    
    # Звезда
    pygame.draw.circle(screen, (255, 215, 0), (tree_x, tree_y - 200), 8)

# --- ГИРЛЯНДА ---
class Garland:
    def __init__(self):
        self.bulbs = []
        count = 18 
        step = SCREEN_WIDTH / count
        for i in range(count + 1):
            x = i * step
            offset_y = abs(math.sin(i * 0.8)) * 20 
            base_y = 100 # Высота панели
            color = random.choice(LIGHT_COLORS)
            self.bulbs.append({
                'x': x, 'y': base_y + offset_y, 'color': color, 'phase': random.uniform(0, 6.28) 
            })

    def draw(self, screen, time_now):
        if len(self.bulbs) > 1:
            points = [(b['x'], b['y'] - 4) for b in self.bulbs]
            pygame.draw.lines(screen, (40, 50, 60), False, points, 2)

        for b in self.bulbs:
            brightness = (math.sin(time_now * 0.003 + b['phase']) + 1) / 2
            brightness = 0.5 + (brightness * 0.5)
            r, g, bl = b['color']
            
            # Свечение
            glow_r = 6 + int(brightness * 5)
            glow_s = pygame.Surface((glow_r*2, glow_r*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_s, (r, g, bl, int(80 * brightness)), (glow_r, glow_r), glow_r)
            screen.blit(glow_s, (b['x'] - glow_r, b['y'] - glow_r))

            pygame.draw.rect(screen, (30,30,40), (b['x']-2, b['y']-6, 4, 4))
            final_col = (min(255, int(r*brightness+50)), min(255, int(g*brightness+50)), min(255, int(bl*brightness+50)))
            pygame.draw.circle(screen, final_col, (b['x'], b['y']), 4)

# --- ЭФФЕКТЫ ---
class SnowFlake:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(-50, SCREEN_HEIGHT)
        # Увеличил размер
        self.size = random.randint(4, 8)
        self.speed = random.uniform(0.8, 2.0)
        # Сделал белее и заметнее
        self.alpha = random.randint(150, 255)

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = -10
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self, screen):
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, self.alpha), (self.size//2, self.size//2), self.size//2)
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
            s = pygame.Surface((int(self.size)*2, int(self.size)*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 215, 0, self.life), (int(self.size), int(self.size)), int(self.size))
            screen.blit(s, (self.x-self.size, self.y-self.size))

# --- КАРТА ---
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
        else: self.hovered = False

    def draw(self, screen):
        dy = self.y - 8 if self.hovered else self.y
        draw_rect = pygame.Rect(self.x, dy, CARD_W, CARD_H)
        s_surf = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
        pygame.draw.rect(s_surf, (*COLOR_SHADOW, 100), (0,0,CARD_W, CARD_H), border_radius=12)
        screen.blit(s_surf, (self.x+5, dy+5))

        if self.is_flipped or self.is_solved:
            pygame.draw.rect(screen, (255,255,255), draw_rect, border_radius=12)
            if self.image:
                ir = self.image.get_rect(center=draw_rect.center)
                screen.blit(self.image, ir)
            if self.is_solved:
                pygame.draw.rect(screen, (255, 215, 0), draw_rect, width=5, border_radius=12)
            else:
                pygame.draw.rect(screen, (200,200,200), draw_rect, width=2, border_radius=12)
        else:
            col = (220, 50, 60) if self.hovered else COLOR_CARD_BACK
            pygame.draw.rect(screen, col, draw_rect, border_radius=12)
            cx, cy = draw_rect.centerx, draw_rect.centery
            pygame.draw.rect(screen, (255, 215, 0), (cx-CARD_W*0.08, dy, CARD_W*0.16, CARD_H))
            pygame.draw.rect(screen, (255, 215, 0), (self.x, cy-CARD_H*0.08, CARD_W, CARD_H*0.16))
            pygame.draw.rect(screen, (255,255,255), draw_rect, width=2, border_radius=12)

# --- SETUP ---
def setup_level(level_index):
    global CARD_W, CARD_H, START_X, START_Y, GAP
    lvl = LEVELS[level_index]
    rows, cols = lvl["rows"], lvl["cols"]
    
    # Доступное место (учитываем отступ сверху и снизу для декора)
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

# --- MAIN ---
def main():
    global ORIGINAL_IMAGES
    pygame.init()
    load_sounds()
    
    # Окно поменьше
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Winter Memory")
    clock = pygame.time.Clock()
    
    ORIGINAL_IMAGES = load_all_images()
    garland = Garland()
    
    try:
        f_ui = pygame.font.SysFont("arial", 28, bold=True) # Чуть меньше шрифт
        f_big = pygame.font.SysFont("georgia", 70, bold=True)
        f_sub = pygame.font.SysFont("georgia", 36)
    except:
        f_ui = pygame.font.Font(None, 30)
        f_big = pygame.font.Font(None, 70)
        f_sub = pygame.font.Font(None, 36)

    curr_lvl = 0
    cards = []
    time_left = 0
    score = 0
    state = "START"
    sel = []
    parts = []
    # Больше снежинок
    snow = [SnowFlake() for _ in range(180)]
    block = False
    timer_check = 0
    last_time = pygame.time.get_ticks()

    running = True
    while running:
        now = pygame.time.get_ticks()
        dt = (now - last_time) / 1000.0
        last_time = now
        mpos = pygame.mouse.get_pos()
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT: running = False
            
            # === ВЫХОД ПО ESC ===
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
            
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if state == "START":
                    curr_lvl, score = 0, 0
                    cards, time_left = setup_level(curr_lvl)
                    state = "PLAY"
                elif state == "LEVEL_DONE":
                    curr_lvl += 1
                    if curr_lvl >= len(LEVELS):
                        state = "WIN"
                        play_sfx("win")
                    else:
                        cards, time_left = setup_level(curr_lvl)
                        state = "PLAY"
                elif state in ["GAME_OVER", "WIN"]:
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

        for s in snow: s.update()
        
        if state == "PLAY":
            time_left -= dt
            if time_left <= 0:
                time_left = 0
                state = "GAME_OVER"
                play_sfx("lose")
            
            if block and (now - timer_check > 700):
                c1, c2 = sel
                if c1.img_idx == c2.img_idx:
                    c1.is_solved = True
                    c2.is_solved = True
                    score += 100 + int(time_left*2)
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
                play_sfx("win")

        for c in cards: c.update(mpos)
        for p in parts[:]:
            p.update()
            if p.life <= 0: parts.remove(p)

        # --- ОТРИСОВКА ---
        
        # 1. Фон
        for i in range(SCREEN_HEIGHT):
            r = COLOR_TOP[0] + (COLOR_BOTTOM[0] - COLOR_TOP[0]) * i / SCREEN_HEIGHT
            g = COLOR_TOP[1] + (COLOR_BOTTOM[1] - COLOR_TOP[1]) * i / SCREEN_HEIGHT
            b = COLOR_TOP[2] + (COLOR_BOTTOM[2] - COLOR_TOP[2]) * i / SCREEN_HEIGHT
            pygame.draw.line(screen, (r, g, b), (0, i), (SCREEN_WIDTH, i))

        # 2. Снег (Сзади)
        for s in snow: s.draw(screen)

        # 3. ЕЛКА И СУГРОБЫ (Перед снегом, но за картами)
        draw_decorations(screen)

        # 4. UI Панель (Темная полоса)
        pygame.draw.rect(screen, COLOR_UI_BAR, (0, 0, SCREEN_WIDTH, 100))
        pygame.draw.line(screen, (255, 215, 0), (0, 100), (SCREEN_WIDTH, 100), 4)
        
        txt_lvl = f_ui.render(f"LEVEL {curr_lvl+1}/{len(LEVELS)}", True, COLOR_TEXT_MAIN)
        txt_score = f_ui.render(f"SCORE: {int(score)}", True, COLOR_TEXT_ACCENT)
        col_t = COLOR_TIMER_WARN if time_left < 10 else COLOR_TEXT_MAIN
        txt_time = f_ui.render(f"TIME: {int(time_left)}", True, col_t)
        
        # Позиции текста
        screen.blit(txt_lvl, (30, 35))
        screen.blit(txt_score, (SCREEN_WIDTH//2 - txt_score.get_width()//2, 35))
        screen.blit(txt_time, (SCREEN_WIDTH - 130, 35))

        # 5. Гирлянда
        garland.draw(screen, now)

        # 6. Карты
        for c in cards: c.draw(screen)
        for p in parts: p.draw(screen)

        # 7. Окна меню
        if state != "PLAY":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((20, 30, 60, 200))
            screen.blit(overlay, (0,0))
            cx, cy = SCREEN_WIDTH//2, SCREEN_HEIGHT//2
            
            def draw_text_center(txt, font, y, color):
                r = txt.get_rect(center=(cx, cy+y))
                screen.blit(txt, r)

            if state == "START":
                t1 = f_big.render("WINTER MEMORY", True, (255, 255, 255))
                t2 = f_sub.render("Click to Start", True, (200, 220, 255))
                draw_text_center(t1, f_big, -50, (255,255,255))
                draw_text_center(t2, f_sub, 50, (200,200,200))
            
            elif state == "LEVEL_DONE":
                t1 = f_big.render("GOOD JOB!", True, (255, 215, 0))
                t2 = f_sub.render("Click for Next Level", True, (255, 255, 255))
                draw_text_center(t1, f_big, -50, (255,215,0))
                draw_text_center(t2, f_sub, 50, (255,255,255))

            elif state == "GAME_OVER":
                t1 = f_big.render("TIME UP!", True, (255, 100, 100))
                t2 = f_sub.render(f"Score: {int(score)}", True, (255, 255, 255))
                t3 = f_ui.render("Click to Retry", True, (200, 200, 200))
                draw_text_center(t1, f_big, -60, (255,100,100))
                draw_text_center(t2, f_sub, 20, (255,255,255))
                draw_text_center(t3, f_ui, 80, (200,200,200))

            elif state == "WIN":
                pulse = math.sin(now*0.005)*10
                t1 = f_big.render("VICTORY!", True, (255, 215, 0))
                t2 = f_sub.render(f"Total Score: {int(score)}", True, (255, 255, 255))
                draw_text_center(t1, f_big, -50+pulse, (255,215,0))
                draw_text_center(t2, f_sub, 40, (255,255,255))

        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()