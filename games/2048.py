import pygame
import random
import sys
import math
import os
import traceback

# --- КОНФИГУРАЦИЯ ---
WIDTH, HEIGHT = 920, 700
GRID_SIZE = 4
TILE_SIZE = 120
GRID_PADDING = 16
BOARD_SIZE = GRID_SIZE * TILE_SIZE + (GRID_SIZE + 1) * GRID_PADDING

UI_WIDTH = 300
BOARD_START_X = 340
BOARD_START_Y = (HEIGHT - BOARD_SIZE) // 2 + 20

FPS = 60
SLIDE_SPEED = 40
POP_SPEED = 0.15

# --- ПАЛИТРА ---
COLORS = {
    'bg_main': (30, 10, 10),
    'bg_board': (50, 20, 20),
    'slot_empty': (70, 30, 30),
    'slot_border': (90, 40, 40),
    'panel_bg': (60, 20, 20),
    'caramel_text': (225, 160, 70),
    'caramel_border': (180, 110, 40),
    'text_label': (210, 190, 190),
    'text_val': (255, 255, 255),
    'btn_normal': (160, 40, 30),
    'btn_hover': (190, 60, 50),
    'btn_click': (130, 30, 20),
    'shadow': (0, 0, 0, 130)
}

TILE_COLORS = {
    2: (245, 240, 225), 4: (235, 220, 200), 8: (230, 190, 170),
    16: (230, 150, 120), 32: (225, 110, 80), 64: (210, 70, 50),
    128: (220, 170, 80), 256: (200, 140, 50), 512: (180, 60, 40),
    1024: (140, 40, 30), 2048: (255, 200, 60)
}
TEXT_COLORS = {2: (90, 70, 60), 4: (90, 70, 60), 8: (90, 70, 60), 'light': (255, 255, 255)}

TREE_GEN_COLORS = [(10, 30, 15), (20, 50, 25), (30, 70, 30), (50, 90, 45), (70, 110, 60)]
ORNAMENT_COLORS = [(220, 50, 50), (60, 120, 220), (230, 190, 60), (180, 60, 180)]
LIGHT_COLORS = [(255, 60, 60), (80, 255, 80), (80, 200, 255), (255, 210, 80)]
PINE_PALETTE = {'stem': (40, 30, 20), 'base': (20, 55, 25), 'shadow': (10, 30, 15), 'light': (50, 90, 50),
                'snow': (240, 245, 255)}


# --- ПОМОЩНИКИ ---
def get_font(names, size, is_bold=False):
    font_preferences = [n.strip() for n in names.split(',')]
    for font_name in font_preferences:
        try:
            return pygame.font.SysFont(font_name, size, bold=is_bold)
        except:
            continue
    return pygame.font.Font(None, size)


def draw_rounded_rect(surf, rect, color, rad, shadow=5):
    sr = pygame.Rect(rect.x + shadow, rect.y + shadow, rect.w, rect.h)
    ss = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(ss, COLORS['shadow'], ss.get_rect(), border_radius=rad)
    surf.blit(ss, sr)
    pygame.draw.rect(surf, color, rect, border_radius=rad)


# --- КЛАССЫ ДЕКОРА ---

