import pygame
import random
import sys
import os
import math


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

# --- КОНСТАНТЫ ---
WIDTH = 550
HEIGHT = 700
FPS = 60

os.environ["SDL_VIDEO_CENTERED"] = "1"  # Центрирует окно на экране

# Палитра (Festive & Elegant)
C_BG_TOP = (10, 15, 40)  # Ночное небо
C_BG_BOT = (50, 65, 100)  # Горизонт
C_MOON = (255, 255, 240)
C_WHITE = (255, 255, 255)

# Цвета Санты и Саней
C_SLEIGH_BODY = (150, 20, 30)
C_SLEIGH_TRIM = (218, 165, 32)
C_RUNNERS = (192, 192, 192)
C_SANTA_RED = (220, 20, 60)
C_SKIN = (255, 224, 189)
C_BEARD = (245, 245, 245)
C_BAG = (139, 69, 19)
C_GIFT_1 = (50, 205, 50)
C_GIFT_2 = (255, 215, 0)

# Физика
GRAVITY = 0.25
JUMP_FORCE = -6.5
PIPE_SPEED = 3.5
PIPE_GAP = 220
PIPE_FREQ = 1600

# --- АУДИО ---
SOUNDS = {}


def load_sounds():
    files = {
        "fly": ["santa fly.wav", "santa fly.mp3"],
        "lose": ["break (lose).wav", "break (lose).mp3"],
        "buster": ["santa take buster.wav", "santa take buster.mp3"],
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
                    print(f"Ошибка загрузки звука {sound_path}: {e}")


def play_sfx(name):
    if name in SOUNDS:
        SOUNDS[name].play()


# --- КОНСТАНТЫ БУСТОВ ---
class BoostType:
    INVINCIBILITY = "invincibility"
    SLOW_TIME = "slow_time"
    SHRINK = "shrink"


BOOST_DURATION = 7000

BOOST_SETTINGS = {
    BoostType.INVINCIBILITY: {
        "duration": BOOST_DURATION,
        "color": (100, 200, 255),
        "name": "invincibility",
        "icon": "🛡️",
    },
    BoostType.SLOW_TIME: {
        "duration": BOOST_DURATION,
        "color": (180, 100, 255),
        "name": "slow time",
        "icon": "⏱️",
    },
    BoostType.SHRINK: {
        "duration": BOOST_DURATION,
        "color": (100, 255, 150),
        "name": "shrink",
        "icon": "🔽",
    },
}

SLOW_TIME_FACTOR = 0.4
SHRINK_SCALE = 0.5
ACTIVE_BOOST_TYPES = [BoostType.INVINCIBILITY, BoostType.SLOW_TIME, BoostType.SHRINK]
GIFT_SPAWN_CHANCE = 0.15

# Глобальные переменные
screen = None
clock = None
font = None
font_big = None
font_medium = None
font_small = None


# --- ГРАФИКА ---

def create_detailed_moon(radius):
    size = radius * 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(surf, C_MOON, (radius, radius), radius)
    craters = [(15, -10, 12), (-20, 15, 10), (25, 25, 6), (-10, -20, 5)]
    for cx, cy, cr in craters:
        pygame.draw.circle(surf, (230, 230, 220), (radius + cx, radius + cy), cr)
    return surf


def create_santa_sprite():
    w, h = 90, 70
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    pygame.draw.line(surf, C_RUNNERS, (10, 60), (80, 60), 3)
    pygame.draw.arc(surf, C_RUNNERS, (60, 40, 25, 25), 0, 3.14 / 2, 3)
    pygame.draw.line(surf, C_RUNNERS, (25, 60), (25, 50), 2)
    pygame.draw.line(surf, C_RUNNERS, (60, 60), (65, 50), 2)

    pygame.draw.circle(surf, C_BAG, (25, 35), 14)
    pygame.draw.rect(surf, C_GIFT_1, (15, 25, 10, 10))
    pygame.draw.rect(surf, C_GIFT_2, (28, 22, 8, 8))

    points_sleigh = [(10, 35), (15, 55), (75, 55), (85, 35)]
    pygame.draw.polygon(surf, C_SLEIGH_BODY, points_sleigh)
    pygame.draw.lines(surf, C_SLEIGH_TRIM, False, [(10, 35), (85, 35)], 4)
    pygame.draw.line(surf, C_SLEIGH_TRIM, (25, 45), (65, 45), 2)

    pygame.draw.ellipse(surf, C_SANTA_RED, (40, 20, 30, 30))
    pygame.draw.line(surf, C_WHITE, (55, 20), (55, 40), 4)

    pygame.draw.circle(surf, C_SKIN, (55, 18), 9)
    pygame.draw.circle(surf, (255, 180, 180), (58, 19), 3)
    pygame.draw.circle(surf, (0, 0, 0), (60, 16), 2)

    pygame.draw.circle(surf, C_BEARD, (55, 26), 8)
    pygame.draw.circle(surf, C_BEARD, (48, 24), 6)
    pygame.draw.circle(surf, C_BEARD, (62, 24), 6)

    pygame.draw.ellipse(surf, C_WHITE, (45, 8, 20, 8))
    points_hat = [(48, 10), (62, 10), (35, 0)]
    pygame.draw.polygon(surf, C_SANTA_RED, points_hat)
    pygame.draw.circle(surf, C_WHITE, (35, 0), 4)

    pygame.draw.circle(surf, (50, 150, 50), (65, 35), 5)

    return surf


def draw_garland(surface, y_base, curvature, ticks, inverted=False):
    num_bulbs = 20
    colors = [
        (255, 50, 50),
        (50, 255, 50),
        (255, 215, 0),
        (50, 100, 255),
        (255, 0, 255),
    ]
    wire_points = []
    spacing = WIDTH / (num_bulbs - 1)
    for i in range(num_bulbs):
        x = i * spacing
        nx = (x / WIDTH) * 2 - 1
        sag = curvature * (1 - nx ** 2)
        y = y_base - sag if inverted else y_base + sag
        wire_points.append((x, y))

    if len(wire_points) > 1:
        pygame.draw.lines(surface, (50, 50, 50), False, wire_points, 3)

    for i, (x, y) in enumerate(wire_points):
        base_color = colors[i % len(colors)]
        flash = math.sin(ticks * 0.002 + i * 5)
        intensity = (flash + 1) / 2
        brightness = 0.3 + 0.7 * intensity
        current_color = (
            int(base_color[0] * brightness),
            int(base_color[1] * brightness),
            int(base_color[2] * brightness),
        )
        if brightness > 0.6:
            glow_radius = 15 + int(10 * intensity)
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            glow_color = (*base_color, int(50 * intensity))
            pygame.draw.circle(glow_surf, glow_color, (glow_radius, glow_radius), glow_radius)
            surface.blit(glow_surf, (x - glow_radius, y - glow_radius + (5 if not inverted else -5)))
        socket_y = y - 2 if not inverted else y + 2
        pygame.draw.rect(surface, (40, 40, 40), (x - 4, socket_y, 8, 6))
        bulb_y = y + 6 if not inverted else y - 6
        pygame.draw.circle(surface, current_color, (int(x), int(bulb_y)), 6)
        pygame.draw.circle(surface, (255, 255, 255), (int(x) - 2, int(bulb_y) - 2), 2)


def draw_slow_time_effect(surface):
    vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pulse = (math.sin(pygame.time.get_ticks() * 0.003) + 1) / 2
    alpha = int(30 + 20 * pulse)
    for i in range(50):
        a = int(alpha * (1 - i / 50))
        color = (150, 80, 200, a)
        pygame.draw.rect(vignette, color, (0, i, WIDTH, 1))
        pygame.draw.rect(vignette, color, (0, HEIGHT - 1 - i, WIDTH, 1))
        pygame.draw.rect(vignette, color, (i, 0, 1, HEIGHT))
        pygame.draw.rect(vignette, color, (WIDTH - 1 - i, 0, 1, HEIGHT))
    surface.blit(vignette, (0, 0))


def draw_shrink_effect(surface):
    ticks = pygame.time.get_ticks()
    for i in range(12):
        x = (ticks * 0.03 + i * 60) % (WIDTH + 40) - 20
        y_top = 10 + math.sin(ticks * 0.002 + i) * 5
        y_bot = HEIGHT - 10 + math.sin(ticks * 0.002 + i + 3) * 5
        size = 2 + int(2 * math.sin(ticks * 0.005 + i))
        alpha = int(100 + 50 * math.sin(ticks * 0.004 + i * 2))
        particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surf, (100, 255, 150, alpha), (size, size), size)
        surface.blit(particle_surf, (x - size, y_top - size))
        surface.blit(particle_surf, (x - size, y_bot - size))


