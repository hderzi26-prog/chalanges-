#!/usr/bin/env python3
"""
Dragon Quest - Free Roam Top-Down Game (Pygame)

Explore a procedural overworld as a dragon. Breathe fire, defeat enemies,
collect gold and hearts, and survive as long as you can.

No external assets; everything is drawn with pygame primitives.
"""

import math
import os
import random
import sys
import time
from dataclasses import dataclass

import pygame


# ------------------------------ Config ---------------------------------

WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 640
FPS = 60

WORLD_WIDTH = 3200
WORLD_HEIGHT = 3200

DRAGON_BASE_SPEED = 220.0  # pixels per second
DRAGON_DASH_SPEED = 420.0
DRAGON_DASH_STAMINA_COST = 28.0
DRAGON_MAX_STAMINA = 100.0
DRAGON_STAMINA_RECOVERY_PER_SEC = 22.0

DRAGON_MAX_HEALTH = 100
FIRE_COOLDOWN_SEC = 0.45
FIRE_LIFETIME_SEC = 0.55
FIRE_SPEED = 650.0
FIRE_SPREAD_DEG = 10.0
FIRE_CONE_PROJECTILES = 7
FIRE_DAMAGE = 34

ENEMY_SPAWN_COUNT = 28
ENEMY_SPEED = 120.0
ENEMY_DAMAGE = 12
ENEMY_MAX_HEALTH = 50
ENEMY_SENSE_RADIUS = 360
ENEMY_PATROL_TURN_SEC = (1.0, 3.5)

PICKUP_GOLD_VALUE = (5, 20)
PICKUP_HEART_HEAL = (10, 25)
LOOT_DROP_CHANCE = 0.35

RNG_SEED = 1337


# ------------------------------ Utilities ------------------------------

def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def vec_from_angle(deg: float) -> pygame.Vector2:
    rad = math.radians(deg)
    return pygame.Vector2(math.cos(rad), math.sin(rad))


def now() -> float:
    return time.perf_counter()


# ------------------------------ Entities -------------------------------

@dataclass
class FireBolt:
    pos: pygame.Vector2
    vel: pygame.Vector2
    expires_at: float
    damage: int = FIRE_DAMAGE


class Dragon:
    def __init__(self, x: float, y: float) -> None:
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.angle_deg = 0.0
        self.health = DRAGON_MAX_HEALTH
        self.stamina = DRAGON_MAX_STAMINA
        self.score = 0
        self.last_fire_time = -999.0

    def update(self, dt: float, keys: pygame.key.ScancodeWrapper) -> None:
        move_dir = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move_dir.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move_dir.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_dir.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_dir.x += 1

        if move_dir.length_squared() > 0:
            move_dir = move_dir.normalize()
            self.angle_deg = math.degrees(math.atan2(move_dir.y, move_dir.x))

        speed = DRAGON_BASE_SPEED
        dashing = False
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.stamina > 0:
            dashing = True
            speed = DRAGON_DASH_SPEED
            self.stamina -= DRAGON_DASH_STAMINA_COST * dt
        else:
            self.stamina += DRAGON_STAMINA_RECOVERY_PER_SEC * dt
        self.stamina = clamp(self.stamina, 0.0, DRAGON_MAX_STAMINA)

        self.vel = move_dir * speed
        self.pos += self.vel * dt
        self.pos.x = clamp(self.pos.x, 0, WORLD_WIDTH)
        self.pos.y = clamp(self.pos.y, 0, WORLD_HEIGHT)

    def can_fire(self) -> bool:
        return (now() - self.last_fire_time) >= FIRE_COOLDOWN_SEC

    def fire(self) -> list[FireBolt]:
        self.last_fire_time = now()
        bolts: list[FireBolt] = []
        base_dir = vec_from_angle(self.angle_deg)
        for i in range(FIRE_CONE_PROJECTILES):
            t = (i / (FIRE_CONE_PROJECTILES - 1)) if FIRE_CONE_PROJECTILES > 1 else 0.5
            spread = (t - 0.5) * 2.0 * FIRE_SPREAD_DEG
            dir_vec = vec_from_angle(self.angle_deg + spread)
            vel = dir_vec * FIRE_SPEED
            bolts.append(FireBolt(pos=self.pos.copy(), vel=vel, expires_at=now() + FIRE_LIFETIME_SEC))
        return bolts


