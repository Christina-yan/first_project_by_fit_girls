import pygame
import random
import sys
import copy
import math

# --- КОНСТАНТЫ ---
WIDTH = 800
HEIGHT = 600
FPS = 60

# Цвета (Winter/Christmas Palette)
C_BG_TOP = (30, 20, 40)  # Темно-фиолетовый
C_BG_BOT = (10, 10, 20)  # Почти черный
C_GLASS_BORDER = (200, 200, 220)
C_GLASS_FILL = (255, 255, 255, 30)  # Полупрозрачность
C_HIGHLIGHT = (255, 255, 255, 100)
C_TEXT = (255, 240, 220)

# Цвета жидкостей (Liquids)
COLORS = {
    0: None,  # Пусто
    1: (220, 20, 60),  # Красный (Berry)
    2: (34, 139, 34),  # Зеленый (Pine)
    3: (255, 215, 0),  # Золотой (Star)
    4: (30, 144, 255),  # Синий (Ice)
    5: (138, 43, 226),  # Фиолетовый (Magic)
    6: (255, 105, 180)  # Розовый (Candy)
}

# Настройки колб
TUBE_WIDTH = 60
TUBE_HEIGHT = 240
BLOCK_HEIGHT = 50  # Высота одного сегмента жидкости
MAX_CAPACITY = 4
GAP = 30

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Christmas Sort Puzzle 🧪🎄")
clock = pygame.time.Clock()

# Шрифты
font_ui = pygame.font.SysFont("Georgia", 24)
font_title = pygame.font.SysFont("Georgia", 50, bold=True)

# --- УРОВНИ (Загадки) ---
# Числа соответствуют цветам в словаре COLORS
LEVELS = [
    # Уровень 1 (Tutorial)
    [
        [1, 2, 1, 2],
        [2, 1, 2, 1],
        [],
    ],
    # Уровень 2
    [
        [1, 2, 3, 1],
        [2, 3, 1, 2],
        [3, 1, 2, 3],
        [],
        []
    ],
    # Уровень 3
    [
        [4, 1, 2, 3],
        [3, 4, 1, 2],
        [2, 3, 4, 1],
        [1, 2, 3, 4],
        [],
        []
    ],
    # Уровень 4
    [
        [1, 5, 2, 3],
        [2, 5, 3, 1],
        [3, 2, 5, 1],
        [5, 1, 2, 3],
        [],
        []
    ],
    # Уровень 5
    [
        [4, 2, 1, 5],
        [3, 5, 1, 4],
        [1, 4, 2, 3],
        [2, 5, 3, 5],
        [3, 2, 4, 1],
        [],
        []
    ],
    # Уровень 6 (Expert)
    [
        [1, 6, 2, 5],
        [4, 3, 5, 2],
        [6, 4, 1, 3],
        [2, 1, 6, 5],
        [5, 2, 3, 4],
        [3, 6, 4, 1],
        [],
        []
    ]
]


# --- КЛАССЫ ---

