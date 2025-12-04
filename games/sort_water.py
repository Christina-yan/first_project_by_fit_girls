import pygame
import sys
import copy

# --- КОНСТАНТЫ И НАСТРОЙКИ ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Цвета (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)

# Цвета жидкостей
RED = (220, 50, 50)
GREEN = (50, 220, 50)
BLUE = (50, 50, 220)
YELLOW = (220, 220, 50)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

# Словарь для маппинга ID цвета в RGB
COLOR_MAP = {
    1: RED,
    2: GREEN,
    3: BLUE,
    4: YELLOW,
    5: ORANGE,
    6: PURPLE,
    7: CYAN
}

# Размеры пробирок
TUBE_WIDTH = 60
TUBE_HEIGHT = 200
BLOCK_HEIGHT = 45  # Высота одной порции жидкости
MAX_CAPACITY = 4  # Максимум 4 блока в пробирке
SPACING = 20  # Расстояние между пробирками

# --- ДАННЫЕ УРОВНЕЙ ---
# Числа обозначают цвета. Пустой список [] - пустая пробирка.
# Уровни от легкого (мало цветов) к сложному.
levels_data = [
    # Уровень 1: 2 цвета, 3 пробирки (очень просто)
    [
        [1, 2, 1, 2],
        [2, 1, 2, 1],
        []
    ],
    # Уровень 2: 3 цвета, 5 пробирок
    [
        [1, 2, 3, 1],
        [2, 3, 1, 2],
        [3, 1, 2, 3],
        []
    ],
    # Уровень 3: 4 цвета, 6 пробирок
    [
        [4, 1, 2, 3],
        [3, 2, 1, 4],
        [1, 4, 3, 2],
        [2, 3, 4, 1],
        []
    ],
    # Уровень 4: 5 цветов, 7 пробирок
    [
        [1, 5, 2, 3],
        [5, 4, 3, 2],
        [4, 1, 5, 2],
        [3, 2, 1, 4],
        [1, 3, 4, 5],
        []
    ],
    # Уровень 5: 6 цветов, 9 пробирок
    [
        [1, 6, 5, 2],
        [3, 1, 4, 6],
        [5, 2, 1, 3],
        [6, 3, 2, 4],
        [4, 5, 6, 1],
        [2, 4, 3, 5],
        []
    ]
]

# --- ИНИЦИАЛИЗАЦИЯ PYGAME ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sort water")
font_main = pygame.font.SysFont('Arial', 24, bold=True)
font_large = pygame.font.SysFont('Arial', 40, bold=True)
clock = pygame.time.Clock()

# --- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ СОСТОЯНИЯ ---
current_level_index = 0
tubes = []  # Текущее состояние пробирок
selected_tube = -1  # Индекс выбранной пробирки (-1 если ничего не выбрано)
steps = 0  # Количество шагов
game_state = "PLAYING"  # PLAYING, LEVEL_COMPLETE, ALL_COMPLETE


def load_level(level_idx):
    """Загружает данные уровня в глобальную переменную tubes"""
    global tubes, steps, selected_tube, game_state
    if level_idx < len(levels_data):
        # Deep copy, чтобы не менять исходные данные уровней при рестарте
        tubes = copy.deepcopy(levels_data[level_idx])
        steps = 0
        selected_tube = -1
        game_state = "PLAYING"
    else:
        game_state = "ALL_COMPLETE"


def draw_tubes():
    """Отрисовка всех пробирок и жидкости"""
    num_tubes = len(tubes)
    # Вычисляем отступ слева, чтобы центрировать все пробирки
    total_width = num_tubes * TUBE_WIDTH + (num_tubes - 1) * SPACING
    start_x = (SCREEN_WIDTH - total_width) // 2
    start_y = (SCREEN_HEIGHT - TUBE_HEIGHT) // 2

    for i in range(num_tubes):
        tube_x = start_x + i * (TUBE_WIDTH + SPACING)
        tube_y = start_y

        # Если пробирка выбрана, рисуем её чуть выше
        if i == selected_tube:
            tube_y -= 20

        # Рисуем саму пробирку (рамку)
        tube_rect = pygame.Rect(tube_x, tube_y, TUBE_WIDTH, TUBE_HEIGHT)
        pygame.draw.rect(screen, GRAY, tube_rect, 3, border_radius=5)  # Рамка

        # Рисуем жидкость
        # Жидкость хранится [дно, ..., верх]. Рисуем снизу вверх.
        current_tube_data = tubes[i]
        for j, color_id in enumerate(current_tube_data):
            color = COLOR_MAP[color_id]
            # Координаты блока жидкости
            # j=0 (дно) -> рисуем в самом низу пробирки
            block_y = tube_y + TUBE_HEIGHT - (j + 1) * BLOCK_HEIGHT - 5  # -5 отступ от дна рамки

            block_rect = pygame.Rect(tube_x + 5, block_y, TUBE_WIDTH - 10, BLOCK_HEIGHT)

            # Скругление углов для жидкости
            border_r = 0
            if j == 0: border_r = 5  # Скруглить дно нижней жидкости

            pygame.draw.rect(screen, color, block_rect, border_radius=border_r)

            # Небольшая черная обводка для разделения блоков
            pygame.draw.rect(screen, DARK_GRAY, block_rect, 1)


