import pygame
import random
import sys
import math

# --- НАСТРОЙКИ И ПАЛИТРА ---

# Эстетичная пастельная палитра ("Sakura & Mochi")
THEME = {
    'bg_top': (255, 230, 235),  # Градиент сверху: нежно-розовый
    'bg_bottom': (200, 220, 255),  # Градиент снизу: нежно-голубой
    'panel_bg': (255, 255, 255, 180),  # Полупрозрачный белый (Glassmorphism)
    'grid_bg': (255, 240, 245),
    'text_dark': (90, 80, 90),  # Мягкий темно-серый
    'text_score': (120, 100, 120),
    'button': (255, 182, 193),  # Light Pink
    'button_hover': (255, 160, 180),
    'shadow': (0, 0, 0, 30)  # Мягкая тень
}

# Цвета плиток (Пастельная радуга)
TILE_COLORS = {
    0: (238, 228, 218, 100),  # Пустая
    2: (255, 255, 255),  # Белый
    4: (255, 228, 225),  # MistyRose
    8: (255, 218, 185),  # Peach
    16: (255, 192, 203),  # Pink
    32: (221, 160, 221),  # Plum
    64: (176, 224, 230),  # PowderBlue
    128: (152, 251, 152),  # PaleGreen
    256: (135, 206, 250),  # LightSkyBlue
    512: (255, 250, 205),  # LemonChiffon
    1024: (255, 105, 180),  # HotPink
    2048: (255, 215, 0),  # Gold
}

# Размеры
SCREEN_WIDTH = 450
SCREEN_HEIGHT = 650
GRID_SIZE = 4
TILE_SIZE = 90
GAP = 12
GRID_OFFSET_Y = 180


# --- КЛАССЫ ЭФФЕКТОВ ---

