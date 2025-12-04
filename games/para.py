import pygame
import random
import sys
import math

# --- КОНСТАНТЫ И НАСТРОЙКИ ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 850  # Увеличено, чтобы вместить интерфейс и карты
FPS = 60

# Параметры сетки
ROWS = 4
COLS = 4
CARD_W = 120
CARD_H = 120
GAP = 25 

# Вычисляем размеры сетки и отступы
GRID_W = COLS * CARD_W + (COLS - 1) * GAP
GRID_H = ROWS * CARD_H + (ROWS - 1) * GAP
START_X = (SCREEN_WIDTH - GRID_W) // 2
# Смещаем сетку вниз (+80 пикселей), чтобы оставить место для UI
START_Y = (SCREEN_HEIGHT - GRID_H) // 2 + 50 

# Цветовая палитра (Dark Modern)
COLOR_BG = (30, 30, 40)           # Темный фон
COLOR_UI_BG = (20, 20, 25)        # Фон верхней панели
COLOR_CARD_BACK = (50, 50, 70)    # Рубашка карты
COLOR_CARD_FRONT = (240, 240, 245)# Лицо карты
COLOR_HOVER = (70, 70, 90)        # Цвет при наведении
COLOR_SHADOW = (15, 15, 20)       # Тень

# Палитра фигур (Pastel / Neon)
SHAPE_COLORS = [
    (255, 89, 94),   # Red/Coral
    (255, 202, 58),  # Yellow/Gold
    (138, 201, 38),  # Green
    (25, 130, 196),  # Blue
    (106, 76, 147),  # Purple
    (255, 153, 200), # Pink
    (0, 255, 255),   # Cyan
    (255, 128, 0)    # Orange
]

# --- КЛАССЫ ЭФФЕКТОВ ---