class Enemy:
    def __init__(self, x: float, y: float) -> None:
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.health = ENEMY_MAX_HEALTH
        self.next_patrol_turn = now() + random.uniform(*ENEMY_PATROL_TURN_SEC)
        self.patrol_dir = vec_from_angle(random.uniform(0, 360))

    def update(self, dt: float, dragon_pos: pygame.Vector2) -> None:
        to_dragon = dragon_pos - self.pos
        dist = to_dragon.length()

        if dist < ENEMY_SENSE_RADIUS:
            if dist > 1e-2:
                desired = to_dragon.normalize() * ENEMY_SPEED
            else:
                desired = pygame.Vector2(0, 0)
        else:
            # patrol
            if now() > self.next_patrol_turn:
                self.patrol_dir = vec_from_angle(random.uniform(0, 360))
                self.next_patrol_turn = now() + random.uniform(*ENEMY_PATROL_TURN_SEC)
            desired = self.patrol_dir * (ENEMY_SPEED * 0.5)

        self.vel = desired
        self.pos += self.vel * dt
        self.pos.x = clamp(self.pos.x, 0, WORLD_WIDTH)
        self.pos.y = clamp(self.pos.y, 0, WORLD_HEIGHT)


@dataclass
class Pickup:
    kind: str  # 'gold' | 'heart'
    pos: pygame.Vector2
    value: int


# ------------------------------ World/Camera ---------------------------

class World:
    def __init__(self) -> None:
        random.seed(RNG_SEED)
        self.decor_rects: list[tuple[pygame.Rect, tuple[int, int, int]]] = []
        # Create simple patches of water and trees via rectangles
        for _ in range(180):
            w = random.randint(120, 420)
            h = random.randint(80, 320)
            x = random.randint(0, WORLD_WIDTH - w)
            y = random.randint(0, WORLD_HEIGHT - h)
            color = random.choice([(45, 85, 45), (35, 75, 35), (25, 65, 25)])
            self.decor_rects.append((pygame.Rect(x, y, w, h), color))
        for _ in range(80):
            w = random.randint(140, 480)
            h = random.randint(100, 420)
            x = random.randint(0, WORLD_WIDTH - w)
            y = random.randint(0, WORLD_HEIGHT - h)
            color = random.choice([(30, 90, 130), (25, 80, 120)])  # water
            self.decor_rects.append((pygame.Rect(x, y, w, h), color))

    def draw(self, surface: pygame.Surface, camera: pygame.Rect) -> None:
        surface.fill((60, 120, 60))  # grass base
        for rect, color in self.decor_rects:
            if rect.colliderect(camera.inflate(200, 200)):
                pygame.draw.rect(surface, color, rect.move(-camera.x, -camera.y))


class Camera:
    def __init__(self) -> None:
        self.rect = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

    def update(self, target: pygame.Vector2) -> None:
        self.rect.centerx = int(target.x)
        self.rect.centery = int(target.y)
        self.rect.x = clamp(self.rect.x, 0, WORLD_WIDTH - self.rect.w)
        self.rect.y = clamp(self.rect.y, 0, WORLD_HEIGHT - self.rect.h)


# ------------------------------ Game -----------------------------------