class Particle:
    """Частицы конфетти при слиянии"""

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(3, 6)
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = 255  # Прозрачность

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 8  # Скорость исчезновения
        self.size = max(0, self.size - 0.05)

    def draw(self, surface):
        if self.life > 0:
            s = pygame.Surface((int(self.size) * 2, int(self.size) * 2), pygame.SRCALPHA)
            # Рисуем кружок
            color_with_alpha = list(self.color) + [self.life]
            pygame.draw.circle(s, color_with_alpha, (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (self.x, self.y))


class Button:
    """Красивая кнопка с эффектом нажатия"""

    def __init__(self, text, x, y, w, h, func):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.func = func
        self.hovered = False
        self.shadow_offset = 4

    def draw(self, screen, font):
        # Тень
        shadow_rect = self.rect.copy()
        shadow_rect.x += self.shadow_offset
        shadow_rect.y += self.shadow_offset
        pygame.draw.rect(screen, THEME['shadow'], shadow_rect, border_radius=15)

        # Сама кнопка
        color = THEME['button_hover'] if self.hovered else THEME['button']
        pygame.draw.rect(screen, color, self.rect, border_radius=15)

        # Текст
        txt_surf = font.render(self.text, True, (255, 255, 255))
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        screen.blit(txt_surf, txt_rect)

    def check_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def check_click(self, mouse_pos):
        if self.hovered:
            self.func()


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("2048: Aesthetic Edition ✨")
        self.clock = pygame.time.Clock()

        # Шрифты (пытаемся найти красивые системные)
        try:
            # Пробуем шрифты в порядке приоритета
            font_name = pygame.font.match_font('segoeui', 'calibri', 'arial')
        except:
            font_name = None

        self.font_lg = pygame.font.Font(font_name, 50)  # Для цифр
        self.font_md = pygame.font.Font(font_name, 32)  # Для заголовка
        self.font_sm = pygame.font.Font(font_name, 20)  # Для UI

        self.particles = []
        self.pop_animations = {}  # Словарь для анимации зума: {(x,y): scale_factor}

        self.score = 0
        self.high_score = 0
        self.matrix = []

        # Кнопка "New Game"
        self.btn_new = Button("New Game", 280, 110, 120, 40, self.reset_game)

        self.reset_game()

    def reset_game(self):
        self.matrix = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.score = 0
        self.add_tile()
        self.add_tile()
        self.game_over = False

    def add_tile(self):
        empty = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if self.matrix[r][c] == 0]
        if empty:
            r, c = random.choice(empty)
            self.matrix[r][c] = 2 if random.random() > 0.1 else 4
            # Запускаем анимацию появления (зум с 0.1 до 1.0)
            self.pop_animations[(r, c)] = 0.5

            # --- ЛОГИКА ИГРЫ (СЖАТАЯ) ---

    def compress(self, mat):
        new_mat = [[0] * 4 for _ in range(4)]
        for i in range(4):
            pos = 0
            for j in range(4):
                if mat[i][j] != 0:
                    new_mat[i][pos] = mat[i][j]
                    pos += 1
        return new_mat

    def merge(self, mat):
        for i in range(4):
            for j in range(3):
                if mat[i][j] != 0 and mat[i][j] == mat[i][j + 1]:
                    mat[i][j] *= 2
                    mat[i][j + 1] = 0
                    self.score += mat[i][j]
                    if self.score > self.high_score: self.high_score = self.score

                    # Эффекты при слиянии
                    self.spawn_particles(i, j, mat[i][j])
                    self.pop_animations[(i, j)] = 1.2  # Tile bump effect
        return mat

    def reverse(self, mat):
        return [row[::-1] for row in mat]

    def transpose(self, mat):
        return [list(row) for row in zip(*mat)]

    def move(self, direction):
        temp = [row[:] for row in self.matrix]
        if direction == 'left':
            temp = self.compress(temp)
            temp = self.merge(temp)
            temp = self.compress(temp)
        elif direction == 'right':
            temp = self.reverse(temp)
            temp = self.compress(temp)
            temp = self.merge(temp)
            temp = self.compress(temp)
            temp = self.reverse(temp)
        elif direction == 'up':
            temp = self.transpose(temp)
            temp = self.compress(temp)
            temp = self.merge(temp)
            temp = self.compress(temp)
            temp = self.transpose(temp)
        elif direction == 'down':
            temp = self.transpose(temp)
            temp = self.reverse(temp)
            temp = self.compress(temp)
            temp = self.merge(temp)
            temp = self.compress(temp)
            temp = self.reverse(temp)
            temp = self.transpose(temp)

        if temp != self.matrix:
            self.matrix = temp
            self.add_tile()

    # --- ВИЗУАЛ И ЭФФЕКТЫ ---

    def spawn_particles(self, r, c, value):
        """Создает взрыв конфетти в координатах плитки"""
        # Координаты на экране
        x = GAP + c * (TILE_SIZE + GAP) + TILE_SIZE // 2
        y = GRID_OFFSET_Y + GAP + r * (TILE_SIZE + GAP) + TILE_SIZE // 2
        color = TILE_COLORS.get(value, (255, 215, 0))

        for _ in range(10):
            self.particles.append(Particle(x, y, color))

    def draw_gradient_bg(self):
        """Рисует вертикальный градиент"""
        # Чтобы не тормозило, рисуем прямоугольники по 2 пикселя высотой
        for y in range(0, SCREEN_HEIGHT, 2):
            ratio = y / SCREEN_HEIGHT
            r = THEME['bg_top'][0] * (1 - ratio) + THEME['bg_bottom'][0] * ratio
            g = THEME['bg_top'][1] * (1 - ratio) + THEME['bg_bottom'][1] * ratio
            b = THEME['bg_top'][2] * (1 - ratio) + THEME['bg_bottom'][2] * ratio
            pygame.draw.rect(self.screen, (int(r), int(g), int(b)), (0, y, SCREEN_WIDTH, 2))

    def draw_ui_panel(self, x, y, title, value):
        """Рисует красивые плашки со счетом"""
        rect = pygame.Rect(x, y, 100, 55)

        # Тень
        shadow = rect.copy()
        shadow.x += 2;
        shadow.y += 2
        pygame.draw.rect(self.screen, THEME['shadow'], shadow, border_radius=12)

        # Фон ("Стекло")
        s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        pygame.draw.rect(s, (255, 255, 255, 200), s.get_rect(), border_radius=12)
        self.screen.blit(s, rect)

        # Текст
        lbl = self.font_sm.render(title, True, (150, 140, 150))
        val = self.font_sm.render(str(value), True, THEME['text_score'])

        self.screen.blit(lbl, (rect.centerx - lbl.get_width() // 2, rect.y + 8))
        self.screen.blit(val, (rect.centerx - val.get_width() // 2, rect.y + 30))

    def draw_grid(self):
        # Подложка под сетку
        grid_rect = pygame.Rect(0, GRID_OFFSET_Y, SCREEN_WIDTH, SCREEN_WIDTH)
        # Полупрозрачный фон сетки
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_WIDTH), pygame.SRCALPHA)
        s.fill((255, 255, 255, 100))
        self.screen.blit(s, (0, GRID_OFFSET_Y))

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                val = self.matrix[r][c]

                x = GAP + c * (TILE_SIZE + GAP) + (SCREEN_WIDTH - (GRID_SIZE * (TILE_SIZE + GAP) + GAP)) // 2
                y = GRID_OFFSET_Y + GAP + r * (TILE_SIZE + GAP)

                # Анимация (Pop effect)
                scale = 1.0
                if (r, c) in self.pop_animations:
                    scale = self.pop_animations[(r, c)]
                    # Возвращаем масштаб к 1.0
                    if scale < 1.0:
                        self.pop_animations[(r, c)] += 0.05
                    elif scale > 1.0:
                        self.pop_animations[(r, c)] -= 0.05

                    if abs(scale - 1.0) < 0.05:
                        del self.pop_animations[(r, c)]
                        scale = 1.0

                # Центрирование для масштабирования
                rect_size = int(TILE_SIZE * scale)
                offset = (TILE_SIZE - rect_size) // 2
                rect = pygame.Rect(x + offset, y + offset, rect_size, rect_size)

                # Цвет
                bg_color = TILE_COLORS.get(val, TILE_COLORS[2048])
                if val == 0: bg_color = (255, 255, 255, 50)  # Прозрачные пустые клетки

                # Рисуем плитку
                if val != 0:
                    # Тень только у активных плиток
                    shadow_rect = rect.copy()
                    shadow_rect.y += 4
                    pygame.draw.rect(self.screen, THEME['shadow'], shadow_rect, border_radius=10)

                # Основной квадрат
                draw_color = bg_color if len(bg_color) == 3 else bg_color
                if len(bg_color) == 4:  # Если есть прозрачность
                    s_tile = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                    pygame.draw.rect(s_tile, bg_color, s_tile.get_rect(), border_radius=10)
                    self.screen.blit(s_tile, rect)
                else:
                    pygame.draw.rect(self.screen, bg_color, rect, border_radius=10)

                # Цифра
                if val != 0:
                    text_col = (80, 80, 80) if val < 8 else (255, 255, 255)
                    txt = self.font_lg.render(str(val), True, text_col)

                    # Если цифра большая, уменьшаем шрифт
                    if val > 512: txt = pygame.transform.scale(txt, (int(rect.w * 0.6), int(rect.h * 0.3)))

                    txt_rect = txt.get_rect(center=rect.center)
                    self.screen.blit(txt, txt_rect)

    def run(self):
        while True:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit();
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.btn_new.check_click(mouse_pos)

                if event.type == pygame.KEYDOWN and not self.game_over:
                    if event.key == pygame.K_LEFT:
                        self.move('left')
                    elif event.key == pygame.K_RIGHT:
                        self.move('right')
                    elif event.key == pygame.K_UP:
                        self.move('up')
                    elif event.key == pygame.K_DOWN:
                        self.move('down')

            # Обновление
            self.btn_new.check_hover(mouse_pos)

            # Отрисовка
            self.draw_gradient_bg()

            # Заголовок
            title_surf = self.font_md.render("2048", True, THEME['text_dark'])
            self.screen.blit(title_surf, (30, 30))
            subtitle_surf = self.font_sm.render("Pastel Edition", True, (150, 150, 150))
            self.screen.blit(subtitle_surf, (32, 75))

            # UI
            self.draw_ui_panel(250, 30, "SCORE", self.score)
            self.draw_ui_panel(360, 30, "BEST", self.high_score)
            self.btn_new.draw(self.screen, self.font_sm)

            # Игровое поле
            self.draw_grid()

            # Частицы
            for p in self.particles[:]:
                p.update()
                p.draw(self.screen)
                if p.life <= 0:
                    self.particles.remove(p)

            if self.game_over:
                pass  # Можно добавить оверлей, но пока просто стоп

            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    Game().run()