class GiftBox:
    def __init__(self, x, y, w, h, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.ribbon = (255, 215, 0)

    def draw(self, screen):
        shadow = pygame.Surface((self.rect.w + 10, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 60), (0, 0, self.rect.w + 10, 8))
        screen.blit(shadow, (self.rect.x - 5, self.rect.bottom - 4))
        pygame.draw.rect(screen, self.color, self.rect)
        rw = 6
        pygame.draw.rect(screen, self.ribbon, (self.rect.centerx - rw // 2, self.rect.y, rw, self.rect.h))
        pygame.draw.rect(screen, self.ribbon, (self.rect.x, self.rect.centery - 5, self.rect.w, rw))
        pygame.draw.ellipse(screen, self.ribbon, (self.rect.centerx - 8, self.rect.y - 6, 8, 8))
        pygame.draw.ellipse(screen, self.ribbon, (self.rect.centerx, self.rect.y - 6, 8, 8))


class RealisticTree:
    def __init__(self, x, y, height=180, width=130):
        self.x = x;
        self.y = y;
        self.w = width;
        self.h = height
        self.surface = pygame.Surface((width, height + 20), pygame.SRCALPHA)

        # Ствол
        trunk_w, trunk_h = 20, 30
        pygame.draw.rect(self.surface, (60, 40, 20), (width // 2 - trunk_w // 2, height - trunk_h, trunk_w, trunk_h))

        # Генерация хвои (иголки)
        layers = 15
        for i in range(layers):
            progress = i / layers
            layer_y = height - trunk_h - (progress * (height - trunk_h - 20))
            layer_w = width * (1 - progress * 0.8)
            density = int(150 * (1 - progress * 0.5))
            for _ in range(density):
                ox = random.uniform(-layer_w / 2, layer_w / 2)
                oy = random.uniform(-10, 10)
                start_pos = (width // 2 + ox * 0.2, layer_y - 10)
                end_pos = (width // 2 + ox, layer_y + oy + 10)
                dist = abs(ox) / (layer_w / 2) if layer_w > 0 else 0
                idx = min(4, int(dist * 5))
                color = TREE_GEN_COLORS[idx]
                pygame.draw.line(self.surface, color, start_pos, end_pos, 2)
                if random.random() < 0.15 and dist > 0.5:
                    pygame.draw.line(self.surface, (240, 245, 255), end_pos, (end_pos[0], end_pos[1] - 1), 2)

        # --- ИГРУШКИ (ИСПРАВЛЕННАЯ ЛОГИКА) ---
        # Распределяем шарики строго внутри конуса елки
        for _ in range(14):
            # Выбираем случайную высоту (Y) от 40px сверху до низа веток
            ty = random.randint(40, height - 35)

            # Рассчитываем максимальную ширину елки на этой высоте
            # (ty / height) дает прогресс от верха к низу (0..1)
            # Умножаем на половину ширины елки и уменьшаем на 10px для отступа от края
            current_radius = (width / 2) * (ty / height) * 0.8

            if current_radius < 2: continue

            # Случайный сдвиг по X внутри этого радиуса
            ox = random.uniform(-current_radius, current_radius)
            tx = width // 2 + ox

            # Рисуем шарик
            pygame.draw.circle(self.surface, random.choice(ORNAMENT_COLORS), (int(tx), int(ty)), 5)
            # Блик
            pygame.draw.circle(self.surface, (255, 255, 255), (int(tx) - 2, int(ty) - 2), 1)

        # Звезда
        star_x, star_y = width // 2, 15
        pts = []
        for k in range(10):
            ang = math.radians(k * 36 - 90)
            r = 12 if k % 2 == 0 else 5
            pts.append((star_x + math.cos(ang) * r, star_y + math.sin(ang) * r))
        pygame.draw.polygon(self.surface, (255, 215, 0), pts)

    def draw(self, screen):
        shadow_surf = pygame.Surface((self.w, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60), (10, 0, self.w - 20, 15))
        screen.blit(shadow_surf, (self.x, self.y + self.h - 25))
        screen.blit(self.surface, (self.x, self.y))


class SnowDrifts:
    def draw(self, screen):
        pygame.draw.ellipse(screen, (210, 220, 235), (-50, 640, 200, 80))
        pygame.draw.ellipse(screen, (210, 220, 235), (180, 650, 150, 70))
        pygame.draw.ellipse(screen, (245, 248, 255), (20, 660, 280, 90))
        pygame.draw.ellipse(screen, (245, 248, 255), (-80, 670, 200, 60))


class Snowman:
    def __init__(self, x, y): self.x = x; self.y = y

    def draw(self, screen):
        x, y = self.x, self.y
        ss = pygame.Surface((100, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(ss, (0, 0, 0, 60), (0, 0, 100, 20))
        screen.blit(ss, (x - 50, y + 32))
        w, sw = (240, 245, 250), (200, 210, 230)
        pygame.draw.circle(screen, sw, (x + 3, y + 20 + 3), 38);
        pygame.draw.circle(screen, w, (x, y + 20), 38)
        pygame.draw.circle(screen, sw, (x + 2, y - 35 + 2), 28);
        pygame.draw.circle(screen, w, (x, y - 35), 28)
        pygame.draw.circle(screen, sw, (x + 1, y - 75 + 1), 20);
        pygame.draw.circle(screen, w, (x, y - 75), 20)
        pygame.draw.circle(screen, (30, 20, 20), (x - 7, y - 80), 3);
        pygame.draw.circle(screen, (30, 20, 20), (x + 7, y - 80), 3)
        pygame.draw.polygon(screen, (230, 100, 20), [(x, y - 75), (x, y - 70), (x + 15, y - 72)])
        pygame.draw.circle(screen, (40, 20, 20), (x, y - 45), 3);
        pygame.draw.circle(screen, (40, 20, 20), (x, y - 30), 3)
        pygame.draw.line(screen, (60, 40, 20), (x - 25, y - 35), (x - 55, y - 50), 3)
        pygame.draw.line(screen, (60, 40, 20), (x - 55, y - 50), (x - 65, y - 65), 2)
        pygame.draw.line(screen, (60, 40, 20), (x + 25, y - 35), (x + 55, y - 50), 3)
        pygame.draw.line(screen, (60, 40, 20), (x + 55, y - 50), (x + 65, y - 65), 2)
        pygame.draw.rect(screen, COLORS['caramel_text'], (x - 22, y - 60, 44, 10), border_radius=3)
        pygame.draw.rect(screen, COLORS['caramel_text'], (x + 5, y - 55, 12, 30), border_radius=3)
        hat_color = (50, 20, 20)
        pygame.draw.rect(screen, hat_color, (x - 25, y - 92, 50, 6))
        pygame.draw.rect(screen, hat_color, (x - 15, y - 115, 30, 25))
        pygame.draw.rect(screen, COLORS['caramel_border'], (x - 15, y - 97, 30, 5))


class Branch:
    def __init__(self, p0, p1, p2):
        self.layers, self.orn, self.snow = [], [], []
        for i in range(400):
            t = i / 400
            bx = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
            by = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
            ang = math.atan2(2 * (1 - t) * (p1[1] - p0[1]) + 2 * t * (p2[1] - p1[1]),
                             2 * (1 - t) * (p1[0] - p0[0]) + 2 * t * (p2[0] - p1[0]))
            w = 65 * (1 - t * 0.6)
            for _ in range(5):
                l = random.uniform(10, w)
                a = ang + random.uniform(0.7, 1.9) * (1 if random.random() < 0.5 else -1)
                nx, ny = bx + math.cos(a) * l, by + math.sin(a) * l
                c = PINE_PALETTE['base']
                if random.random() < 0.4:
                    c = PINE_PALETTE['shadow']
                elif random.random() > 0.8:
                    c = PINE_PALETTE['light']
                self.layers.append((c, (bx, by), (nx, ny)))
                if random.random() < 0.15:
                    sl = l * 0.4
                    self.snow.append(((nx - math.cos(a) * sl, ny - math.sin(a) * sl), (nx, ny)))
            if random.random() < 0.03:
                self.orn.append(
                    ((bx + math.sin(ang) * 10, by + math.cos(ang) * 15 + 10), random.choice(ORNAMENT_COLORS)))

    def draw(self, s):
        for c, st, en in self.layers: pygame.draw.aaline(s, c, st, en)
        for st, en in self.snow: pygame.draw.line(s, PINE_PALETTE['snow'], st, en, 2)
        for p, c in self.orn:
            pygame.draw.circle(s, c, (int(p[0]), int(p[1])), 6)


class Garland:
    def __init__(self):
        self.b = [{'p': (int(WIDTH / 20 * i), int(-15 + math.sin(i / 20 * math.pi) * 70)), 'c': LIGHT_COLORS[i % 4],
                   'on': True} for i in range(21)]
        self.last = 0

    def update(self):
        if pygame.time.get_ticks() - self.last > 600:
            self.last = pygame.time.get_ticks()
            for b in self.b: b['on'] = not b['on']

    def draw(self, s):
        if len(self.b) > 1: pygame.draw.lines(s, (30, 30, 30), False, [x['p'] for x in self.b], 3)
        for x in self.b:
            pygame.draw.rect(s, (40, 40, 40), (x['p'][0] - 3, x['p'][1] - 6, 6, 6))
            if x['on']:
                gs = pygame.Surface((40, 40), pygame.SRCALPHA)
                pygame.draw.circle(gs, (*x['c'], 50), (20, 20), 16)
                s.blit(gs, (x['p'][0] - 20, x['p'][1] - 10))
                pygame.draw.circle(s, x['c'], (x['p'][0], x['p'][1] + 5), 6)
            else:
                pygame.draw.circle(s, tuple(c // 4 for c in x['c']), (x['p'][0], x['p'][1] + 5), 6)


class Button:
    def __init__(self, r, t, f):
        self.rect = pygame.Rect(r); self.text = t; self.font = f; self.st = 'normal'

    def event(self, e):
        mp = pygame.mouse.get_pos()
        hov = self.rect.collidepoint(mp)
        if e.type == pygame.MOUSEMOTION: self.st = 'hover' if hov else 'normal'
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and hov: self.st = 'clicked'; return True
        if e.type == pygame.MOUSEBUTTONUP: self.st = 'hover' if hov else 'normal'
        return False

    def draw(self, s):
        c = COLORS['btn_click'] if self.st == 'clicked' else (
            COLORS['btn_hover'] if self.st == 'hover' else COLORS['btn_normal'])
        draw_rounded_rect(s, self.rect, c, 14, 2 if self.st == 'clicked' else 4)
        txt = self.font.render(self.text, True, (255, 255, 255))
        r = txt.get_rect(center=self.rect.center)
        if self.st == 'clicked': r.y += 2
        s.blit(txt, r)


# --- ИГРА ---
class Game2048:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("2048: Exclusive Edition")
        self.clock = pygame.time.Clock()

        f = "times new roman, arial, serif"
        self.ft = get_font(f, 85, True)
        self.fst = get_font(f, 26)
        self.fb = get_font(f, 22, True)
        self.fsl = get_font(f, 18, True)
        self.fsv = get_font(f, 38, True)
        self.fonts_tile = {'l': get_font(f, 70, True), 'm': get_font(f, 55, True), 's': get_font(f, 40, True)}

        self.btn_new = Button((50, 420, 220, 60), "NEW GAME", self.fb)
        self.btn_try = Button((WIDTH // 2 - 120, HEIGHT // 2 + 80, 240, 60), "TRY AGAIN", self.fb)

        self.decor = [
            Garland(),
            Branch((-10, 80), (150, 160), (280, 120)),
            Branch((WIDTH + 10, 80), (WIDTH - 250, 160), (WIDTH - 500, 110))
        ]

        self.drifts = SnowDrifts()
        self.snowman = Snowman(220, 630)
        self.tree = RealisticTree(80, 480, height=190, width=140)

        self.gifts = [
            GiftBox(55, 640, 30, 25, (200, 50, 50)),
            GiftBox(95, 645, 25, 20, (50, 100, 200)),
            GiftBox(125, 655, 35, 30, (50, 150, 50))  # Зеленый подарок опущен ниже
        ]
        self.snow = [
            [random.randint(0, WIDTH), random.randint(-HEIGHT, 0), random.randint(2, 4), random.uniform(0.5, 2)] for _
            in range(100)]

        self.best_score = self.load_best()
        self.init_game()

    def load_best(self):
        try:
            if os.path.exists("highscore.txt"):
                with open("highscore.txt", "r") as f: return int(f.read())
        except:
            pass
        return 0

    def save_best(self):
        try:
            with open("highscore.txt", "w") as f:
                f.write(str(self.best_score))
        except:
            pass

    def init_game(self):
        self.matrix = [[0] * 4 for _ in range(4)]
        self.score = 0;
        self.game_over = False;
        self.fade = 0
        self.anim_state = 'IDLE';
        self.moves = [];
        self.pop_tile = None
        self.add_tile(2)

    def add_tile(self, count=1):
        for _ in range(count):
            empty = [(r, c) for r in range(4) for c in range(4) if self.matrix[r][c] == 0]
            if empty:
                r, c = random.choice(empty)
                val = 4 if random.random() > 0.9 else 2
                self.matrix[r][c] = val
                if self.anim_state != 'IDLE' or count == 1:
                    self.anim_state = 'SPAWN'
                    self.pop_tile = {'r': r, 'c': c, 'val': val, 'scale': 0.1}

    def calculate_moves(self, dx, dy):
        new_mat = [[0] * 4 for _ in range(4)];
        moves = [];
        score_add = 0;
        merged_pos = set()
        r_range = range(4) if dx <= 0 else range(3, -1, -1)
        c_range = range(4) if dy <= 0 else range(3, -1, -1)
        for r in r_range:
            for c in c_range:
                val = self.matrix[r][c]
                if val == 0: continue
                nr, nc = r, c
                while True:
                    next_r, next_c = nr + dx, nc + dy
                    if not (0 <= next_r < 4 and 0 <= next_c < 4): break
                    tv = new_mat[next_r][next_c]
                    if tv == 0:
                        nr, nc = next_r, next_c
                    elif tv == val and (next_r, next_c) not in merged_pos:
                        nr, nc = next_r, next_c;
                        merged_pos.add((nr, nc));
                        score_add += val * 2;
                        new_mat[nr][nc] = val * 2
                        moves.append({'val': val, 'start': (r, c), 'end': (nr, nc), 'pixel_start': self.get_pos(r, c),
                                      'pixel_end': self.get_pos(nr, nc), 'is_merge': True})
                        break
                    else:
                        break
                if (nr, nc) not in merged_pos:
                    new_mat[nr][nc] = val
                    moves.append({'val': val, 'start': (r, c), 'end': (nr, nc), 'pixel_start': self.get_pos(r, c),
                                  'pixel_end': self.get_pos(nr, nc), 'is_merge': False})
        return (new_mat != self.matrix), new_mat, moves, score_add

    def get_pos(self, r, c):
        return (BOARD_START_X + GRID_PADDING + c * (TILE_SIZE + GRID_PADDING),
                BOARD_START_Y + GRID_PADDING + r * (TILE_SIZE + GRID_PADDING))

    def handle_input(self, key):
        if self.anim_state != 'IDLE': return
        dx, dy = 0, 0
        if key == pygame.K_LEFT:
            dy = -1
        elif key == pygame.K_RIGHT:
            dy = 1
        elif key == pygame.K_UP:
            dx = -1
        elif key == pygame.K_DOWN:
            dx = 1
        else:
            return
        changed, new_mat, moves, score_inc = self.calculate_moves(dx, dy)
        if changed:
            self.matrix = [[0] * 4 for _ in range(4)]
            self.future_matrix = new_mat;
            self.moves = moves;
            self.score_buffer = score_inc
            self.anim_state = 'SLIDE';
            self.anim_t = 0

    def update(self):
        for s in self.snow:
            s[1] += s[3]
            if s[1] > HEIGHT: s[1], s[0] = random.randint(-50, -10), random.randint(0, WIDTH)
        self.decor[0].update()
        if self.anim_state == 'SLIDE':
            self.anim_t += (SLIDE_SPEED / (TILE_SIZE + GRID_PADDING))
            if self.anim_t >= 1.0:
                self.anim_t = 1.0;
                self.anim_state = 'IDLE';
                self.matrix = self.future_matrix;
                self.score += self.score_buffer
                if self.score > self.best_score: self.best_score = self.score; self.save_best()
                self.add_tile()
                if self.check_over(): self.game_over = True
        elif self.anim_state == 'SPAWN':
            if self.pop_tile:
                self.pop_tile['scale'] += POP_SPEED
                if self.pop_tile['scale'] >= 1.0: self.pop_tile[
                    'scale'] = 1.0; self.anim_state = 'IDLE'; self.pop_tile = None

    def check_over(self):
        if any(0 in r for r in self.matrix): return False
        for i in range(4):
            for j in range(3):
                if self.matrix[i][j] == self.matrix[i][j + 1] or self.matrix[j][i] == self.matrix[j + 1][
                    i]: return False
        return True

    def draw_tile(self, x, y, val, scale=1.0):
        if val == 0: return
        size = int(TILE_SIZE * scale);
        offset = (TILE_SIZE - size) // 2
        rect = pygame.Rect(x + offset, y + offset, size, size)
        color = TILE_COLORS.get(val, TILE_COLORS[2048])
        draw_rounded_rect(self.screen, rect, color, int(12 * scale), 4)
        if size > 20:
            f_key = 'l' if val < 100 else ('m' if val < 1000 else 's')
            tc = TEXT_COLORS.get(val, TEXT_COLORS['light'])
            txt = self.fonts_tile[f_key].render(str(val), True, tc)
            self.screen.blit(txt, txt.get_rect(center=rect.center))

    def draw(self):
        self.screen.fill(COLORS['bg_main'])
        for s in self.snow:
            s_surf = pygame.Surface((s[2] * 2, s[2] * 2), pygame.SRCALPHA)
            pygame.draw.circle(s_surf, (255, 255, 255, 100), (s[2], s[2]), s[2])
            self.screen.blit(s_surf, (s[0], s[1]))

        t = self.ft.render("2048", True, COLORS['caramel_text'])
        ts = self.ft.render("2048", True, (0, 0, 0))
        self.screen.blit(ts, (52, 152));
        self.screen.blit(t, (50, 150))
        self.screen.blit(self.fst.render("Exclusive Edition", True, (170, 130, 130)), (55, 245))

        score_rect = pygame.Rect(45, 300, 110, 90)
        draw_rounded_rect(self.screen, score_rect, COLORS['panel_bg'], 18)
        pygame.draw.rect(self.screen, COLORS['caramel_border'], score_rect, 3, 18)
        self.screen.blit(self.fsl.render("SCORE", True, COLORS['text_label']),
                         (score_rect.centerx - 28, score_rect.y + 12))
        sc = self.fsv.render(str(self.score), True, COLORS['text_val'])
        self.screen.blit(sc, (score_rect.centerx - sc.get_width() // 2, score_rect.y + 35))

        best_rect = pygame.Rect(165, 300, 110, 90)
        draw_rounded_rect(self.screen, best_rect, COLORS['panel_bg'], 18)
        pygame.draw.rect(self.screen, COLORS['caramel_border'], best_rect, 3, 18)
        self.screen.blit(self.fsl.render("BEST", True, COLORS['text_label']),
                         (best_rect.centerx - 22, best_rect.y + 12))
        bs = self.fsv.render(str(self.best_score), True, COLORS['text_val'])
        self.screen.blit(bs, (best_rect.centerx - bs.get_width() // 2, best_rect.y + 35))

        self.btn_new.draw(self.screen)
        self.drifts.draw(self.screen)
        self.tree.draw(self.screen)
        for g in self.gifts: g.draw(self.screen)
        self.snowman.draw(self.screen)

        br = pygame.Rect(BOARD_START_X, BOARD_START_Y, BOARD_SIZE, BOARD_SIZE)
        draw_rounded_rect(self.screen, br, COLORS['bg_board'], 18, 8)

        for r in range(4):
            for c in range(4):
                px, py = self.get_pos(r, c)
                pygame.draw.rect(self.screen, COLORS['slot_empty'], (px, py, TILE_SIZE, TILE_SIZE), border_radius=12)
                pygame.draw.rect(self.screen, COLORS['slot_border'], (px, py, TILE_SIZE, TILE_SIZE), 2, 12)

        if self.anim_state == 'SLIDE':
            for m in self.moves:
                sx, sy = m['pixel_start'];
                ex, ey = m['pixel_end'];
                t = self.anim_t
                self.draw_tile(sx + (ex - sx) * t, sy + (ey - sy) * t, m['val'])
        else:
            for r in range(4):
                for c in range(4):
                    val = self.matrix[r][c]
                    if val != 0:
                        scale = 1.0
                        if self.pop_tile and self.pop_tile['r'] == r and self.pop_tile['c'] == c: scale = self.pop_tile[
                            'scale']
                        px, py = self.get_pos(r, c)
                        self.draw_tile(px, py, val, scale)

        for d in self.decor: d.draw(self.screen)

        if self.game_over:
            if self.fade < 210: self.fade += 5
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, self.fade))
            self.screen.blit(ov, (0, 0))
            g = self.ft.render("Game Over", True, COLORS['caramel_text'])
            gs = self.ft.render("Game Over", True, (0, 0, 0))
            gr = g.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
            self.screen.blit(gs, (gr.x + 3, gr.y + 3));
            self.screen.blit(g, gr)
            self.btn_try.draw(self.screen)

    def run(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT or (
                        e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE): pygame.quit(); sys.exit()
                if self.game_over:
                    if self.btn_try.event(e): self.init_game()
                else:
                    if self.btn_new.event(e): self.init_game()
                    if e.type == pygame.KEYDOWN: self.handle_input(e.key)
            self.update();
            self.draw();
            pygame.display.flip();
            self.clock.tick(FPS)


if __name__ == "__main__":
    try:
        Game2048().run()
    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()
        input("Press Enter to exit...")