class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Dragon Quest - Free Roam")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Verdana", 18)
        self.big_font = pygame.font.SysFont("Verdana", 28, bold=True)

        self.world = World()
        self.camera = Camera()

        self.dragon = Dragon(WORLD_WIDTH / 2, WORLD_HEIGHT / 2)
        self.enemies: list[Enemy] = []
        self.pickups: list[Pickup] = []
        self.projectiles: list[FireBolt] = []

        self.paused = False
        self.show_help = True

        self.spawn_initial_enemies()

    # -------------------------- Spawning --------------------------
    def spawn_initial_enemies(self) -> None:
        for _ in range(ENEMY_SPAWN_COUNT):
            x = random.uniform(0, WORLD_WIDTH)
            y = random.uniform(0, WORLD_HEIGHT)
            self.enemies.append(Enemy(x, y))

    def spawn_loot(self, pos: pygame.Vector2) -> None:
        if random.random() < LOOT_DROP_CHANCE:
            if random.random() < 0.7:
                value = random.randint(*PICKUP_GOLD_VALUE)
                self.pickups.append(Pickup("gold", pos.copy(), value))
            else:
                heal = random.randint(*PICKUP_HEART_HEAL)
                self.pickups.append(Pickup("heart", pos.copy(), heal))

    # -------------------------- Update ----------------------------
    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                if event.key in (pygame.K_h, pygame.K_SLASH):
                    self.show_help = not self.show_help
                if event.key == pygame.K_SPACE and self.dragon.can_fire() and not self.paused:
                    self.projectiles.extend(self.dragon.fire())

    def update(self, dt: float) -> None:
        if self.paused:
            return
        keys = pygame.key.get_pressed()
        self.dragon.update(dt, keys)
        for e in self.enemies:
            e.update(dt, self.dragon.pos)
        self.update_projectiles(dt)
        self.resolve_collisions()
        self.camera.update(self.dragon.pos)

    def update_projectiles(self, dt: float) -> None:
        now_time = now()
        alive: list[FireBolt] = []
        for bolt in self.projectiles:
            if now_time > bolt.expires_at:
                continue
            bolt.pos += bolt.vel * dt
            if 0 <= bolt.pos.x <= WORLD_WIDTH and 0 <= bolt.pos.y <= WORLD_HEIGHT:
                alive.append(bolt)
        self.projectiles = alive

    def resolve_collisions(self) -> None:
        # Dragon vs enemies (touch damage)
        for e in list(self.enemies):
            if (e.pos - self.dragon.pos).length() < 28:
                self.dragon.health -= ENEMY_DAMAGE * (1 / FPS) * 8  # small continuous damage
        self.dragon.health = int(clamp(self.dragon.health, 0, DRAGON_MAX_HEALTH))

        # Projectiles vs enemies
        for bolt in list(self.projectiles):
            for e in list(self.enemies):
                if (e.pos - bolt.pos).length() < 24:
                    e.health -= bolt.damage
                    # knockback
                    delta = e.pos - bolt.pos
                    if delta.length() > 0:
                        e.pos += delta.normalize() * 12
                    # mark bolt expired
                    bolt.expires_at = 0
                    if e.health <= 0:
                        self.spawn_loot(e.pos)
                        self.enemies.remove(e)
                        self.dragon.score += 25

        # Dragon vs pickups
        for p in list(self.pickups):
            if (p.pos - self.dragon.pos).length() < 28:
                if p.kind == "gold":
                    self.dragon.score += p.value
                else:
                    self.dragon.health = int(clamp(self.dragon.health + p.value, 0, DRAGON_MAX_HEALTH))
                self.pickups.remove(p)

    # -------------------------- Draw ------------------------------
    def draw(self) -> None:
        cam = self.camera.rect
        self.world.draw(self.screen, cam)

        # Draw pickups
        for p in self.pickups:
            screen_pos = (int(p.pos.x - cam.x), int(p.pos.y - cam.y))
            if p.kind == "gold":
                pygame.draw.circle(self.screen, (230, 190, 20), screen_pos, 6)
                pygame.draw.circle(self.screen, (255, 220, 60), screen_pos, 6, 2)
            else:  # heart
                pygame.draw.circle(self.screen, (200, 40, 70), (screen_pos[0] - 4, screen_pos[1]), 5)
                pygame.draw.circle(self.screen, (200, 40, 70), (screen_pos[0] + 4, screen_pos[1]), 5)
                pygame.draw.polygon(self.screen, (200, 40, 70), [
                    (screen_pos[0] - 8, screen_pos[1]),
                    (screen_pos[0] + 8, screen_pos[1]),
                    (screen_pos[0], screen_pos[1] + 10),
                ])

        # Draw enemies
        for e in self.enemies:
            screen_pos = (int(e.pos.x - cam.x), int(e.pos.y - cam.y))
            pygame.draw.circle(self.screen, (40, 40, 40), screen_pos, 18)
            pygame.draw.circle(self.screen, (180, 50, 50), screen_pos, 16)
            # health ring
            pct = clamp(e.health / ENEMY_MAX_HEALTH, 0, 1)
            color = (int(255 * (1 - pct)), int(255 * pct), 40)
            pygame.draw.circle(self.screen, color, screen_pos, 20, 2)

        # Draw projectiles
        for bolt in self.projectiles:
            screen_pos = (int(bolt.pos.x - cam.x), int(bolt.pos.y - cam.y))
            pygame.draw.circle(self.screen, (255, 150, 40), screen_pos, 5)
            pygame.draw.circle(self.screen, (255, 220, 120), screen_pos, 3)

        # Draw dragon (triangle)
        d = self.dragon
        dir_vec = vec_from_angle(d.angle_deg)
        perp = pygame.Vector2(-dir_vec.y, dir_vec.x)
        tip = d.pos + dir_vec * 22
        left = d.pos - dir_vec * 12 + perp * 14
        right = d.pos - dir_vec * 12 - perp * 14
        pts = [
            (int(tip.x - cam.x), int(tip.y - cam.y)),
            (int(left.x - cam.x), int(left.y - cam.y)),
            (int(right.x - cam.x), int(right.y - cam.y)),
        ]
        pygame.draw.polygon(self.screen, (60, 60, 60), pts)
        pygame.draw.polygon(self.screen, (50, 180, 220), pts, 2)

        # HUD
        self.draw_hud()

        if self.paused:
            self.draw_center_message("Paused - Press P to resume")
        if self.show_help:
            self.draw_help()

    def draw_center_message(self, text: str) -> None:
        s = self.big_font.render(text, True, (255, 255, 255))
        rect = s.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        pygame.draw.rect(self.screen, (0, 0, 0), rect.inflate(20, 12))
        self.screen.blit(s, rect)

    def draw_hud(self) -> None:
        # Panels
        pygame.draw.rect(self.screen, (0, 0, 0), (10, 10, 350, 86))
        pygame.draw.rect(self.screen, (0, 0, 0), (WINDOW_WIDTH - 220, 10, 210, 86))

        # Health bar
        hp_pct = clamp(self.dragon.health / DRAGON_MAX_HEALTH, 0, 1)
        pygame.draw.rect(self.screen, (120, 40, 40), (18, 18, 330, 18))
        pygame.draw.rect(self.screen, (220, 60, 60), (18, 18, int(330 * hp_pct), 18))
        self.screen.blit(self.font.render("Health", True, (255, 255, 255)), (22, 18))

        # Stamina bar
        st_pct = clamp(self.dragon.stamina / DRAGON_MAX_STAMINA, 0, 1)
        pygame.draw.rect(self.screen, (40, 40, 80), (18, 42, 330, 18))
        pygame.draw.rect(self.screen, (60, 80, 200), (18, 42, int(330 * st_pct), 18))
        self.screen.blit(self.font.render("Stamina", True, (255, 255, 255)), (22, 42))

        # Fire cooldown bar
        since_fire = now() - self.dragon.last_fire_time
        cd_pct = clamp(since_fire / FIRE_COOLDOWN_SEC, 0, 1)
        pygame.draw.rect(self.screen, (80, 40, 0), (18, 66, 330, 18))
        pygame.draw.rect(self.screen, (255, 160, 40), (18, 66, int(330 * cd_pct), 18))
        self.screen.blit(self.font.render("Fire", True, (255, 255, 255)), (22, 66))

        # Score panel
        self.screen.blit(self.font.render(f"Score: {self.dragon.score}", True, (255, 255, 255)), (WINDOW_WIDTH - 208, 18))
        self.screen.blit(self.font.render("P: Pause  H/?: Help", True, (220, 220, 220)), (WINDOW_WIDTH - 208, 42))
        self.screen.blit(self.font.render("Esc/Q: Quit", True, (220, 220, 220)), (WINDOW_WIDTH - 208, 66))

    def draw_help(self) -> None:
        lines = [
            "Dragon Quest - Free Roam",
            "WASD/Arrows to move, Shift to dash",
            "Space to breathe fire",
            "Pick up gold and hearts",
            "Avoid enemies or roast them",
            "P to pause, H/? for help",
        ]
        x, y = 12, WINDOW_HEIGHT - 18 * (len(lines) + 1)
        pygame.draw.rect(self.screen, (0, 0, 0), (x - 4, y - 6, 460, 24 + 18 * len(lines)))
        for i, t in enumerate(lines):
            self.screen.blit(self.font.render(t, True, (240, 240, 240)), (x, y + i * 18))

    # -------------------------- Main loop -------------------------
    def run(self) -> None:
        last = now()
        while True:
            self.handle_events()
            current = now()
            dt = clamp(current - last, 0, 1/20)  # cap dt to avoid spiral
            last = current
            self.update(dt)
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)


def main() -> None:
    Game().run()


if __name__ == "__main__":
    main()