class FloatingText:
    """Всплывающий текст (+100 очков и т.д.)"""
    def __init__(self, x, y, text, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.alpha = 255
        self.font = pygame.font.SysFont("arial", 28, bold=True)
        
    def update(self):
        self.y -= 1.5       # Летит вверх
        self.alpha -= 4     # Исчезает
        if self.alpha < 0: self.alpha = 0
        
    def draw(self, screen):
        if self.alpha > 0:
            text_surf = self.font.render(self.text, True, self.color)
            text_surf.set_alpha(self.alpha)
            screen.blit(text_surf, (int(self.x), int(self.y)))

class Particle:
    """Частицы конфетти при совпадении"""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(4, 8)
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = 255

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 5
        self.size -= 0.1

    def draw(self, screen):
        if self.life > 0 and self.size > 0:
            s = pygame.Surface((int(self.size)*2, int(self.size)*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, self.life), (int(self.size), int(self.size)), int(self.size))
            screen.blit(s, (self.x - self.size, self.y - self.size))

# --- КЛАСС КАРТЫ ---

class Card:
    def __init__(self, r, c, shape_id):
        self.r = r
        self.c = c
        self.shape_id = shape_id
        self.color = SHAPE_COLORS[shape_id]
        
        # Координаты
        self.base_x = START_X + c * (CARD_W + GAP)
        self.base_y = START_Y + r * (CARD_H + GAP)
        self.x = self.base_x
        self.y = self.base_y
        
        self.rect = pygame.Rect(self.x, self.y, CARD_W, CARD_H)
        
        self.is_flipped = False
        self.is_matched = False
        self.hovered = False

    def update(self, mouse_pos):
        # Анимация наведения (подпрыгивание)
        if self.rect.collidepoint(mouse_pos) and not self.is_flipped and not self.is_matched:
            self.hovered = True
            target_y = self.base_y - 8 # Всплывает на 8 пикселей
        else:
            self.hovered = False
            target_y = self.base_y
            
        # Плавное движение (Lerp)
        self.y += (target_y - self.y) * 0.2
        self.rect.y = int(self.y)

    def draw(self, screen):
        # 1. Тень
        shadow_rect = pygame.Rect(self.x + 5, self.y + 5, CARD_W, CARD_H)
        pygame.draw.rect(screen, COLOR_SHADOW, shadow_rect, border_radius=15)

        # 2. Основной фон карты
        if self.is_flipped or self.is_matched:
            # Если совпало - легкий зеленый оттенок, иначе белый
            bg_color = (230, 255, 230) if self.is_matched else COLOR_CARD_FRONT
        else:
            # Рубашка (светлее при наведении)
            bg_color = COLOR_HOVER if self.hovered else COLOR_CARD_BACK
        
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=15)
        
        # 3. Рамка (Золотая, если совпало)
        border_color = (255, 215, 0) if self.is_matched else (200, 200, 200)
        border_w = 4 if self.is_matched else 2
        if not self.is_flipped and not self.is_matched:
            border_color = (60, 60, 80) # Темная рамка для рубашки
            
        pygame.draw.rect(screen, border_color, self.rect, width=border_w, border_radius=15)

        # 4. Контент (Рисунок или Узор рубашки)
        cx, cy = self.rect.centerx, self.rect.centery
        if self.is_flipped or self.is_matched:
            self.draw_shape(screen, cx, cy)
        else:
            self.draw_back_pattern(screen, cx, cy)

    def draw_back_pattern(self, screen, cx, cy):
        # Минималистичный узор на рубашке
        pygame.draw.circle(screen, (65, 65, 85), (cx, cy), 20, 3)
        pygame.draw.line(screen, (65, 65, 85), (cx-10, cy-10), (cx+10, cy+10), 3)
        pygame.draw.line(screen, (65, 65, 85), (cx+10, cy-10), (cx-10, cy+10), 3)

    def draw_shape(self, screen, cx, cy):
        # Процедурная генерация фигур
        radius = 30
        col = self.color
        sid = self.shape_id
        
        if sid == 0: # Круг
            pygame.draw.circle(screen, col, (cx, cy), radius)
        elif sid == 1: # Квадрат
            pygame.draw.rect(screen, col, (cx-25, cy-25, 50, 50))
        elif sid == 2: # Треугольник
            p = [(cx, cy-30), (cx-30, cy+25), (cx+30, cy+25)]
            pygame.draw.polygon(screen, col, p)
        elif sid == 3: # Ромб
            p = [(cx, cy-35), (cx+35, cy), (cx, cy+35), (cx-35, cy)]
            pygame.draw.polygon(screen, col, p)
        elif sid == 4: # Крест
            pygame.draw.rect(screen, col, (cx-8, cy-32, 16, 64))
            pygame.draw.rect(screen, col, (cx-32, cy-8, 64, 16))
        elif sid == 5: # Пончик
            pygame.draw.circle(screen, col, (cx, cy), 32, 10)
        elif sid == 6: # Звезда (линейная)
            for i in range(3):
                angle = math.radians(i * 60)
                x1 = cx + math.cos(angle) * 30
                y1 = cy + math.sin(angle) * 30
                x2 = cx - math.cos(angle) * 30
                y2 = cy - math.sin(angle) * 30
                pygame.draw.line(screen, col, (x1, y1), (x2, y2), 8)
        elif sid == 7: # Гексагон
            pts = []
            for i in range(6):
                a = math.radians(60 * i)
                pts.append((cx + 30 * math.cos(a), cy + 30 * math.sin(a)))
            pygame.draw.polygon(screen, col, pts)

# --- ИНТЕРФЕЙС (HUD) ---

def draw_ui(screen, score, moves, start_time):
    # Верхняя панель
    pygame.draw.rect(screen, COLOR_UI_BG, (0, 0, SCREEN_WIDTH, 90))
    pygame.draw.line(screen, (60, 60, 80), (0, 90), (SCREEN_WIDTH, 90), 2)

    # Шрифты
    font_label = pygame.font.SysFont("arial", 20)
    font_val = pygame.font.SysFont("arial", 36, bold=True)

    # Расчет времени
    elapsed = (pygame.time.get_ticks() - start_time) // 1000
    mins, secs = elapsed // 60, elapsed % 60
    time_str = f"{mins:02}:{secs:02}"

    # Функция для отрисовки блока статистики
    def draw_stat_block(label, value, x, color):
        lbl = font_label.render(label, True, (150, 150, 170))
        val = font_val.render(str(value), True, color)
        screen.blit(lbl, (x, 15))
        screen.blit(val, (x, 40))

    # Отрисовка блоков
    draw_stat_block("SCORE", score, 80, (255, 215, 0))   # Золотой
    draw_stat_block("MOVES", moves, 350, (100, 200, 255))# Синий
    draw_stat_block("TIME", time_str, 620, (200, 200, 200)) # Серый

