import pygame
import random
import sys
import os
import math

# --- КОНСТАНТЫ ---
WIDTH = 550
HEIGHT = 800
FPS = 60

# Палитра (Festive & Elegant)
C_BG_TOP = (10, 15, 40)  # Ночное небо
C_BG_BOT = (50, 65, 100)  # Горизонт
C_MOON = (255, 255, 240)
C_WHITE = (255, 255, 255)

# Цвета Санты и Саней
C_SLEIGH_BODY = (160, 10, 20)  # Темно-красные сани
C_SLEIGH_TRIM = (218, 165, 32)  # Золотая отделка
C_RUNNERS = (192, 192, 192)  # Серебряные полозья
C_SANTA_RED = (220, 20, 60)  # Красная шуба
C_SKIN = (255, 224, 189)  # Цвет кожи
C_BEARD = (245, 245, 245)  # Борода
C_BAG = (139, 69, 19)  # Мешок (коричневый)
C_GIFT_1 = (50, 205, 50)  # Зеленый подарок
C_GIFT_2 = (255, 215, 0)  # Желтый подарок

# Физика
GRAVITY = 0.25
JUMP_FORCE = -6.5
PIPE_SPEED = 3.5
PIPE_GAP = 220  # Чуть шире, так как сани крупнее
PIPE_FREQ = 1600

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Santa's Sleigh Ride 🎅")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 24, bold=True)
font_big = pygame.font.SysFont("Arial", 50, bold=True)


# --- ГРАФИКА ---


def create_detailed_moon(radius):
    size = radius * 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(surf, C_MOON, (radius, radius), radius)
    # Кратеры
    craters = [(15, -10, 12), (-20, 15, 10), (25, 25, 6), (-10, -20, 5)]
    for cx, cy, cr in craters:
        pygame.draw.circle(surf, (230, 230, 220), (radius + cx, radius + cy), cr)
    return surf


def create_santa_sprite():
    """Рисует Санту в санях векторными фигурами"""
    w, h = 90, 70
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    # 1. Полозья (Runners) - снизу
    # Задняя часть полоза
    pygame.draw.line(surf, C_RUNNERS, (10, 60), (80, 60), 3)
    # Завиток спереди
    pygame.draw.arc(surf, C_RUNNERS, (60, 40, 25, 25), 0, 3.14 / 2, 3)
    # Стойки полозьев
    pygame.draw.line(surf, C_RUNNERS, (25, 60), (25, 50), 2)
    pygame.draw.line(surf, C_RUNNERS, (60, 60), (65, 50), 2)

    # 2. Мешок с подарками (Сзади)
    pygame.draw.circle(surf, C_BAG, (25, 35), 14)
    # Торчащие коробки подарков
    pygame.draw.rect(surf, C_GIFT_1, (15, 25, 10, 10))  # Зеленый
    pygame.draw.rect(surf, C_GIFT_2, (28, 22, 8, 8))  # Желтый

    # 3. Тело Саней (The Sleigh)
    # Форма лодки
    points_sleigh = [(10, 35), (15, 55), (75, 55), (85, 35)]
    pygame.draw.polygon(surf, C_SLEIGH_BODY, points_sleigh)
    # Золотая окантовка сверху
    pygame.draw.lines(surf, C_SLEIGH_TRIM, False, [(10, 35), (85, 35)], 4)
    # Декор сбоку
    pygame.draw.line(surf, C_SLEIGH_TRIM, (25, 45), (65, 45), 2)

    # 4. Санта (Тело)
    # Шуба (полукруг)
    pygame.draw.ellipse(surf, C_SANTA_RED, (40, 20, 30, 30))
    # Белый мех на груди
    pygame.draw.line(surf, C_WHITE, (55, 20), (55, 40), 4)

    # 5. Голова Санты
    # Лицо
    pygame.draw.circle(surf, C_SKIN, (55, 18), 9)
    # Розовый нос
    pygame.draw.circle(surf, (255, 180, 180), (58, 19), 3)
    # Глаз
    pygame.draw.circle(surf, (0, 0, 0), (60, 16), 2)

    # 6. Борода (Пышная)
    # Рисуем несколько кругов для объема
    pygame.draw.circle(surf, C_BEARD, (55, 26), 8)  # Центр
    pygame.draw.circle(surf, C_BEARD, (48, 24), 6)  # Слева
    pygame.draw.circle(surf, C_BEARD, (62, 24), 6)  # Справа

    # 7. Шапка
    # Основание
    pygame.draw.ellipse(surf, C_WHITE, (45, 8, 20, 8))
    # Красный колпак (сдувает ветром назад)
    points_hat = [(48, 10), (62, 10), (35, 0)]
    pygame.draw.polygon(surf, C_SANTA_RED, points_hat)
    # Помпон
    pygame.draw.circle(surf, C_WHITE, (35, 0), 4)

    # 8. Рука в варежке (Держит поводья)
    pygame.draw.circle(surf, (50, 150, 50), (65, 35), 5)  # Зеленая варежка

    return surf


