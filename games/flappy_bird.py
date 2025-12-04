"""
Версия: 1.0

Управление:
  - SPACE или ЛКМ: прыжок / старт / рестарт
  - ESC: выход из игры
═══════════════════════════════════════════════════════════════════════════════
"""

import pygame
import random
import math
import sys
from dataclasses import dataclass
from typing import List, Tuple


# ═══════════════════════════════════════════════════════════════════════════════
#                              КОНФИГУРАЦИЯ ИГРЫ
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class Config:
    """
    Централизованная конфигурация игры.
    Все параметры легко настраиваются для балансировки геймплея.
    """

    # ─────────────────────────────────────────────────────────────────────────
    # Размеры экрана и производительность
    # ─────────────────────────────────────────────────────────────────────────
    SCREEN_WIDTH: int = 520
    SCREEN_HEIGHT: int = 640
    FPS: int = 60
    TITLE: str = "Flappy Bird"

    # ─────────────────────────────────────────────────────────────────────────
    # Цветовая палитра (Flat Design / Современный минимализм)
    # ─────────────────────────────────────────────────────────────────────────
    # Фон и окружение
    COLOR_SKY_TOP: Tuple[int, int, int] = (142, 218, 251)  # Светло-голубой
    COLOR_SKY_BOTTOM: Tuple[int, int, int] = (107, 185, 240)  # Голубой
    COLOR_GROUND: Tuple[int, int, int] = (222, 184, 135)  # Песочный
    COLOR_GROUND_DARK: Tuple[int, int, int] = (185, 140, 85)  # Темный песок
    COLOR_GRASS: Tuple[int, int, int] = (124, 185, 72)  # Зеленая трава

    # Птица
    COLOR_BIRD_BODY: Tuple[int, int, int] = (255, 218, 68)  # Желтый
    COLOR_BIRD_WING: Tuple[int, int, int] = (245, 171, 53)  # Оранжевый
    COLOR_BIRD_BEAK: Tuple[int, int, int] = (255, 121, 85)  # Коралловый
    COLOR_BIRD_EYE: Tuple[int, int, int] = (255, 255, 255)  # Белый
    COLOR_BIRD_PUPIL: Tuple[int, int, int] = (50, 50, 50)  # Почти черный

    # Трубы
    COLOR_PIPE_MAIN: Tuple[int, int, int] = (92, 175, 95)  # Зеленый
    COLOR_PIPE_DARK: Tuple[int, int, int] = (62, 135, 65)  # Темно-зеленый
    COLOR_PIPE_LIGHT: Tuple[int, int, int] = (122, 205, 125)  # Светло-зеленый
    COLOR_PIPE_BORDER: Tuple[int, int, int] = (52, 115, 55)  # Обводка

    # UI
    COLOR_TEXT_MAIN: Tuple[int, int, int] = (255, 218, 68)  # Желтый текст
    COLOR_TEXT_SHADOW: Tuple[int, int, int] = (80, 80, 80)  # Тень текста
    COLOR_PANEL_BG: Tuple[int, int, int] = (255, 255, 255)  # Фон панели
    COLOR_ACCENT: Tuple[int, int, int] = (255, 121, 85)  # Акцент (коралл)

    # ─────────────────────────────────────────────────────────────────────────
    # Физика птицы (тщательно сбалансировано!)
    # ─────────────────────────────────────────────────────────────────────────
    GRAVITY: float = 0.45  # Гравитация - не слишком жесткая
    JUMP_VELOCITY: float = -8.5  # Сила прыжка (отрицательная = вверх)
    MAX_FALL_SPEED: float = 11.0  # Максимальная скорость падения

    # Вращение птицы
    ROTATION_VELOCITY_FACTOR: float = 4.0  # Насколько скорость влияет на угол
    MAX_ROTATION_UP: float = 30.0  # Максимальный угол "вверх"
    MAX_ROTATION_DOWN: float = -80.0  # Максимальный угол "вниз"
    ROTATION_SMOOTHNESS: float = 0.15  # Плавность вращения (0-1)

    # Размеры и позиция птицы
    BIRD_RADIUS: int = 18  # Радиус птицы
    BIRD_START_X: int = 100  # Начальная позиция X

    # ─────────────────────────────────────────────────────────────────────────
    # Трубы (препятствия)
    # ─────────────────────────────────────────────────────────────────────────
    PIPE_WIDTH: int = 70  # Ширина трубы
    PIPE_GAP: int = 150  # Зазор между верхней и нижней трубой
    PIPE_SPAWN_TIME: int = 1500  # Интервал появления труб (мс)
    PIPE_MIN_HEIGHT: int = 60  # Минимальная высота трубы
    PIPE_CAP_HEIGHT: int = 26  # Высота "козырька" трубы
    PIPE_CAP_OVERHANG: int = 6  # Выступ козырька

    # ─────────────────────────────────────────────────────────────────────────
    # Скорость и прогрессия сложности
    # ─────────────────────────────────────────────────────────────────────────
    INITIAL_SPEED: float = 3.5  # Начальная скорость труб
    SPEED_INCREMENT: float = 0.08  # Прибавка скорости за очко
    MAX_SPEED: float = 7.0  # Максимальная скорость

    # ─────────────────────────────────────────────────────────────────────────
    # Земля
    # ─────────────────────────────────────────────────────────────────────────
    GROUND_HEIGHT: int = 90  # Высота земли

    # ─────────────────────────────────────────────────────────────────────────
    # UI и шрифты
    # ─────────────────────────────────────────────────────────────────────────
    FONT_SIZE_TITLE: int = 56
    FONT_SIZE_SCORE: int = 52
    FONT_SIZE_MEDIUM: int = 32
    FONT_SIZE_SMALL: int = 24