# --- ОСНОВНОЙ ЦИКЛ ---

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Memory Game: Ultimate Edition")
    clock = pygame.time.Clock()

    # Данные игры
    score = 0
    moves = 0
    game_start_time = pygame.time.get_ticks()
    
    # Генерация колоды
    deck = list(range(8)) * 2
    random.shuffle(deck)
    cards = []
    for r in range(ROWS):
        for c in range(COLS):
            cards.append(Card(r, c, deck.pop()))

    # Списки объектов
    selected_cards = []
    particles = []
    floating_texts = []
    
    wait_start_time = 0
    block_input = False

    running = True
    while running:
        dt = clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()

        # --- СОБЫТИЯ ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Блокируем ввод, если идет проверка пары
                if not block_input:
                    for card in cards:
                        if card.rect.collidepoint(mouse_pos) and not card.is_flipped and not card.is_matched:
                            card.is_flipped = True
                            selected_cards.append(card)
                            
                            if len(selected_cards) == 2:
                                moves += 1
                                block_input = True
                                wait_start_time = pygame.time.get_ticks()

        # --- ЛОГИКА ИГРЫ ---
        if block_input:
            c1, c2 = selected_cards[0], selected_cards[1]
            
            if c1.shape_id == c2.shape_id:
                # --- СОВПАДЕНИЕ ---
                if not c1.is_matched:
                    score += 100
                    c1.is_matched = True
                    c2.is_matched = True
                    
                    # Спавним эффекты (Конфетти)
                    for _ in range(20):
                        particles.append(Particle(c1.rect.centerx, c1.rect.centery, c1.color))
                        particles.append(Particle(c2.rect.centerx, c2.rect.centery, c2.color))
                    
                    # Всплывающий текст
                    floating_texts.append(FloatingText(c1.rect.x, c1.rect.y, "+100", (100, 255, 100)))
                    
                    selected_cards = []
                    block_input = False
            else:
                # --- ОШИБКА ---
                # Ждем 0.8 секунды перед переворотом
                if pygame.time.get_ticks() - wait_start_time > 800:
                    c1.is_flipped = False
                    c2.is_flipped = False
                    
                    # Штраф
                    new_score = score - 10
                    score = max(0, new_score)
                    
                    # Красный текст штрафа
                    floating_texts.append(FloatingText(c2.rect.x, c2.rect.y, "-10", (255, 80, 80)))
                    
                    selected_cards = []
                    block_input = False

        # --- ОБНОВЛЕНИЕ ---
        for c in cards: c.update(mouse_pos)
        
        for p in particles[:]:
            p.update()
            if p.life <= 0: particles.remove(p)
            
        for ft in floating_texts[:]:
            ft.update()
            if ft.alpha <= 0: floating_texts.remove(ft)

        # --- ОТРИСОВКА ---
        screen.fill(COLOR_BG)
        
        # Рисуем UI
        draw_ui(screen, score, moves, game_start_time)
        
        # Рисуем фоновый узор (точки)
        for x in range(0, SCREEN_WIDTH, 40):
            for y in range(100, SCREEN_HEIGHT, 40):
                pygame.draw.circle(screen, (35, 35, 45), (x, y), 2)

        # Карты
        for card in cards: card.draw(screen)
        
        # Эффекты поверх карт
        for p in particles: p.draw(screen)
        for ft in floating_texts: ft.draw(screen)

        # --- ПОБЕДА ---
        if all(c.is_matched for c in cards):
            # Полупрозрачный слой
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0,0))
            
            # Текст
            font_win = pygame.font.SysFont("arial", 80, bold=True)
            font_sub = pygame.font.SysFont("arial", 40)
            
            text_win = font_win.render("YOU WIN!", True, (255, 215, 0))
            text_score = font_sub.render(f"Final Score: {score}", True, (255, 255, 255))
            
            # Пульсация победного текста
            scale = 1 + 0.05 * math.sin(pygame.time.get_ticks() * 0.005)
            w = int(text_win.get_width() * scale)
            h = int(text_win.get_height() * scale)
            scaled_text = pygame.transform.scale(text_win, (w, h))
            
            screen.blit(scaled_text, scaled_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 40)))
            screen.blit(text_score, text_score.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 40)))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
