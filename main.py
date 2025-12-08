# main.py - Главное меню
import subprocess
import sys
import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Новогодний сборник игр")

# Цвета
WHITE = (255, 255, 255)
RED = (200, 50, 50)
GREEN = (50, 150, 50)
BLUE = (50, 50, 200)

font = pygame.font.Font(None, 48)

# Кнопки: (текст, rect, файл игры)
buttons = [
    ("Игра 1: 2048", pygame.Rect(250, 150, 300, 60), "2048.py"),
    ("Игра 2: Santa Ride", pygame.Rect(250, 230, 300, 60), "flappy_bird.py"),
    ("Игра 3: Pairs", pygame.Rect(250, 310, 300, 60), "para.py"),
    ("Игра 4: Sort Water", pygame.Rect(250, 390, 300, 60), "sort_water.py"),
]


def run_game(game_file):
    """Запускает игру как отдельный процесс"""
    pygame.quit()  # Закрываем pygame перед запуском
    subprocess.run([sys.executable, game_file])
    # После закрытия игры — перезапускаем меню
    subprocess.run([sys.executable, "main.py"])
    sys.exit()


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            for text, rect, game_file in buttons:
                if rect.collidepoint(event.pos):
                    run_game(f"games/{game_file}")

    screen.fill((30, 30, 60))  # Тёмно-синий фон

    # Заголовок
    title = font.render("🎄 Новогодние игры 🎄", True, WHITE)
    screen.blit(title, (250, 50))

    # Кнопки
    for text, rect, _ in buttons:
        pygame.draw.rect(screen, GREEN, rect, border_radius=10)
        text_surf = font.render(text, True, WHITE)
        screen.blit(text_surf, (rect.x + 20, rect.y + 15))

    pygame.display.flip()

pygame.quit()