# ═══════════════════════════════════════════════════════════════════════════════
#                              КЛАСС ПТИЦЫ
# ═══════════════════════════════════════════════════════════════════════════════


class Bird:
    """
    Главный персонаж игры - птица.

    Отвечает за:
    - Физику движения (гравитация, прыжок)
    - Вращение в зависимости от направления полета
    - Отрисовку (легко заменить на спрайты)
    - Коллизии
    """

    def __init__(self, config: Config):
        """Инициализация птицы."""
        self.config = config
        self.x: float = config.BIRD_START_X
        self.y: float = config.SCREEN_HEIGHT // 2
        self.velocity: float = 0.0
        self.rotation: float = 0.0
        self.target_rotation: float = 0.0

        # Для анимации крыла
        self.wing_offset: float = 0.0

        # Прямоугольник коллизий
        self.rect: pygame.Rect = self._create_collision_rect()

    def _create_collision_rect(self) -> pygame.Rect:
        """Создание прямоугольника коллизий (чуть меньше визуального размера)."""
        hitbox_size = self.config.BIRD_RADIUS * 1.6
        return pygame.Rect(
            self.x - hitbox_size // 2,
            self.y - hitbox_size // 2,
            hitbox_size,
            hitbox_size * 0.75,  # Немного сплющенный для честности
        )

    def reset(self):
        """Сброс птицы в начальное положение."""
        self.y = self.config.SCREEN_HEIGHT // 2
        self.velocity = 0.0
        self.rotation = 0.0
        self.target_rotation = 0.0

    def jump(self):
        """Прыжок птицы вверх."""
        self.velocity = self.config.JUMP_VELOCITY

    def update(self, dt: float):
        """
        Обновление физики птицы.

        Args:
            dt: Delta time (время кадра в секундах)
        """
        # Применяем гравитацию
        self.velocity += self.config.GRAVITY

        # Ограничиваем максимальную скорость падения
        self.velocity = min(self.velocity, self.config.MAX_FALL_SPEED)

        # Обновляем позицию
        self.y += self.velocity

        # ─────────────────────────────────────────────────────────────────────
        # Вращение птицы
        # ─────────────────────────────────────────────────────────────────────
        # Целевой угол зависит от вертикальной скорости
        self.target_rotation = -self.velocity * self.config.ROTATION_VELOCITY_FACTOR

        # Ограничиваем угол
        self.target_rotation = max(
            self.config.MAX_ROTATION_DOWN,
            min(self.config.MAX_ROTATION_UP, self.target_rotation),
        )

        # Плавная интерполяция к целевому углу
        self.rotation += (
            self.target_rotation - self.rotation
        ) * self.config.ROTATION_SMOOTHNESS

        # Анимация крыла (синусоида)
        self.wing_offset = math.sin(pygame.time.get_ticks() * 0.015) * 3

        # Обновляем rect коллизий
        self.rect = self._create_collision_rect()

    def draw(self, screen: pygame.Surface):
        """
        Отрисовка птицы.

        Сейчас использует примитивы pygame.draw.
        Для замены на спрайты достаточно заменить содержимое этого метода
        на pygame.image.load и blit с поворотом.
        """
        cfg = self.config

        # Создаем поверхность для птицы (с прозрачностью)
        bird_size = cfg.BIRD_RADIUS * 4
        bird_surface = pygame.Surface((bird_size, bird_size), pygame.SRCALPHA)
        center = bird_size // 2

        # ─────────────────────────────────────────────────────────────────────
        # Рисуем части птицы относительно центра поверхности
        # ─────────────────────────────────────────────────────────────────────

        # Тело (основной овал)
        body_rect = pygame.Rect(
            center - cfg.BIRD_RADIUS - 2,
            center - cfg.BIRD_RADIUS + 2,
            cfg.BIRD_RADIUS * 2 + 4,
            cfg.BIRD_RADIUS * 2 - 4,
        )
        pygame.draw.ellipse(bird_surface, cfg.COLOR_BIRD_BODY, body_rect)

        # Крыло (анимированное)
        wing_y = center + int(self.wing_offset)
        wing_rect = pygame.Rect(
            center - cfg.BIRD_RADIUS + 4,
            wing_y - 4,
            cfg.BIRD_RADIUS,
            cfg.BIRD_RADIUS - 2,
        )
        pygame.draw.ellipse(bird_surface, cfg.COLOR_BIRD_WING, wing_rect)

        # Глаз (белок)
        eye_x = center + cfg.BIRD_RADIUS // 2
        eye_y = center - 4
        pygame.draw.circle(bird_surface, cfg.COLOR_BIRD_EYE, (eye_x, eye_y), 8)

        # Зрачок
        pygame.draw.circle(bird_surface, cfg.COLOR_BIRD_PUPIL, (eye_x + 2, eye_y), 4)

        # Клюв (треугольник)
        beak_points = [
            (center + cfg.BIRD_RADIUS, center),
            (center + cfg.BIRD_RADIUS + 14, center + 4),
            (center + cfg.BIRD_RADIUS, center + 8),
        ]
        pygame.draw.polygon(bird_surface, cfg.COLOR_BIRD_BEAK, beak_points)

        # ─────────────────────────────────────────────────────────────────────
        # Поворот и отрисовка на экране
        # ─────────────────────────────────────────────────────────────────────
        rotated_surface = pygame.transform.rotate(bird_surface, self.rotation)
        rotated_rect = rotated_surface.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(rotated_surface, rotated_rect)

    def check_collision_bounds(self, ground_y: int) -> bool:
        """
        Проверка столкновения с границами экрана.

        Returns:
            True если произошло столкновение
        """
        # Столкновение с землей
        if self.y + self.config.BIRD_RADIUS > ground_y:
            return True

        # Столкновение с потолком (более снисходительное)
        if self.y - self.config.BIRD_RADIUS < -20:
            return True

        return False