class Particle:
    """Искры для завершенных колб"""

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
        self.flakes = [{'x': random.randint(0, WIDTH), 'y': random.randint(0, HEIGHT), 's': random.randint(2, 4),
                        'v': random.uniform(0.5, 1.5)} for _ in range(100)]

    def update_draw(self, surface):
        for f in self.flakes:
            f['y'] += f['v']
            f['x'] += math.sin(pygame.time.get_ticks() * 0.001 + f['y']) * 0.3
            if f['y'] > HEIGHT: f['y'] = -10; f['x'] = random.randint(0, WIDTH)

            # Рисуем с альфой
            s = pygame.Surface((f['s'], f['s']), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 255, 150), (f['s'] // 2, f['s'] // 2), f['s'] // 2)
            surface.blit(s, (f['x'], f['y']))


class Tube:
    def __init__(self, x, y, content):
        self.rect = pygame.Rect(x, y, TUBE_WIDTH, TUBE_HEIGHT)
        self.content = list(content)  # Копия списка цветов
        self.selected = False
        self.hover_offset = 0
        self.completed = False
        self.particles = []

    def update(self):
        # Анимация поднятия при выборе
        target_offset = -20 if self.selected else 0
        self.hover_offset += (target_offset - self.hover_offset) * 0.2

        # Проверка завершения
        if not self.completed and len(self.content) == 4 and len(set(self.content)) == 1:
            self.completed = True
            # Салют
            for _ in range(30):
                self.particles.append(Particle(
                    self.rect.centerx, self.rect.top, COLORS[self.content[0]]
                ))

        # Частицы
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

    def draw(self, surface):
        # Смещение отрисовки
        draw_y = self.rect.y + self.hover_offset

        # 1. Рисуем жидкости
        for i, color_idx in enumerate(self.content):
            color = COLORS[color_idx]
            # Координаты блока (рисуем снизу вверх)
            # Индекс 0 - это дно.
            block_y = draw_y + TUBE_HEIGHT - (i + 1) * BLOCK_HEIGHT - 10  # -10 отступ снизу

            # Форма жидкости (закругленная)
            liq_rect = pygame.Rect(self.rect.x + 4, block_y, TUBE_WIDTH - 8, BLOCK_HEIGHT)

            # Скругление зависит от позиции
            border_rad = 0
            if i == 0: border_rad = 15  # Дно
            # Верхний слой всегда чуть скруглен визуально

            # Рисуем сглаженный прямоугольник
            pygame.draw.rect(surface, color, liq_rect, border_radius=10)

            # Блик на жидкости (объем)
            pygame.draw.rect(surface, (255, 255, 255, 50), (liq_rect.x, liq_rect.y, 10, BLOCK_HEIGHT), border_radius=10)

        # 2. Стеклянная колба
        glass_surf = pygame.Surface((TUBE_WIDTH, TUBE_HEIGHT), pygame.SRCALPHA)

        # Тело колбы (заливка)
        pygame.draw.rect(glass_surf, C_GLASS_FILL, (0, 0, TUBE_WIDTH, TUBE_HEIGHT), border_radius=20)

        # Контур
        pygame.draw.rect(glass_surf, C_GLASS_BORDER, (0, 0, TUBE_WIDTH, TUBE_HEIGHT), 3, border_radius=20)

        # Горлышко
        pygame.draw.rect(glass_surf, C_GLASS_BORDER, (0, 0, TUBE_WIDTH, 10), border_radius=5)

        # Блик на стекле (длинный слева)
        pygame.draw.line(glass_surf, C_HIGHLIGHT, (10, 20), (10, TUBE_HEIGHT - 20), 3)

        surface.blit(glass_surf, (self.rect.x, draw_y))

        # 3. Эффект завершения (Пробка/Звезда)
        if self.completed:
            # Рисуем пробку
            cork_rect = pygame.Rect(self.rect.x + 5, draw_y - 10, TUBE_WIDTH - 10, 15)
            pygame.draw.rect(surface, (139, 69, 19), cork_rect, border_radius=3)
            # Частицы
            for p in self.particles:
                p.draw(surface)


class GameManager:
    def __init__(self):
        self.level_idx = 0
        self.load_level(self.level_idx)
        self.snow = SnowManager()
        self.game_won = False

    def load_level(self, idx):
        self.level_idx = idx
        self.tubes = []

        level_data = copy.deepcopy(LEVELS[idx])
        num_tubes = len(level_data)

        # Центрируем колбы
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
            # Расширяем зону клика для удобства
            hitbox = tube.rect.inflate(0, 40)
            if hitbox.collidepoint(pos):
                clicked_idx = i
                break

        if clicked_idx is not None:
            if self.selected_idx is None:
                # Выбор первой колбы
                if self.tubes[clicked_idx].content:  # Нельзя выбрать пустую
                    self.selected_idx = clicked_idx
                    self.tubes[clicked_idx].selected = True
            else:
                # Попытка перемещения
                src = self.selected_idx
                dst = clicked_idx

                if src == dst:
                    # Отмена выбора
                    self.tubes[src].selected = False
                    self.selected_idx = None
                else:
                    # Логика переливания
                    if self.try_pour(src, dst):
                        # Успешно перелили
                        self.tubes[src].selected = False
                        self.selected_idx = None
                        self.check_win()
                    else:
                        # Нельзя перелить -> меняем выбор
                        self.tubes[src].selected = False
                        if self.tubes[dst].content:
                            self.selected_idx = dst
                            self.tubes[dst].selected = True
                        else:
                            self.selected_idx = None

    def try_pour(self, src_idx, dst_idx):
        src = self.tubes[src_idx]
        dst = self.tubes[dst_idx]

        if not src.content: return False  # Откуда лить пусто
        if len(dst.content) >= MAX_CAPACITY: return False  # Куда лить полно

        color_to_move = src.content[-1]  # Верхний цвет

        # Правила:
        # 1. Целевая пустая
        # 2. ИЛИ Верхний цвет целевой совпадает с переливаемым
        if not dst.content or dst.content[-1] == color_to_move:
            # Сколько блоков этого цвета сверху?
            count = 0
            for color in reversed(src.content):
                if color == color_to_move:
                    count += 1
                else:
                    break

            # Сколько места в целевой?
            space = MAX_CAPACITY - len(dst.content)

            # Переливаем столько, сколько влезет
            amount = min(count, space)

            for _ in range(amount):
                dst.content.append(src.content.pop())

            return True

        return False

    def check_win(self):
        # Уровень пройден, если все колбы либо пустые, либо полные одного цвета
        won = True
        for tube in self.tubes:
            if not tube.content: continue  # Пустая - ок
            if len(tube.content) != MAX_CAPACITY: won = False; break  # Неполная - не ок
            if len(set(tube.content)) != 1: won = False; break  # Разноцветная - не ок

        if won:
            self.game_won = True

    def next_level(self):
        if self.level_idx < len(LEVELS) - 1:
            self.load_level(self.level_idx + 1)
        else:
            # Игра пройдена полностью
            self.level_idx = 0
            self.load_level(0)

    def reset_level(self):
        self.load_level(self.level_idx)

    def update(self):
        self.snow.update_draw(screen)
        for tube in self.tubes:
            tube.update()

    def draw(self, surface):
        # Фон
        for i in range(HEIGHT):
            ratio = i / HEIGHT
            color = [C_BG_TOP[j] * (1 - ratio) + C_BG_BOT[j] * ratio for j in range(3)]
            pygame.draw.line(surface, color, (0, i), (WIDTH, i))

        self.snow.update_draw(surface)

        # Заголовок
        title_surf = font_title.render(f"Level {self.level_idx + 1}", True, C_TEXT)
        surface.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 50))

        sub_text = "R: Restart"
        ui_surf = font_ui.render(sub_text, True, (150, 150, 150))
        surface.blit(ui_surf, (WIDTH - 120, 20))

        # Колбы
        for tube in self.tubes:
            tube.draw(surface)

        # Win Screen         to change arina's paint
        if self.game_won:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            surface.blit(overlay, (0, 0))

            win_text = font_title.render("Level Complete!", True, (255, 215, 0))

            next_hint = "Press SPACE for next level"
            if self.level_idx == len(LEVELS) - 1:
                next_hint = "You finished the game! SPACE to replay"

            hint_text = font_ui.render(next_hint, True, C_TEXT)

            surface.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 50))
            surface.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, HEIGHT // 2 + 20))


# --- MAIN LOOP ---
def main():
    game = GameManager()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # ЛКМ
                    game.handle_click(event.pos)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game.reset_level()

                if game.game_won and event.key == pygame.K_SPACE:
                    game.next_level()

        game.update()
        game.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()