# --- СИСТЕМА БУСТОВ ---

class BoostManager:
    def __init__(self):
        self.active_boosts = {}
        self.boost_particles = []

    def add_boost(self, boost_type):
        if boost_type in BOOST_SETTINGS:
            self.active_boosts.clear()
            duration = BOOST_SETTINGS[boost_type]["duration"]
            self.active_boosts[boost_type] = pygame.time.get_ticks() + duration
            self._create_pickup_particles(BOOST_SETTINGS[boost_type]["color"])
            play_sfx("buster")

    def is_active(self, boost_type):
        if boost_type in self.active_boosts:
            if pygame.time.get_ticks() < self.active_boosts[boost_type]:
                return True
            else:
                del self.active_boosts[boost_type]
        return False

    def get_time_factor(self):
        if self.is_active(BoostType.SLOW_TIME):
            return SLOW_TIME_FACTOR
        return 1.0

    def update(self, paused=False):
        if paused:
            return
        current = pygame.time.get_ticks()
        expired = [k for k, v in self.active_boosts.items() if current >= v]
        for k in expired:
            del self.active_boosts[k]
        self._update_particles()

    def _create_pickup_particles(self, color):
        for _ in range(20):
            self.boost_particles.append({
                "x": 120, "y": HEIGHT // 2,
                "vx": random.uniform(-5, 5), "vy": random.uniform(-5, 5),
                "life": 60, "color": color, "size": random.randint(3, 8),
            })

    def _update_particles(self):
        time_factor = self.get_time_factor()
        for p in self.boost_particles[:]:
            p["x"] += p["vx"] * time_factor
            p["y"] += p["vy"] * time_factor
            p["life"] -= 1
            p["size"] = max(1, p["size"] - 0.1)
            if p["life"] <= 0:
                self.boost_particles.remove(p)

    def draw_particles(self, surface):
        for p in self.boost_particles:
            alpha = int(255 * (p["life"] / 60))
            color = (*p["color"][:3], alpha)
            s = pygame.Surface((int(p["size"] * 2), int(p["size"] * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (int(p["size"]), int(p["size"])), int(p["size"]))
            surface.blit(s, (p["x"] - p["size"], p["y"] - p["size"]))

    def draw_ui(self, surface):
        y_offset = 50
        for boost_type, end_time in self.active_boosts.items():
            if boost_type in BOOST_SETTINGS:
                settings = BOOST_SETTINGS[boost_type]
                remaining = max(0, end_time - pygame.time.get_ticks())
                duration = settings["duration"]
                bar_width = 150
                bar_height = 20
                bar_x = 10
                bar_y = y_offset
                pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height), border_radius=5)
                fill_width = int(bar_width * (remaining / duration))
                pygame.draw.rect(surface, settings["color"], (bar_x, bar_y, fill_width, bar_height), border_radius=5)
                pygame.draw.rect(surface, C_WHITE, (bar_x, bar_y, bar_width, bar_height), 2, border_radius=5)
                text = font_small.render(f"{settings['name']}", True, C_WHITE)
                surface.blit(text, (bar_x + bar_width + 10, bar_y))
                break