# ═══════════════════════════════════════════════════════════════════════════════
#                              КЛАСС ТРУБЫ
# ═══════════════════════════════════════════════════════════════════════════════


class Pipe:
    """
    Препятствие - пара труб (верхняя и нижняя).

    Отвечает за:
    - Случайную генерацию позиции прохода
    - Движение справа налево
    - Отрисовку с декоративными элементами
    - Коллизии
    """

    def __init__(self, x: float, config: Config):
        """
        Инициализация трубы.

        Args:
            x: Начальная позиция X (правый край экрана)
            config: Конфигурация игры
        """
        self.config = config
        self.x: float = x
        self.passed: bool = False  # Для подсчета очков

        # Рассчитываем границы для позиции прохода
        playable_height = config.SCREEN_HEIGHT - config.GROUND_HEIGHT
        min_gap_center = config.PIPE_MIN_HEIGHT + config.PIPE_GAP // 2 + 20
        max_gap_center = (
            playable_height - config.PIPE_MIN_HEIGHT - config.PIPE_GAP // 2 - 20
        )

        # Случайная позиция центра прохода
        self.gap_center_y: int = random.randint(min_gap_center, max_gap_center)

        # Создаем rect'ы для коллизий
        self._update_collision_rects()

    def _update_collision_rects(self):
        """Обновление прямоугольников коллизий."""
        cfg = self.config
        half_gap = cfg.PIPE_GAP // 2

        # Верхняя труба
        top_height = self.gap_center_y - half_gap
        self.top_rect = pygame.Rect(int(self.x), 0, cfg.PIPE_WIDTH, top_height)

        # Нижняя труба
        bottom_y = self.gap_center_y + half_gap
        bottom_height = cfg.SCREEN_HEIGHT - bottom_y
        self.bottom_rect = pygame.Rect(
            int(self.x), bottom_y, cfg.PIPE_WIDTH, bottom_height
        )

    def update(self, speed: float):
        """
        Обновление позиции трубы.

        Args:
            speed: Текущая скорость движения
        """
        self.x -= speed
        self._update_collision_rects()

    def draw(self, screen: pygame.Surface):
        """
        Отрисовка пары труб с декоративными элементами.

        Использует примитивы pygame.draw. Легко заменить на спрайты.
        """
        cfg = self.config
        x = int(self.x)
        half_gap = cfg.PIPE_GAP // 2

        top_height = self.gap_center_y - half_gap
        bottom_y = self.gap_center_y + half_gap
        ground_y = cfg.SCREEN_HEIGHT - cfg.GROUND_HEIGHT

        # ─────────────────────────────────────────────────────────────────────
        # ВЕРХНЯЯ ТРУБА
        # ─────────────────────────────────────────────────────────────────────

        # Основное тело
        body_top = pygame.Rect(
            x + 4, 0, cfg.PIPE_WIDTH - 8, top_height - cfg.PIPE_CAP_HEIGHT
        )
        pygame.draw.rect(screen, cfg.COLOR_PIPE_MAIN, body_top)

        # Левый блик (светлая полоса)
        highlight_rect = pygame.Rect(x + 8, 0, 8, top_height - cfg.PIPE_CAP_HEIGHT)
        pygame.draw.rect(screen, cfg.COLOR_PIPE_LIGHT, highlight_rect)

        # Правая тень (темная полоса)
        shadow_rect = pygame.Rect(
            x + cfg.PIPE_WIDTH - 16, 0, 8, top_height - cfg.PIPE_CAP_HEIGHT
        )
        pygame.draw.rect(screen, cfg.COLOR_PIPE_DARK, shadow_rect)

        # Козырек (cap)
        cap_rect = pygame.Rect(
            x - cfg.PIPE_CAP_OVERHANG,
            top_height - cfg.PIPE_CAP_HEIGHT,
            cfg.PIPE_WIDTH + cfg.PIPE_CAP_OVERHANG * 2,
            cfg.PIPE_CAP_HEIGHT,
        )
        pygame.draw.rect(screen, cfg.COLOR_PIPE_MAIN, cap_rect)
        pygame.draw.rect(screen, cfg.COLOR_PIPE_BORDER, cap_rect, 3)

        # Блик на козырьке
        cap_highlight = pygame.Rect(
            x - cfg.PIPE_CAP_OVERHANG + 4,
            top_height - cfg.PIPE_CAP_HEIGHT + 4,
            8,
            cfg.PIPE_CAP_HEIGHT - 8,
        )
        pygame.draw.rect(screen, cfg.COLOR_PIPE_LIGHT, cap_highlight)

        # ─────────────────────────────────────────────────────────────────────
        # НИЖНЯЯ ТРУБА
        # ─────────────────────────────────────────────────────────────────────

        # Козырек
        cap_rect_bottom = pygame.Rect(
            x - cfg.PIPE_CAP_OVERHANG,
            bottom_y,
            cfg.PIPE_WIDTH + cfg.PIPE_CAP_OVERHANG * 2,
            cfg.PIPE_CAP_HEIGHT,
        )
        pygame.draw.rect(screen, cfg.COLOR_PIPE_MAIN, cap_rect_bottom)
        pygame.draw.rect(screen, cfg.COLOR_PIPE_BORDER, cap_rect_bottom, 3)

        # Блик на козырьке
        cap_highlight_bottom = pygame.Rect(
            x - cfg.PIPE_CAP_OVERHANG + 4, bottom_y + 4, 8, cfg.PIPE_CAP_HEIGHT - 8
        )
        pygame.draw.rect(screen, cfg.COLOR_PIPE_LIGHT, cap_highlight_bottom)

        # Основное тело
        body_bottom_y = bottom_y + cfg.PIPE_CAP_HEIGHT
        body_bottom_height = ground_y - body_bottom_y
        body_bottom = pygame.Rect(
            x + 4, body_bottom_y, cfg.PIPE_WIDTH - 8, body_bottom_height
        )
        pygame.draw.rect(screen, cfg.COLOR_PIPE_MAIN, body_bottom)

        # Левый блик
        highlight_bottom = pygame.Rect(x + 8, body_bottom_y, 8, body_bottom_height)
        pygame.draw.rect(screen, cfg.COLOR_PIPE_LIGHT, highlight_bottom)

        # Правая тень
        shadow_bottom = pygame.Rect(
            x + cfg.PIPE_WIDTH - 16, body_bottom_y, 8, body_bottom_height
        )
        pygame.draw.rect(screen, cfg.COLOR_PIPE_DARK, shadow_bottom)

    def is_off_screen(self) -> bool:
        """Проверка, ушла ли труба за левый край экрана."""
        return self.x + self.config.PIPE_WIDTH < 0

    def collides_with(self, bird_rect: pygame.Rect) -> bool:
        """
        Проверка столкновения с птицей.

        Args:
            bird_rect: Прямоугольник коллизий птицы

        Returns:
            True если произошло столкновение
        """
        return self.top_rect.colliderect(bird_rect) or self.bottom_rect.colliderect(
            bird_rect
        )