# --- КЛАССЫ ---


class SantaPlayer:
    def __init__(self):
        self.original_image = create_santa_sprite()
        # Центрируем чуть левее центра, так как сани длинные
        self.rect = self.original_image.get_rect(center=(120, HEIGHT // 2))
        self.vel = 0
        self.angle = 0
        self.glow_alpha = 0

    def jump(self):
        self.vel = JUMP_FORCE
        self.angle = 10  # Сани тяжелые, угол меньше

    def move(self):
        self.vel += GRAVITY
        self.rect.y += self.vel

        # Вращение (Плавное)
        self.angle -= 1.0
        if self.angle < -20:
            self.angle = -20
        if self.vel < 0:
            self.angle = 10

        if self.rect.top < 0:
            self.rect.top = 0
            self.vel = 0

    def draw(self, surface):
        rotated = pygame.transform.rotate(self.original_image, self.angle)
        new_rect = rotated.get_rect(center=self.rect.center)
        surface.blit(rotated, new_rect.topleft)

        # Магический шлейф за санями (золотая пыль)
        if random.random() < 0.4:
            # Генерируем частицы сзади саней
            offset_x = -30
            offset_y = 10
            px = self.rect.centerx + offset_x
            py = self.rect.centery + offset_y + random.randint(-5, 10)
            pygame.draw.circle(surface, (255, 215, 0), (px, py), random.randint(1, 3))


class CandyPipe:
    def __init__(self, x, gap_y):
        self.x = x
        self.width = 75
        self.gap_y = gap_y
        self.passed = False
        self.top_rect = pygame.Rect(x, 0, self.width, gap_y)
        self.bot_rect = pygame.Rect(
            x, gap_y + PIPE_GAP, self.width, HEIGHT - (gap_y + PIPE_GAP)
        )

    def update(self):
        self.x -= PIPE_SPEED
        self.top_rect.x = self.x
        self.bot_rect.x = self.x

    def draw(self, surface):
        self.draw_cane(surface, self.top_rect)
        self.draw_cane(surface, self.bot_rect)

        # Декор крышек
        cap_h = 24
        self.draw_cap(surface, self.x - 6, self.gap_y - cap_h, self.width + 12, cap_h)
        self.draw_cap(
            surface, self.x - 6, self.gap_y + PIPE_GAP, self.width + 12, cap_h
        )

    def draw_cane(self, surface, rect):
        pygame.draw.rect(surface, (245, 245, 250), rect)
        # Полоски
        clip = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        offset = (pygame.time.get_ticks() // 10) % 60
        for i in range(-60, rect.height + 60, 60):
            pts = [
                (0, i - offset),
                (rect.width, i - offset + 40),
                (rect.width, i - offset + 70),
                (0, i - offset + 30),
            ]
            pygame.draw.polygon(clip, (220, 20, 60), pts)
            pygame.draw.line(clip, (180, 0, 0), pts[0], pts[1], 2)

        # Блик
        pygame.draw.rect(clip, (255, 255, 255, 80), (8, 0, 12, rect.height))
        surface.blit(clip, rect.topleft)
        pygame.draw.rect(surface, (80, 80, 80), rect, 2)

    def draw_cap(self, surface, x, y, w, h):
        r = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surface, (220, 20, 60), r, border_radius=8)
        pygame.draw.rect(surface, (80, 80, 80), r, 2, border_radius=8)
        pygame.draw.rect(
            surface, (255, 255, 255, 100), (x + 4, y + 4, w - 8, 6), border_radius=4
        )


class SnowSystem:
    def __init__(self):
        self.flakes = []
        for _ in range(120):
            self.flakes.append(self.new_flake(True))

    def new_flake(self, random_y=False):
        return {
            "x": random.randint(0, WIDTH),
            "y": random.randint(0, HEIGHT) if random_y else -10,
            "r": random.uniform(1, 4),
            "speed": random.uniform(1, 3.5),
            "off": random.uniform(0, 6.28),
        }

    def draw(self, surface):
        for f in self.flakes:
            f["y"] += f["speed"]
            f["x"] += math.sin(pygame.time.get_ticks() * 0.002 + f["off"]) * 0.5
            if f["y"] > HEIGHT:
                new = self.new_flake()
                f["x"], f["y"] = new["x"], new["y"]

            alpha = int(180 * (f["r"] / 4))
            s = pygame.Surface((int(f["r"] * 2), int(f["r"] * 2)), pygame.SRCALPHA)
            pygame.draw.circle(
                s, (255, 255, 255, alpha), (int(f["r"]), int(f["r"])), int(f["r"])
            )
            surface.blit(s, (f["x"], f["y"]))


# --- MAIN ---


def main():
    moon_img = create_detailed_moon(80)
    high_score = 0
    if os.path.exists("santa_score.txt"):
        try:
            with open("santa_score.txt", "r") as f:
                high_score = int(f.read())
        except:
            pass

    while True:
        santa = SantaPlayer()
        pipes = []
        snow = SnowSystem()
        score = 0
        last_pipe = pygame.time.get_ticks()
        game_active = False
        game_over = False

        while True:
            # ФОН
            screen.fill(C_BG_TOP)
            # Градиент
            for i in range(0, HEIGHT, 5):
                ratio = i / HEIGHT
                color = [
                    C_BG_TOP[j] * (1 - ratio) + C_BG_BOT[j] * ratio for j in range(3)
                ]
                pygame.draw.rect(screen, color, (0, i, WIDTH, 5))

            # Луна
            glow = pygame.Surface((220, 220), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 255, 255, 15), (110, 110), 110)
            pygame.draw.circle(glow, (255, 255, 255, 30), (110, 110), 90)
            screen.blit(glow, (WIDTH - 220, 30))
            screen.blit(moon_img, (WIDTH - 190, 60))

            snow.draw(screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if not game_active and not game_over:
                        game_active = True
                        santa.jump()
                    elif game_active:
                        santa.jump()
                    elif game_over:
                        break

            if game_active:
                if pygame.time.get_ticks() - last_pipe > PIPE_FREQ:
                    gap = random.randint(150, HEIGHT - 150 - PIPE_GAP)
                    pipes.append(CandyPipe(WIDTH + 50, gap))
                    last_pipe = pygame.time.get_ticks()

                santa.move()

                rem = []
                for p in pipes:
                    p.update()
                    p.draw(screen)
                    if p.x < -100:
                        rem.append(p)
                    # Хитбокс поменьше
                    hb = santa.rect.inflate(-30, -25)
                    if hb.colliderect(p.top_rect) or hb.colliderect(p.bot_rect):
                        game_active = False
                        game_over = True
                    if not p.passed and p.x < santa.rect.x:
                        score += 1
                        p.passed = True
                for r in rem:
                    pipes.remove(r)

                if santa.rect.bottom >= HEIGHT:
                    game_active = False
                    game_over = True

                santa.draw(screen)

                # Счет
                sc_txt = font_big.render(str(score), True, C_WHITE)
                screen.blit(sc_txt, (WIDTH // 2 - sc_txt.get_width() // 2, 100))

            elif not game_active and not game_over:
                santa.rect.y = (
                    HEIGHT // 2 + math.sin(pygame.time.get_ticks() * 0.004) * 15
                )
                santa.draw(screen)
                t = font_big.render("SANTA RIDE", True, C_WHITE)
                s = font.render("Press SPACE", True, (200, 200, 200))
                screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 3))
                screen.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 3 + 60))

            elif game_over:
                for p in pipes:
                    p.draw(screen)
                santa.draw(screen)
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))

                if score > high_score:
                    high_score = score
                    with open("santa_score.txt", "w") as f:
                        f.write(str(high_score))

                panel = pygame.Rect(WIDTH // 2 - 130, HEIGHT // 2 - 110, 260, 220)
                pygame.draw.rect(screen, C_WHITE, panel, border_radius=20)
                pygame.draw.rect(screen, C_SLEIGH_BODY, panel, 4, border_radius=20)

                l1 = font_big.render("GAME OVER", True, C_SLEIGH_BODY)
                l2 = font.render(f"Score: {score}", True, (50, 50, 50))
                l3 = font.render(f"Best: {high_score}", True, (200, 150, 0))
                l4 = font.render("Press SPACE", True, (150, 150, 150))

                screen.blit(l1, (WIDTH // 2 - l1.get_width() // 2, HEIGHT // 2 - 150))
                screen.blit(l2, (WIDTH // 2 - l2.get_width() // 2, HEIGHT // 2 - 50))
                screen.blit(l3, (WIDTH // 2 - l3.get_width() // 2, HEIGHT // 2 - 10))
                screen.blit(l4, (WIDTH // 2 - l4.get_width() // 2, HEIGHT // 2 + 60))

                if pygame.key.get_pressed()[pygame.K_SPACE]:
                    break

            pygame.display.flip()
            clock.tick(FPS)


if __name__ == "__main__":
    main()