class GiftBoost:
    GIFT_COLORS = {
        BoostType.INVINCIBILITY: ((100, 180, 255), (200, 230, 255)),
        BoostType.SLOW_TIME: ((180, 100, 255), (230, 180, 255)),
        BoostType.SHRINK: ((100, 255, 150), (180, 255, 200)),
    }

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.base_y = y
        self.size = 35
        self.rect = pygame.Rect(x - self.size // 2, y - self.size // 2, self.size, self.size)
        self.collected = False
        self.boost_type = random.choice(ACTIVE_BOOST_TYPES)
        self.bob_offset = random.uniform(0, 6.28)
        self.rotation = 0
        self.glow_phase = random.uniform(0, 6.28)

    def update(self, pipe_speed):
        if self.collected:
            return
        self.x -= pipe_speed
        bob = math.sin(pygame.time.get_ticks() * 0.005 + self.bob_offset) * 8
        self.y = self.base_y + bob
        self.rotation = math.sin(pygame.time.get_ticks() * 0.003 + self.bob_offset) * 10
        self.rect.x = self.x - self.size // 2
        self.rect.y = self.y - self.size // 2

    def draw(self, surface):
        if self.collected:
            return
        colors = self.GIFT_COLORS.get(self.boost_type, ((255, 50, 50), (255, 150, 150)))
        main_color, ribbon_color = colors
        glow_intensity = (math.sin(pygame.time.get_ticks() * 0.008 + self.glow_phase) + 1) / 2
        glow_radius = int(self.size + 15 * glow_intensity)
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        glow_alpha = int(80 * glow_intensity)
        pygame.draw.circle(glow_surf, (*main_color, glow_alpha), (glow_radius, glow_radius), glow_radius)
        surface.blit(glow_surf, (self.x - glow_radius, self.y - glow_radius))

        gift_surf = pygame.Surface((self.size + 10, self.size + 10), pygame.SRCALPHA)
        center = (self.size + 10) // 2
        box_rect = pygame.Rect(5, 8, self.size, self.size - 5)
        pygame.draw.rect(gift_surf, main_color, box_rect, border_radius=4)
        pygame.draw.rect(gift_surf, (50, 50, 50), box_rect, 2, border_radius=4)
        pygame.draw.rect(gift_surf, ribbon_color, (center - 4, 8, 8, self.size - 5))
        pygame.draw.rect(gift_surf, ribbon_color, (5, center - 2, self.size, 6))

        rotated = pygame.transform.rotate(gift_surf, self.rotation)
        rot_rect = rotated.get_rect(center=(self.x, self.y))
        surface.blit(rotated, rot_rect.topleft)

    def check_collision(self, player_rect):
        if self.collected:
            return False
        expanded_rect = player_rect.inflate(10, 10)
        return self.rect.colliderect(expanded_rect)

    def collect(self):
        self.collected = True
        return self.boost_type


# --- КЛАССЫ ИГРОКА И МИРА ---

class SantaPlayer:
    def __init__(self):
        self.original_image = create_santa_sprite()
        self.rect = self.original_image.get_rect(center=(120, HEIGHT // 2))
        self.vel = 0
        self.angle = 0
        self.current_scale = 1.0
        self.target_scale = 1.0

    def jump(self):
        self.vel = JUMP_FORCE
        self.angle = 10
        play_sfx("fly")

    def update_scale(self, boost_manager):
        if boost_manager and boost_manager.is_active(BoostType.SHRINK):
            self.target_scale = SHRINK_SCALE
        else:
            self.target_scale = 1.0
        scale_speed = 0.1
        if self.current_scale < self.target_scale:
            self.current_scale = min(self.current_scale + scale_speed, self.target_scale)
        elif self.current_scale > self.target_scale:
            self.current_scale = max(self.current_scale - scale_speed, self.target_scale)

    def get_hitbox(self):
        base_shrink_x = -30
        base_shrink_y = -25
        scale_factor = self.current_scale
        hitbox_width = int((self.rect.width + base_shrink_x) * scale_factor)
        hitbox_height = int((self.rect.height + base_shrink_y) * scale_factor)
        hitbox = pygame.Rect(0, 0, hitbox_width, hitbox_height)
        hitbox.center = self.rect.center
        return hitbox

    def move(self, time_factor=1.0):
        self.vel += GRAVITY * time_factor
        self.rect.y += self.vel * time_factor
        self.angle -= 1.0 * time_factor
        if self.angle < -20: self.angle = -20
        if self.vel < 0: self.angle = 10
        if self.rect.top < 0:
            self.rect.top = 0
            self.vel = 0

    def draw(self, surface, boost_manager=None):
        self.update_scale(boost_manager)
        is_invincible = boost_manager and boost_manager.is_active(BoostType.INVINCIBILITY)
        is_shrunk = boost_manager and boost_manager.is_active(BoostType.SHRINK)

        if self.current_scale != 1.0:
            scaled_width = int(self.original_image.get_width() * self.current_scale)
            scaled_height = int(self.original_image.get_height() * self.current_scale)
            scaled_image = pygame.transform.scale(self.original_image, (scaled_width, scaled_height))
        else:
            scaled_image = self.original_image

        rotated = pygame.transform.rotate(scaled_image, self.angle)
        new_rect = rotated.get_rect(center=self.rect.center)

        if is_invincible:
            alpha = 100 + int(50 * math.sin(pygame.time.get_ticks() * 0.02))
            temp_surf = rotated.copy()
            temp_surf.set_alpha(alpha)
            surface.blit(temp_surf, new_rect.topleft)
            shield_radius = int((55 + int(5 * math.sin(pygame.time.get_ticks() * 0.01))) * self.current_scale)
            shield_surf = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (100, 200, 255, 100), (shield_radius, shield_radius), shield_radius, 3)
            surface.blit(shield_surf, (self.rect.centerx - shield_radius, self.rect.centery - shield_radius))
        elif is_shrunk:
            surface.blit(rotated, new_rect.topleft)
        else:
            surface.blit(rotated, new_rect.topleft)


class CandyPipe:
    def __init__(self, x, gap_y):
        self.x = x
        self.width = 75
        self.gap_y = gap_y
        self.passed = False
        self.top_rect = pygame.Rect(x, 0, self.width, gap_y)
        self.bot_rect = pygame.Rect(x, gap_y + PIPE_GAP, self.width, HEIGHT - (gap_y + PIPE_GAP))

    def update(self, speed=None):
        if speed is None: speed = PIPE_SPEED
        self.x -= speed
        self.top_rect.x = self.x
        self.bot_rect.x = self.x

    def draw(self, surface):
        self.draw_cane(surface, self.top_rect)
        self.draw_cane(surface, self.bot_rect)
        cap_h = 24
        self.draw_cap(surface, self.x - 6, self.gap_y - cap_h, self.width + 12, cap_h)
        self.draw_cap(surface, self.x - 6, self.gap_y + PIPE_GAP, self.width + 12, cap_h)

    def draw_cane(self, surface, rect):
        pygame.draw.rect(surface, (245, 245, 250), rect)
        clip = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        offset = (pygame.time.get_ticks() // 10) % 60
        for i in range(-60, rect.height + 60, 60):
            pts = [(0, i - offset), (rect.width, i - offset + 40), (rect.width, i - offset + 70), (0, i - offset + 30)]
            pygame.draw.polygon(clip, (220, 20, 60), pts)
            pygame.draw.line(clip, (180, 0, 0), pts[0], pts[1], 2)
        pygame.draw.rect(clip, (255, 255, 255, 80), (8, 0, 12, rect.height))
        surface.blit(clip, rect.topleft)
        pygame.draw.rect(surface, (80, 80, 80), rect, 2)

    def draw_cap(self, surface, x, y, w, h):
        r = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surface, (220, 20, 60), r, border_radius=8)
        pygame.draw.rect(surface, (80, 80, 80), r, 2, border_radius=8)
        pygame.draw.rect(surface, (255, 255, 255, 100), (x + 4, y + 4, w - 8, 6), border_radius=4)


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

    def draw(self, surface, paused=False, time_factor=1.0):
        for f in self.flakes:
            if not paused:
                f["y"] += f["speed"] * time_factor
                f["x"] += math.sin(pygame.time.get_ticks() * 0.002 + f["off"]) * 0.5 * time_factor
                if f["y"] > HEIGHT:
                    new = self.new_flake()
                    f["x"], f["y"] = new["x"], new["y"]
            alpha = int(180 * (f["r"] / 4))
            s = pygame.Surface((int(f["r"] * 2), int(f["r"] * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 255, alpha), (int(f["r"]), int(f["r"])), int(f["r"]))
            surface.blit(s, (f["x"], f["y"]))


def draw_pause_screen(surface, score):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 40, 200))
    surface.blit(overlay, (0, 0))
    ticks = pygame.time.get_ticks()
    draw_garland(surface, y_base=0, curvature=60, ticks=ticks, inverted=False)
    draw_garland(surface, y_base=HEIGHT, curvature=50, ticks=ticks + 1000, inverted=True)

    panel_width = 310
    panel_height = 230
    panel = pygame.Rect(WIDTH // 2 - panel_width // 2, HEIGHT // 2 - panel_height // 2, panel_width, panel_height)
    panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    pygame.draw.rect(panel_surf, (30, 60, 100, 220), (0, 0, panel_width, panel_height), border_radius=15)
    surface.blit(panel_surf, panel.topleft)
    pygame.draw.rect(surface, C_SLEIGH_TRIM, panel, 4, border_radius=15)

    pause_text = font_big.render("PAUSED", True, C_WHITE)
    surface.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 70))
    score_text = font.render(f"Score: {score}", True, C_GIFT_2)
    surface.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 10))
    hint1 = font.render("P - Resume", True, (180, 180, 180))
    hint2 = font.render("Q - Back to Menu", True, (150, 150, 150))
    surface.blit(hint1, (WIDTH // 2 - hint1.get_width() // 2, HEIGHT // 2 + 30))
    surface.blit(hint2, (WIDTH // 2 - hint2.get_width() // 2, HEIGHT // 2 + 60))


# --- ГЛАВНАЯ ФУНКЦИЯ ---

def run():
    global screen, clock, font, font_big, font_medium, font_small

    if not pygame.get_init():
        pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Santa's Sleigh Ride 🎅")
    load_sounds()
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 24, bold=True)
    font_big = pygame.font.SysFont("Arial", 50, bold=True)
    font_medium = pygame.font.SysFont("Arial", 36, bold=True)
    font_small = pygame.font.SysFont("Arial", 18, bold=True)

    moon_img = create_detailed_moon(80)
    high_score = 0
    if os.path.exists("santa_score.txt"):
        try:
            with open("santa_score.txt", "r") as f:
                high_score = int(f.read())
        except:
            pass

    # Загрузка картинки проигрыша
    lose_image = None
    try:
        path = resource_path(os.path.join("Win_Lose_screen", "Lose.png"))
        if os.path.exists(path):
            lose_image = pygame.image.load(path).convert_alpha()
    except:
        pass

    running = True
    while running:
        santa = SantaPlayer()
        pipes = []
        gifts = []
        snow = SnowSystem()
        boost_manager = BoostManager()
        score = 0
        pipe_spawn_timer = 0.0

        game_active = False
        game_over = False
        paused = False
        pause_time = 0
        restart_game = False

        # Переменные для эффекта game over
        blur_bg = None
        fade_alpha = 0

        # Rect картинки (будет вычислен при проигрыше)
        final_image_rect = None

        while running and not restart_game:
            dt = clock.tick(FPS) / 1000.0

            time_factor = boost_manager.get_time_factor()
            is_slow_time = boost_manager.is_active(BoostType.SLOW_TIME)
            game_dt = dt * time_factor

            # --- ОТРИСОВКА ФОНА ---
            screen.fill(C_BG_TOP)
            for i in range(0, HEIGHT, 5):
                ratio = i / HEIGHT
                color = [C_BG_TOP[j] * (1 - ratio) + C_BG_BOT[j] * ratio for j in range(3)]
                pygame.draw.rect(screen, color, (0, i, WIDTH, 5))

            # Луна и Снег
            glow = pygame.Surface((220, 220), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 255, 255, 15), (110, 110), 110)
            pygame.draw.circle(glow, (255, 255, 255, 30), (110, 110), 90)
            screen.blit(glow, (WIDTH - 220, 30))
            screen.blit(moon_img, (WIDTH - 190, 60))
            snow.draw(screen, paused, time_factor if game_active else 1.0)

            # --- СОБЫТИЯ ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                        if game_active and not game_over:
                            paused = not paused
                            if paused:
                                pause_time = pygame.time.get_ticks()
                            else:
                                for boost_type in boost_manager.active_boosts:
                                    boost_manager.active_boosts[boost_type] += (pygame.time.get_ticks() - pause_time)

                    if event.key == pygame.K_ESCAPE and not game_active and not game_over:
                        running = False  # Выход из меню

                    if event.key == pygame.K_q and paused:
                        running = False

                    if event.key == pygame.K_SPACE and not paused:
                        if not game_active and not game_over:
                            game_active = True
                            pipe_spawn_timer = 0.0
                            santa.jump()
                        elif game_active:
                            santa.jump()
                        # Логика рестарта перенесена ниже в секцию game_over

            if not running: break

            boost_manager.update(paused)
            is_invincible = boost_manager.is_active(BoostType.INVINCIBILITY)

            # --- ЛОГИКА ИГРЫ ---
            if game_active and not paused:
                pipe_spawn_timer += game_dt * 1000
                current_pipe_speed = PIPE_SPEED * time_factor

                if pipe_spawn_timer >= PIPE_FREQ:
                    gap = random.randint(150, HEIGHT - 150 - PIPE_GAP)
                    pipes.append(CandyPipe(WIDTH + 50, gap))
                    if random.random() < GIFT_SPAWN_CHANCE:
                        gifts.append(GiftBoost(WIDTH + 87, gap + PIPE_GAP // 2 + random.randint(-30, 30)))
                    pipe_spawn_timer = 0.0

                santa.move(time_factor)

                rem_pipes = []
                for p in pipes:
                    p.update(current_pipe_speed)
                    p.draw(screen)
                    if p.x < -100: rem_pipes.append(p)

                    if not is_invincible:
                        hb = santa.get_hitbox()
                        if hb.colliderect(p.top_rect) or hb.colliderect(p.bot_rect):
                            game_active = False
                            game_over = True
                            play_sfx("lose")

                    if not p.passed and p.x < santa.rect.x:
                        score += 1
                        p.passed = True

                for r in rem_pipes: pipes.remove(r)

                rem_gifts = []
                for gift in gifts:
                    gift.update(current_pipe_speed)
                    gift.draw(screen)
                    if gift.x < -50: rem_gifts.append(gift)
                    if gift.check_collision(santa.rect):
                        boost_manager.add_boost(gift.collect())
                        rem_gifts.append(gift)
                for r in rem_gifts:
                    if r in gifts: gifts.remove(r)

                if santa.rect.bottom >= HEIGHT:
                    if not is_invincible:
                        game_active = False
                        game_over = True
                        play_sfx("lose")
                    else:
                        santa.rect.bottom = HEIGHT
                        santa.vel = 0

                santa.draw(screen, boost_manager)
                if is_slow_time: draw_slow_time_effect(screen)
                if boost_manager.is_active(BoostType.SHRINK): draw_shrink_effect(screen)
                boost_manager.draw_particles(screen)

                sc_txt = font_big.render(str(score), True, C_WHITE)
                screen.blit(sc_txt, (WIDTH // 2 - sc_txt.get_width() // 2, 100))
                boost_manager.draw_ui(screen)

            # --- ПАУЗА ---
            elif game_active and paused:
                for p in pipes: p.draw(screen)
                for gift in gifts: gift.draw(screen)
                santa.draw(screen, boost_manager)
                draw_pause_screen(screen, score)

            # --- МЕНЮ ---
            elif not game_active and not game_over:
                santa.rect.y = HEIGHT // 2 + math.sin(pygame.time.get_ticks() * 0.004) * 15
                santa.draw(screen)
                t = font_big.render("SANTA RIDE", True, C_WHITE)
                s = font.render("Press SPACE to start", True, (200, 200, 200))
                boost_hint = font_small.render("Collect gifts for power-ups!", True, (255, 200, 100))
                screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 3))
                screen.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 3 + 60))
                screen.blit(boost_hint, (WIDTH // 2 - boost_hint.get_width() // 2, HEIGHT // 3 + 100))

            # --- GAME OVER (CLEAN STYLE) ---
            elif game_over:
                # Отрисовка застывшей игры на заднем плане
                for p in pipes: p.draw(screen)
                for gift in gifts: gift.draw(screen)
                santa.draw(screen)

                # Создание размытия (один раз)
                if blur_bg is None:
                    try:
                        snapshot = screen.copy()
                        small = pygame.transform.smoothscale(snapshot, (WIDTH // 10, HEIGHT // 10))
                        blur_bg = pygame.transform.smoothscale(small, (WIDTH, HEIGHT))
                    except:
                        blur_bg = screen.copy()  # Fallback

                # Рисуем размытый фон
                screen.blit(blur_bg, (0, 0))

                # Затемнение
                if fade_alpha < 255: fade_alpha += 8
                darkness = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                darkness.fill((0, 0, 0, min(fade_alpha, 180)))
                screen.blit(darkness, (0, 0))

                # Сохраняем рекорд
                if score > high_score:
                    high_score = score
                    with open("santa_score.txt", "w") as f:
                        f.write(str(high_score))

                # Рисуем Lose.png
                if lose_image:
                    # Pop-up анимация
                    current_scale = 0.85 + 0.15 * (fade_alpha / 255)
                    if current_scale > 0.1:
                        img_target_w = 480
                        aspect_ratio = lose_image.get_height() / lose_image.get_width()
                        img_target_h = int(img_target_w * aspect_ratio)

                        # Масштабируем
                        final_w = int(img_target_w * current_scale)
                        final_h = int(img_target_h * current_scale)
                        final_img = pygame.transform.smoothscale(lose_image, (final_w, final_h))

                        img_rect = final_img.get_rect()
                        # Центрируем чуть выше середины
                        img_rect.center = (WIDTH // 2, HEIGHT // 2 - 40)

                        # Рисуем картинку (без тени и рамок)
                        screen.blit(final_img, img_rect)

                        # --- ТЕКСТ СНИЗУ (БЕЗ ФОНА) ---
                        panel_w = 260
                        panel_h = 100
                        panel_x = WIDTH // 2 - panel_w // 2
                        panel_y = img_rect.bottom + 20

                        # Текст
                        sc_text = font.render(f"Score: {score}", True, C_WHITE)
                        best_text = font.render(f"Best: {high_score}", True, C_GIFT_2)

                        # Располагаем текст
                        screen.blit(sc_text, (panel_x + 20, panel_y + 15))
                        screen.blit(best_text, (panel_x + panel_w - 20 - best_text.get_width(), panel_y + 15))

                        # Разделитель
                        pygame.draw.line(screen, (150, 150, 150), (panel_x + 20, panel_y + 45),
                                         (panel_x + panel_w - 20, panel_y + 45), 1)

                        # Подсказки управления
                        retry_hint = font_small.render("SPACE - Retry", True, (200, 200, 200))
                        menu_hint = font_small.render("ESC - Menu", True, (150, 150, 150))

                        screen.blit(retry_hint, (WIDTH // 2 - retry_hint.get_width() // 2, panel_y + 55))
                        screen.blit(menu_hint, (WIDTH // 2 - menu_hint.get_width() // 2, panel_y + 75))

                else:
                    # Резервный вариант, если картинки нет (текст)
                    l1 = font_big.render("GAME OVER", True, C_SLEIGH_BODY)
                    l2 = font.render(f"Score: {score}", True, C_WHITE)
                    screen.blit(l1, (WIDTH // 2 - l1.get_width() // 2, HEIGHT // 2 - 50))
                    screen.blit(l2, (WIDTH // 2 - l2.get_width() // 2, HEIGHT // 2 + 10))

                # Управление в game over
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    restart_game = True
                if keys[pygame.K_ESCAPE]:
                    running = False

            pygame.display.flip()

    return


if __name__ == "__main__":
    run()