# ═══════════════════════════════════════════════════════════════════════════════
#                           ОСНОВНОЙ КЛАСС ИГРЫ
# ═══════════════════════════════════════════════════════════════════════════════


class Game:
    """
    Главный класс игры.

    Управляет:
    - Игровым циклом
    - Состояниями (меню, игра, game over)
    - Созданием и обновлением объектов
    - Отрисовкой всех элементов
    - Обработкой ввода
    """

    # Состояния игры
    STATE_MENU = "menu"
    STATE_PLAYING = "playing"
    STATE_GAME_OVER = "game_over"

    def __init__(self):
        """Инициализация игры."""
        # Инициализация Pygame
        pygame.init()
        pygame.mixer.init()  # Для будущих звуков

        # Конфигурация
        self.config = Config()

        # Создание окна
        self.screen = pygame.display.set_mode(
            (self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT)
        )
        pygame.display.set_caption(self.config.TITLE)

        # Часы для контроля FPS
        self.clock = pygame.time.Clock()

        # Шрифты
        self._init_fonts()

        # Игровые объекты
        self.bird = Bird(self.config)
        self.pipes: List[Pipe] = []

        # Игровые переменные
        self.score: int = 0
        self.high_score: int = 0
        self.current_speed: float = self.config.INITIAL_SPEED
        self.state: str = self.STATE_MENU

        # Таймер для спавна труб
        self.pipe_spawn_timer: int = 0

        # Флаг работы игры
        self.running: bool = True

        # Предварительно создаем фон для оптимизации
        self._create_background()

    def _init_fonts(self):
        """Инициализация шрифтов."""
        try:
            # Пытаемся использовать системный шрифт
            self.font_title = pygame.font.SysFont(
                "Arial", self.config.FONT_SIZE_TITLE, bold=True
            )
            self.font_score = pygame.font.SysFont(
                "Arial", self.config.FONT_SIZE_SCORE, bold=True
            )
            self.font_medium = pygame.font.SysFont(
                "Arial", self.config.FONT_SIZE_MEDIUM
            )
            self.font_small = pygame.font.SysFont("Arial", self.config.FONT_SIZE_SMALL)
        except:
            # Fallback на дефолтный шрифт
            self.font_title = pygame.font.Font(None, self.config.FONT_SIZE_TITLE)
            self.font_score = pygame.font.Font(None, self.config.FONT_SIZE_SCORE)
            self.font_medium = pygame.font.Font(None, self.config.FONT_SIZE_MEDIUM)
            self.font_small = pygame.font.Font(None, self.config.FONT_SIZE_SMALL)

    def _create_background(self):
        """Создание фоновой поверхности (для оптимизации)."""
        self.background = pygame.Surface(
            (self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT)
        )

        # Градиент неба
        for y in range(self.config.SCREEN_HEIGHT - self.config.GROUND_HEIGHT):
            ratio = y / (self.config.SCREEN_HEIGHT - self.config.GROUND_HEIGHT)
            r = int(
                self.config.COLOR_SKY_TOP[0]
                + (self.config.COLOR_SKY_BOTTOM[0] - self.config.COLOR_SKY_TOP[0])
                * ratio
            )
            g = int(
                self.config.COLOR_SKY_TOP[1]
                + (self.config.COLOR_SKY_BOTTOM[1] - self.config.COLOR_SKY_TOP[1])
                * ratio
            )
            b = int(
                self.config.COLOR_SKY_TOP[2]
                + (self.config.COLOR_SKY_BOTTOM[2] - self.config.COLOR_SKY_TOP[2])
                * ratio
            )
            pygame.draw.line(
                self.background, (r, g, b), (0, y), (self.config.SCREEN_WIDTH, y)
            )

        # Декоративные облака (простые)
        self._draw_clouds_on_background()

        # Земля
        ground_y = self.config.SCREEN_HEIGHT - self.config.GROUND_HEIGHT
        pygame.draw.rect(
            self.background,
            self.config.COLOR_GROUND,
            (0, ground_y, self.config.SCREEN_WIDTH, self.config.GROUND_HEIGHT),
        )

        # Полоса травы
        pygame.draw.rect(
            self.background,
            self.config.COLOR_GRASS,
            (0, ground_y, self.config.SCREEN_WIDTH, 15),
        )

        # Текстура земли (простые линии)
        for x in range(0, self.config.SCREEN_WIDTH, 30):
            pygame.draw.line(
                self.background,
                self.config.COLOR_GROUND_DARK,
                (x, ground_y + 20),
                (x + 20, ground_y + self.config.GROUND_HEIGHT),
                2,
            )

    def _draw_clouds_on_background(self):
        """Рисуем декоративные облака на фоне."""
        cloud_color = (255, 255, 255, 180)
        cloud_positions = [(50, 80), (200, 120), (350, 60), (100, 200), (300, 180)]

        for x, y in cloud_positions:
            # Каждое облако - группа кругов
            pygame.draw.circle(self.background, (255, 255, 255), (x, y), 25)
            pygame.draw.circle(self.background, (255, 255, 255), (x + 25, y + 5), 20)
            pygame.draw.circle(self.background, (255, 255, 255), (x - 20, y + 5), 18)
            pygame.draw.circle(self.background, (255, 255, 255), (x + 10, y - 10), 15)

    def reset_game(self):
        """Сброс игры для нового раунда."""
        self.bird.reset()
        self.pipes.clear()
        self.score = 0
        self.current_speed = self.config.INITIAL_SPEED
        self.pipe_spawn_timer = 0

    def handle_events(self):
        """Обработка событий ввода."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == self.STATE_PLAYING:
                        self.state = self.STATE_MENU
                    else:
                        self.running = False
                    return

                if event.key == pygame.K_SPACE:
                    self._handle_action()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    self._handle_action()

    def _handle_action(self):
        """Обработка основного действия (пробел/клик)."""
        if self.state == self.STATE_MENU:
            self.state = self.STATE_PLAYING
            self.reset_game()
        elif self.state == self.STATE_PLAYING:
            self.bird.jump()
        elif self.state == self.STATE_GAME_OVER:
            self.state = self.STATE_MENU

    def update(self):
        """Обновление игровой логики."""
        dt = self.clock.get_time() / 1000.0  # Delta time в секундах

        if self.state != self.STATE_PLAYING:
            return

        # ─────────────────────────────────────────────────────────────────────
        # Обновление птицы
        # ─────────────────────────────────────────────────────────────────────
        self.bird.update(dt)

        # Проверка столкновения с границами
        ground_y = self.config.SCREEN_HEIGHT - self.config.GROUND_HEIGHT
        if self.bird.check_collision_bounds(ground_y):
            self._game_over()
            return

        # ─────────────────────────────────────────────────────────────────────
        # Обновление труб
        # ─────────────────────────────────────────────────────────────────────
        for pipe in self.pipes:
            pipe.update(self.current_speed)

            # Проверка столкновения с трубой
            if pipe.collides_with(self.bird.rect):
                self._game_over()
                return

            # Проверка прохождения трубы (начисление очков)
            if not pipe.passed and pipe.x + self.config.PIPE_WIDTH < self.bird.x:
                pipe.passed = True
                self.score += 1

                # Плавное увеличение скорости
                self.current_speed = min(
                    self.config.INITIAL_SPEED
                    + self.score * self.config.SPEED_INCREMENT,
                    self.config.MAX_SPEED,
                )

        # Удаление труб за экраном
        self.pipes = [p for p in self.pipes if not p.is_off_screen()]

        # ─────────────────────────────────────────────────────────────────────
        # Спавн новых труб
        # ─────────────────────────────────────────────────────────────────────
        self.pipe_spawn_timer += self.clock.get_time()
        if self.pipe_spawn_timer >= self.config.PIPE_SPAWN_TIME:
            self._spawn_pipe()
            self.pipe_spawn_timer = 0

    def _spawn_pipe(self):
        """Создание новой пары труб."""
        new_pipe = Pipe(self.config.SCREEN_WIDTH + 50, self.config)
        self.pipes.append(new_pipe)

    def _game_over(self):
        """Обработка окончания игры."""
        self.state = self.STATE_GAME_OVER

        # Обновляем рекорд
        if self.score > self.high_score:
            self.high_score = self.score

    def draw(self):
        """Отрисовка всех игровых элементов."""
        # ─────────────────────────────────────────────────────────────────────
        # Фон
        # ─────────────────────────────────────────────────────────────────────
        self.screen.blit(self.background, (0, 0))

        # ─────────────────────────────────────────────────────────────────────
        # Трубы (рисуем перед землей, чтобы земля была сверху)
        # ─────────────────────────────────────────────────────────────────────
        for pipe in self.pipes:
            pipe.draw(self.screen)

        # ─────────────────────────────────────────────────────────────────────
        # Птица
        # ─────────────────────────────────────────────────────────────────────
        if self.state == self.STATE_MENU:
            # На экране меню - птица покачивается
            original_y = self.bird.y
            self.bird.y += math.sin(pygame.time.get_ticks() * 0.005) * 8
            self.bird.rotation = math.sin(pygame.time.get_ticks() * 0.003) * 10
            self.bird.draw(self.screen)
            self.bird.y = original_y
        else:
            self.bird.draw(self.screen)

        # ─────────────────────────────────────────────────────────────────────
        # UI в зависимости от состояния
        # ─────────────────────────────────────────────────────────────────────
        if self.state == self.STATE_MENU:
            self._draw_menu()
        elif self.state == self.STATE_PLAYING:
            self._draw_score()
        elif self.state == self.STATE_GAME_OVER:
            self._draw_game_over()

        # Обновляем экран
        pygame.display.flip()

    def _draw_text_with_shadow(
        self,
        text: str,
        font: pygame.font.Font,
        color: Tuple[int, int, int],
        center_pos: Tuple[int, int],
        shadow_offset: int = 2,
    ):
        """Отрисовка текста с тенью."""
        # Тень
        shadow_surface = font.render(text, True, self.config.COLOR_TEXT_SHADOW)
        shadow_rect = shadow_surface.get_rect(
            center=(center_pos[0] + shadow_offset, center_pos[1] + shadow_offset)
        )
        self.screen.blit(shadow_surface, shadow_rect)

        # Основной текст
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=center_pos)
        self.screen.blit(text_surface, text_rect)

    def _draw_menu(self):
        """Отрисовка главного меню."""
        center_x = self.config.SCREEN_WIDTH // 2

        # Заголовок
        self._draw_text_with_shadow(
            "FLAPPY BIRD",
            self.font_title,
            self.config.COLOR_TEXT_MAIN,
            (center_x, 120),
            shadow_offset=3,
        )

        # Мигающая подсказка
        if (pygame.time.get_ticks() // 600) % 2:
            self._draw_text_with_shadow(
                "Press SPACE to Start",
                self.font_medium,
                self.config.COLOR_TEXT_MAIN,
                (center_x, 380),
            )

        # Рекорд (если есть)
        if self.high_score > 0:
            self._draw_text_with_shadow(
                f"Best: {self.high_score}",
                self.font_small,
                self.config.COLOR_ACCENT,
                (center_x, 450),
            )

        # Управление
        self._draw_text_with_shadow(
            "SPACE or Click to Flap", self.font_small, (200, 200, 200), (center_x, 520)
        )

    def _draw_score(self):
        """Отрисовка текущего счета во время игры."""
        self._draw_text_with_shadow(
            str(self.score),
            self.font_score,
            self.config.COLOR_TEXT_MAIN,
            (self.config.SCREEN_WIDTH // 2, 60),
            shadow_offset=3,
        )

    def _draw_game_over(self):
        """Отрисовка экрана Game Over."""
        center_x = self.config.SCREEN_WIDTH // 2
        center_y = self.config.SCREEN_HEIGHT // 2

        # Полупрозрачный оверлей
        overlay = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(150)
        self.screen.blit(overlay, (0, 0))

        # Панель с результатами
        panel_width, panel_height = 280, 220
        panel_rect = pygame.Rect(
            center_x - panel_width // 2,
            center_y - panel_height // 2 - 20,
            panel_width,
            panel_height,
        )

        # Фон панели
        pygame.draw.rect(
            self.screen, self.config.COLOR_PANEL_BG, panel_rect, border_radius=15
        )
        pygame.draw.rect(
            self.screen, self.config.COLOR_PIPE_BORDER, panel_rect, 4, border_radius=15
        )

        # Заголовок "GAME OVER"
        go_text = self.font_title.render("GAME OVER", True, self.config.COLOR_ACCENT)
        go_rect = go_text.get_rect(center=(center_x, panel_rect.y + 45))
        self.screen.blit(go_text, go_rect)

        # Линия-разделитель
        pygame.draw.line(
            self.screen,
            self.config.COLOR_PIPE_BORDER,
            (panel_rect.x + 20, panel_rect.y + 80),
            (panel_rect.x + panel_width - 20, panel_rect.y + 80),
            2,
        )

        # Текущий счет
        score_label = self.font_small.render(
            "Score", True, self.config.COLOR_TEXT_SHADOW
        )
        self.screen.blit(
            score_label,
            score_label.get_rect(center=(center_x - 60, panel_rect.y + 110)),
        )

        score_value = self.font_score.render(
            str(self.score), True, self.config.COLOR_ACCENT
        )
        self.screen.blit(
            score_value,
            score_value.get_rect(center=(center_x - 60, panel_rect.y + 150)),
        )

        # Лучший счет
        best_label = self.font_small.render("Best", True, self.config.COLOR_TEXT_SHADOW)
        self.screen.blit(
            best_label, best_label.get_rect(center=(center_x + 60, panel_rect.y + 110))
        )

        best_value = self.font_score.render(
            str(self.high_score), True, self.config.COLOR_PIPE_MAIN
        )
        self.screen.blit(
            best_value, best_value.get_rect(center=(center_x + 60, panel_rect.y + 150))
        )

        # Подсказка рестарта (мигающая)
        if (pygame.time.get_ticks() // 500) % 2:
            restart_text = self.font_small.render(
                "Press SPACE to Continue", True, self.config.COLOR_TEXT_SHADOW
            )
            restart_rect = restart_text.get_rect(
                center=(center_x, panel_rect.y + panel_height - 25)
            )
            self.screen.blit(restart_text, restart_rect)

    def run(self):
        """Главный игровой цикл."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.config.FPS)

        # Корректное завершение
        pygame.quit()
        sys.exit()


# ═══════════════════════════════════════════════════════════════════════════════
#                              ТОЧКА ВХОДА
# ═══════════════════════════════════════════════════════════════════════════════


def main():
    """Главная функция запуска игры."""
    print("=" * 60)
    print("            FLAPPY BIRD")
    print("=" * 60)
    print("Управление:")
    print("  SPACE / ЛКМ  - Прыжок / Старт / Рестарт")
    print("  ESC          - Выход в меню / Выход из игры")
    print("=" * 60)
    print("\nЗапуск игры...")

    game = Game()
    game.run()


if __name__ == "__main__":
    main()