def draw_ui():
    """Отрисовка текста интерфейса"""
    # Уровень
    level_text = font_main.render(f"Уровень: {current_level_index + 1} / {len(levels_data)}", True, BLACK)
    screen.blit(level_text, (20, 20))

    # Шаги
    step_text = font_main.render(f"Шаги: {steps}", True, BLACK)
    screen.blit(step_text, (20, 50))

    # Подсказки
    hint_text = font_main.render("R - Рестарт | Пробел - Следующий уровень (при победе)", True, DARK_GRAY)
    # Центрируем подсказку внизу
    hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
    screen.blit(hint_text, hint_rect)

    # Сообщение о победе
    if game_state == "LEVEL_COMPLETE":
        msg = font_large.render("Уровень пройден! Нажми ПРОБЕЛ", True, GREEN)
        msg_rect = msg.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(msg, msg_rect)
    elif game_state == "ALL_COMPLETE":
        msg = font_large.render("ПОЗДРАВЛЯЕМ! ИГРА ПРОЙДЕНА!", True, ORANGE)
        msg_rect = msg.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(msg, msg_rect)


def get_tube_under_mouse(mouse_pos):
    """Возвращает индекс пробирки под курсором или -1"""
    num_tubes = len(tubes)
    total_width = num_tubes * TUBE_WIDTH + (num_tubes - 1) * SPACING
    start_x = (SCREEN_WIDTH - total_width) // 2
    start_y = (SCREEN_HEIGHT - TUBE_HEIGHT) // 2

    x, y = mouse_pos

    for i in range(num_tubes):
        tube_x = start_x + i * (TUBE_WIDTH + SPACING)
        # Учитываем смещение, если пробирка выбрана
        tube_y = start_y - 20 if i == selected_tube else start_y

        rect = pygame.Rect(tube_x, tube_y, TUBE_WIDTH, TUBE_HEIGHT)
        if rect.collidepoint(x, y):
            return i
    return -1


def check_win_condition():
    """Проверяет, завершен ли уровень"""
    global game_state
    completed_tubes = 0
    for tube in tubes:
        if len(tube) == 0:
            completed_tubes += 1
        elif len(tube) == MAX_CAPACITY:
            # Проверяем, все ли цвета в пробирке одинаковые
            first_color = tube[0]
            if all(color == first_color for color in tube):
                completed_tubes += 1

    if completed_tubes == len(tubes):
        game_state = "LEVEL_COMPLETE"


def handle_click(pos):
    """Логика обработки клика мышью"""
    global selected_tube, steps

    if game_state != "PLAYING":
        return

    clicked_index = get_tube_under_mouse(pos)

    if clicked_index == -1:
        # Клик мимо пробирок - сброс выделения
        selected_tube = -1
        return

    if selected_tube == -1:
        # Если ничего не выбрано, выбираем кликнутую, если она не пуста
        if len(tubes[clicked_index]) > 0:
            selected_tube = clicked_index
    else:
        # Если уже выбрана пробирка
        src = selected_tube
        dst = clicked_index

        if src == dst:
            # Кликнули по той же самой - отмена выделения
            selected_tube = -1
        else:
            # Пытаемся перелить
            if is_valid_move(src, dst):
                pour_liquid(src, dst)
                steps += 1
                check_win_condition()
                selected_tube = -1  # Сброс выделения после хода
            else:
                # Если ход невозможен, просто переключаем выделение на новую (если она не пуста)
                if len(tubes[dst]) > 0:
                    selected_tube = dst
                else:
                    selected_tube = -1


def is_valid_move(src_idx, dst_idx):
    """Проверка правил переливания"""
    src_tube = tubes[src_idx]
    dst_tube = tubes[dst_idx]

    if len(src_tube) == 0:
        return False  # Нечего лить
    if len(dst_tube) >= MAX_CAPACITY:
        return False  # Некуда лить

    # Цвет верхней жидкости в источнике
    src_color = src_tube[-1]

    # Если целевая пуста - можно лить
    if len(dst_tube) == 0:
        return True

    # Если не пуста, цвета должны совпадать
    dst_color = dst_tube[-1]
    if src_color != dst_color:
        return False

    return True


def pour_liquid(src_idx, dst_idx):
    """Переливает жидкость (все блоки одного цвета сверху)"""
    src_tube = tubes[src_idx]
    dst_tube = tubes[dst_idx]

    color_to_move = src_tube[-1]

    # Перемещаем блоки пока:
    # 1. В источнике есть блоки
    # 2. Верхний блок источника того же цвета
    # 3. В приемнике есть место
    while (len(src_tube) > 0 and
           src_tube[-1] == color_to_move and
           len(dst_tube) < MAX_CAPACITY):
        dst_tube.append(src_tube.pop())


# --- ЗАПУСК ПЕРВОГО УРОВНЯ ---
load_level(current_level_index)

# --- ИГРОВОЙ ЦИКЛ ---
running = True
while running:
    # 1. Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Левая кнопка мыши
                handle_click(event.pos)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Рестарт текущего уровня
                load_level(current_level_index)

            if event.key == pygame.K_SPACE:
                # Переход на следующий уровень (если выиграли)
                if game_state == "LEVEL_COMPLETE":
                    current_level_index += 1
                    if current_level_index < len(levels_data):
                        load_level(current_level_index)
                    else:
                        game_state = "ALL_COMPLETE"

    # 2. Отрисовка
    screen.fill(WHITE)  # Фон

    draw_tubes()
    draw_ui()

    # 3. Обновление экрана
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()