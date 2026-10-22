import math
import random
import pygame
from src.constants import (
    N, LO, HI, WINDOW_WIDTH, WINDOW_HEIGHT,
    COLOR_BG_DARK, COLOR_PANEL_BG, COLOR_PANEL_BORDER,
    COLOR_TEXT_LIGHT, COLOR_TEXT_GOLD, COLOR_TEXT_MUTED,
    FACTIONS, ORDER, TEAM, UNIT_NAMES, ATK, MAX_HP, UNIT_COST, CARDS
)
from src.piece_graphics import PieceGraphics
from src.asset_manager import AssetManager
from src.oracle import GeminiOracle

class Particle:
    def __init__(self, x, y, vx, vy, color, life, size=3, drag=0.96, gravity=0.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.max_life = life
        self.life = life
        self.size = size
        self.drag = drag
        self.gravity = gravity

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.vx *= self.drag
        self.vy *= self.drag
        self.life -= dt
        return self.life > 0

    def draw(self, surface):
        alpha = max(0, min(255, int(255 * (self.life / self.max_life))))
        r, g, b = self.color[:3]
        s_size = int(self.size * 2 + 4)
        s = pygame.Surface((s_size, s_size), pygame.SRCALPHA)
        center = s_size // 2
        pygame.draw.circle(s, (r, g, b, alpha // 3), (center, center), int(self.size + 1))
        pygame.draw.circle(s, (r, g, b, alpha), (center, center), int(self.size))
        if self.size >= 2:
            pygame.draw.circle(s, (255, 255, 255, alpha), (center, center), max(1, int(self.size * 0.4)))
        surface.blit(s, (int(self.x - center), int(self.y - center)))

class Shockwave:
    def __init__(self, x, y, max_radius=40, speed=160, color=(255, 215, 0), width=3):
        self.x = x
        self.y = y
        self.radius = 4.0
        self.max_radius = max_radius
        self.speed = speed
        self.color = color
        self.width = width
        self.life = 1.0

    def update(self, dt):
        self.radius += self.speed * dt
        self.life = max(0.0, 1.0 - (self.radius / self.max_radius))
        return self.radius < self.max_radius

    def draw(self, surface):
        if self.radius <= 1 or self.life <= 0:
            return
        alpha = int(255 * (self.life ** 1.4))
        r, g, b = self.color[:3]
        s_size = int(self.radius * 2 + 10)
        s = pygame.Surface((s_size, s_size), pygame.SRCALPHA)
        center = s_size // 2
        w = max(1, int(self.width * self.life))
        pygame.draw.circle(s, (r, g, b, alpha), (center, center), int(self.radius), w)
        if self.radius > 6:
            pygame.draw.circle(s, (255, 255, 255, alpha // 2), (center, center), max(1, int(self.radius - w)), 1)
        surface.blit(s, (int(self.x - center), int(self.y - center)))

class SlashEffect:
    def __init__(self, x1, y1, x2, y2, duration=0.22, color=(255, 230, 120)):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.time = 0.0
        self.duration = duration
        self.color = color

    def update(self, dt):
        self.time += dt
        return self.time < self.duration

    def draw(self, surface):
        p = self.time / self.duration
        alpha = int(255 * (1.0 - p))
        r, g, b = self.color[:3]
        mid_x = (self.x1 + self.x2) / 2
        mid_y = (self.y1 + self.y2) / 2
        dx = self.x2 - self.x1
        dy = self.y2 - self.y1
        dist = math.hypot(dx, dy)
        if dist == 0: return
        nx = -dy / dist * 16.0
        ny = dx / dist * 16.0

        pts = []
        for i in range(9):
            t = i / 8.0
            bx = (1 - t)**2 * self.x1 + 2 * (1 - t) * t * (mid_x + nx) + t**2 * self.x2
            by = (1 - t)**2 * self.y1 + 2 * (1 - t) * t * (mid_y + ny) + t**2 * self.y2
            pts.append((bx, by))

        if len(pts) > 1:
            glow_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            pygame.draw.lines(glow_surf, (r, g, b, alpha // 2), False, pts, 6)
            pygame.draw.lines(glow_surf, (255, 255, 255, alpha), False, pts, 2)
            surface.blit(glow_surf, (0, 0))

class UIRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.assets = AssetManager()
        self.oracle = GeminiOracle.get_instance()
        self.init_fonts()
        self.particles = []
        self.shockwaves = []
        self.slashes = []
        self.shake_trauma = 0.0
        self.shake_offset = (0, 0)

        self.board_x = 24
        self.board_y = 14
        self.board_size = 608
        self.tile_size = self.board_size // N
        self.anim_time = 0.0

    def init_fonts(self):
        pygame.font.init()
        self.font_title = pygame.font.SysFont("segoeui,consolas,arial", 26, bold=True)
        self.font_header = pygame.font.SysFont("segoeui,consolas,arial", 18, bold=True)
        self.font_body = pygame.font.SysFont("segoeui,consolas,arial", 14)
        self.font_bold = pygame.font.SysFont("segoeui,consolas,arial", 13, bold=True)
        self.font_small = pygame.font.SysFont("segoeui,consolas,arial", 11)
        self.font_hp = pygame.font.SysFont("consolas,arial", 11, bold=True)
        self.font_badge = pygame.font.SysFont("segoeui,consolas,arial", 9, bold=True)
        self.font_tile = pygame.font.SysFont("segoeui,consolas,arial", 20, bold=True)
        self.font_oracle_italic = pygame.font.SysFont("segoeui,georgia,arial", 12, italic=True)

    def wrap_text(self, text, font, max_width, max_lines=2):
        words = text.split(' ')
        lines = []
        cur = []
        for w in words:
            test = " ".join(cur + [w])
            if font.size(test)[0] > max_width:
                if cur:
                    lines.append(" ".join(cur))
                    cur = [w]
                else:
                    lines.append(w)
                    cur = []
            else:
                cur.append(w)
            if len(lines) >= max_lines:
                break
        if cur and len(lines) < max_lines:
            lines.append(" ".join(cur))
        return lines

    def draw_vector_heart(self, surface, x, y, size=14, filled=True, color=(255, 60, 90)):
        w = size
        h = size
        r = int(w * 0.28)
        cx1 = int(x + r + 1)
        cx2 = int(x + w - r - 1)
        cy = int(y + r + 1)
        if filled:
            s_pts = [(int(x + 1), int(cy + 1)), (int(x + w - 1), int(cy + 1)), (int(x + w // 2), int(y + h + 1))]
            pygame.draw.polygon(surface, (15, 8, 10), s_pts)
            pygame.draw.circle(surface, color, (cx1, cy), r)
            pygame.draw.circle(surface, color, (cx2, cy), r)
            pts = [(int(x + 1), cy), (int(x + w - 1), cy), (int(x + w // 2), int(y + h))]
            pygame.draw.polygon(surface, color, pts)
            glint_r = max(1, r // 2)
            pygame.draw.circle(surface, (255, 255, 255), (cx1 - 1, cy - 1), glint_r)
        else:
            empty_bg = (32, 22, 25)
            border_c = (110, 45, 55)
            pygame.draw.circle(surface, empty_bg, (cx1, cy), r)
            pygame.draw.circle(surface, empty_bg, (cx2, cy), r)
            pts = [(int(x + 1), cy), (int(x + w - 1), cy), (int(x + w // 2), int(y + h))]
            pygame.draw.polygon(surface, empty_bg, pts)
            pygame.draw.circle(surface, border_c, (cx1, cy), r, 1)
            pygame.draw.circle(surface, border_c, (cx2, cy), r, 1)
            pygame.draw.lines(surface, border_c, False, [(int(x + 1), cy), (int(x + w // 2), int(y + h)), (int(x + w - 1), cy)], 1)

    def draw_vector_gem(self, surface, x, y, size=11, color=(0, 215, 255)):
        w = size
        h = size
        pts = [
            (x + w // 2, y),
            (x + w, y + int(h * 0.35)),
            (x + w // 2, y + h),
            (x, y + int(h * 0.35))
        ]
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.polygon(surface, (255, 255, 255), [(x + w // 2, y), (x + int(w * 0.75), y + int(h * 0.35)), (x + int(w * 0.25), y + int(h * 0.35))])
        pygame.draw.polygon(surface, (0, 80, 140), pts, 1)

    def draw_vector_sword(self, surface, x, y, size=11, color=(255, 120, 120)):
        pygame.draw.line(surface, (240, 245, 255), (x + size - 2, y + 2), (x + 2, y + size - 2), 2)
        pygame.draw.line(surface, (240, 245, 255), (x + 2, y + 2), (x + size - 2, y + size - 2), 2)
        pygame.draw.circle(surface, color, (x + size // 2, y + size // 2), 2)

    def draw_vector_lightning(self, surface, x, y, size=12, color=(255, 215, 0)):
        pts = [
            (x + int(size * 0.65), y),
            (x + int(size * 0.15), y + int(size * 0.55)),
            (x + int(size * 0.55), y + int(size * 0.55)),
            (x + int(size * 0.35), y + size),
            (x + int(size * 0.95), y + int(size * 0.42)),
            (x + int(size * 0.55), y + int(size * 0.42))
        ]
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.polygon(surface, (255, 255, 255), pts, 1)

    def draw_vector_trap(self, surface, x, y, size=11, color=(255, 80, 80)):
        pts = [(x + size // 2, y), (x + size - 1, y + size // 2), (x + size // 2, y + size - 1), (x + 1, y + size // 2)]
        pygame.draw.polygon(surface, (50, 15, 20), pts)
        pygame.draw.polygon(surface, color, pts, 1)
        pygame.draw.line(surface, color, (x + 3, y + 3), (x + size - 4, y + size - 4), 1)
        pygame.draw.line(surface, color, (x + size - 4, y + 3), (x + 3, y + size - 4), 1)

    def draw_vector_star(self, surface, x, y, size=12, color=(255, 215, 0)):
        cx = x + size // 2
        cy = y + size // 2
        pts = [
            (cx, y), (cx + 2, cy - 2), (x + size, cy), (cx + 2, cy + 2),
            (cx, y + size), (cx - 2, cy + 2), (x, cy), (cx - 2, cy - 2)
        ]
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 1)

    def draw_vector_shield(self, surface, x, y, size=12, color=(255, 215, 0)):
        w = size
        h = size
        pts = [
            (x + 1, y), (x + w - 1, y),
            (x + w - 1, y + int(h * 0.6)),
            (x + w // 2, y + h),
            (x + 1, y + int(h * 0.6))
        ]
        pygame.draw.polygon(surface, (45, 35, 20), pts)
        pygame.draw.polygon(surface, color, pts, 1)
        pygame.draw.line(surface, color, (x + w // 2, y + 2), (x + w // 2, y + h - 3), 1)

    def draw_sacred_flag(self, surface, cx, cy, size=28, anim_time=0.0):
        wave = math.sin(anim_time * 5.0) * 3
        shrine_radius = int(size * 0.55)
        shrine_surf = pygame.Surface((shrine_radius * 2, shrine_radius * 2), pygame.SRCALPHA)
        pulse_alpha = int(90 + 40 * math.sin(anim_time * 4.0))
        pygame.draw.circle(shrine_surf, (255, 215, 0, pulse_alpha), (shrine_radius, shrine_radius), shrine_radius)
        pygame.draw.circle(shrine_surf, (255, 245, 170, pulse_alpha + 30), (shrine_radius, shrine_radius), int(shrine_radius * 0.5), 1)
        surface.blit(shrine_surf, (cx - shrine_radius, cy - shrine_radius))

        pole_x = cx - size // 4
        pole_top_y = cy - size // 2
        pole_bot_y = cy + size // 2
        pygame.draw.line(surface, (255, 235, 120), (pole_x, pole_top_y), (pole_x, pole_bot_y), 3)
        pygame.draw.circle(surface, (255, 215, 0), (pole_x, pole_top_y), 4)

        flag_w = int(size * 0.72)
        flag_h = int(size * 0.44)
        pts = [
            (pole_x + 1, pole_top_y + 2),
            (pole_x + flag_w + int(wave), pole_top_y + 2 + int(wave * 0.4)),
            (pole_x + int(flag_w * 0.8) + int(wave * 0.7), pole_top_y + flag_h // 2),
            (pole_x + flag_w + int(wave * 0.5), pole_top_y + flag_h),
            (pole_x + 1, pole_top_y + flag_h)
        ]
        pygame.draw.polygon(surface, (215, 25, 45), pts)
        pygame.draw.polygon(surface, (255, 215, 40), pts, 1)
        pygame.draw.circle(surface, (255, 215, 0), (pole_x + flag_w // 2, pole_top_y + flag_h // 2), 3)

    def draw_mini_flag(self, surface, x, y, size=14, anim_time=0.0):
        wave = math.sin(anim_time * 5.0) * 1.5
        pygame.draw.line(surface, (255, 235, 120), (x, y - 6), (x, y + 6), 2)
        pygame.draw.circle(surface, (255, 215, 0), (x, y - 6), 2)
        pts = [
            (x + 1, y - 5),
            (x + size + int(wave), y - 5 + int(wave * 0.5)),
            (x + int(size * 0.75), y - 1),
            (x + size + int(wave * 0.5), y + 3),
            (x + 1, y + 3)
        ]
        pygame.draw.polygon(surface, (220, 20, 45), pts)
        pygame.draw.polygon(surface, (255, 215, 0), pts, 1)

    def add_sparkles(self, x, y, count=8, color=(255, 215, 0)):
        for _ in range(count):
            angle = math.radians(math.sin(x + y) * 360 + _ * (360 / count))
            spd = 40 + (_ * 15) % 60
            self.particles.append(Particle(
                x, y,
                math.cos(angle) * spd, math.sin(angle) * spd,
                color, life=0.6, size=3
            ))

    def add_combat_sparks(self, x, y, count=8, color=(255, 215, 0)):
        for i in range(count):
            ang = random.uniform(0, 2 * math.pi)
            spd = random.uniform(70, 160)
            self.particles.append(Particle(
                x, y,
                math.cos(ang) * spd, math.sin(ang) * spd,
                color, life=random.uniform(0.25, 0.45), size=random.randint(2, 3),
                drag=0.92, gravity=60.0
            ))

    def add_explosion_particles(self, x, y, count=18, color=(255, 60, 60)):
        for i in range(count):
            ang = random.uniform(0, 2 * math.pi)
            spd = random.uniform(80, 200)
            c = color if i % 2 == 0 else (255, random.randint(160, 220), 40)
            self.particles.append(Particle(
                x, y,
                math.cos(ang) * spd, math.sin(ang) * spd,
                c, life=random.uniform(0.35, 0.65), size=random.randint(2, 4),
                drag=0.94, gravity=40.0
            ))

    def add_divine_rays(self, x, y, count=12):
        for _ in range(count):
            self.particles.append(Particle(
                x + random.randint(-12, 12),
                y + random.randint(-4, 4),
                random.uniform(-15, 15),
                random.uniform(-90, -45),
                (255, 225, 100), life=random.uniform(0.5, 0.8), size=random.randint(2, 3),
                drag=0.97, gravity=-20.0
            ))

    def add_spell_runes(self, x, y, count=12, color=(0, 200, 255)):
        for i in range(count):
            ang = i * (2 * math.pi / count)
            spd = random.uniform(50, 110)
            self.particles.append(Particle(
                x, y,
                math.cos(ang) * spd, math.sin(ang) * spd,
                color, life=random.uniform(0.4, 0.65), size=3,
                drag=0.95, gravity=0.0
            ))

    def trigger_shake(self, amount):
        self.shake_trauma = min(14.0, self.shake_trauma + amount)

    def process_vfx_events(self, game):
        ts = self.tile_size
        bx = self.board_x + int(self.shake_offset[0])
        by = self.board_y + int(self.shake_offset[1])

        while getattr(game, 'vfx_events', None):
            ev = game.vfx_events.pop(0)
            etype = ev.get('type')

            if etype == 'slash':
                fx = bx + ev['fc'] * ts + ts // 2
                fy = by + ev['fr'] * ts + ts // 2
                tx = bx + ev['tc'] * ts + ts // 2
                ty = by + ev['tr'] * ts + ts // 2
                f_code = ev.get('p', 'S')
                f_data = next((f for f in FACTIONS.values() if f['code'] == f_code), None)
                f_col = f_data['color'] if f_data else (255, 215, 0)
                self.slashes.append(SlashEffect(fx, fy, tx, ty, duration=0.20, color=f_col))
                self.add_combat_sparks(tx, ty, count=8, color=f_col)

            elif etype == 'impact':
                tx = bx + ev['c'] * ts + ts // 2
                ty = by + ev['r'] * ts + ts // 2
                self.shockwaves.append(Shockwave(tx, ty, max_radius=36, speed=160, color=(255, 120, 60), width=3))
                self.add_combat_sparks(tx, ty, count=6, color=(255, 220, 100))

            elif etype == 'death_burst':
                tx = bx + ev['c'] * ts + ts // 2
                ty = by + ev['r'] * ts + ts // 2
                p = ev.get('p', 'S')
                f_data = next((f for f in FACTIONS.values() if f['code'] == p), None)
                col = f_data['color'] if f_data else (255, 60, 60)
                self.shockwaves.append(Shockwave(tx, ty, max_radius=52, speed=180, color=col, width=4))
                self.shockwaves.append(Shockwave(tx, ty, max_radius=35, speed=120, color=(255, 255, 255), width=2))
                self.add_explosion_particles(tx, ty, count=18, color=col)

            elif etype == 'flag_pickup':
                tx = bx + ev['c'] * ts + ts // 2
                ty = by + ev['r'] * ts + ts // 2
                self.shockwaves.append(Shockwave(tx, ty, max_radius=46, speed=140, color=(255, 215, 0), width=4))
                self.add_divine_rays(tx, ty, count=12)

            elif etype == 'pickup_special':
                tx = bx + ev['c'] * ts + ts // 2
                ty = by + ev['r'] * ts + ts // 2
                sp = ev.get('sp')
                col = (255, 60, 110) if sp == 'H' else ((255, 215, 0) if sp == 'I' else (255, 50, 50))
                self.shockwaves.append(Shockwave(tx, ty, max_radius=32, speed=130, color=col, width=2))
                self.add_sparkles(tx, ty, count=10, color=col)

            elif etype == 'spell_cast':
                tx = bx + ev['c'] * ts + ts // 2
                ty = by + ev['r'] * ts + ts // 2
                cid = ev.get('cid', '')
                col = (0, 200, 255) if cid in ('AURA', 'PORTAL', 'GRILLETE') else ((255, 90, 30) if cid in ('IMPACTO', 'CENIZA') else (255, 215, 0))
                self.shockwaves.append(Shockwave(tx, ty, max_radius=48, speed=150, color=col, width=3))
                self.add_spell_runes(tx, ty, count=12, color=col)

            elif etype == 'deploy_burst':
                tx = bx + ev['c'] * ts + ts // 2
                ty = by + ev['r'] * ts + ts // 2
                self.shockwaves.append(Shockwave(tx, ty, max_radius=32, speed=130, color=(78, 205, 145), width=3))
                self.add_sparkles(tx, ty, count=10, color=(120, 255, 180))

            elif etype == 'teleport_burst':
                tx = bx + ev['c'] * ts + ts // 2
                ty = by + ev['r'] * ts + ts // 2
                self.shockwaves.append(Shockwave(tx, ty, max_radius=42, speed=160, color=(56, 189, 248), width=3))
                self.add_spell_runes(tx, ty, count=14, color=(56, 189, 248))

            elif etype == 'victory_burst':
                cx = bx + self.board_size // 2
                cy = by + self.board_size // 2
                self.shockwaves.append(Shockwave(cx, cy, max_radius=220, speed=260, color=(255, 215, 0), width=6))
                for _ in range(35):
                    rx = bx + random.randint(0, self.board_size)
                    ry = by + random.randint(0, self.board_size)
                    self.add_sparkles(rx, ry, count=6, color=(255, 215, 0))

            elif etype == 'shake':
                self.trigger_shake(ev.get('trauma', 3.0))

    def update_particles(self, dt):
        self.anim_time += dt

        if self.shake_trauma > 0:
            self.shake_trauma = max(0.0, self.shake_trauma - dt * 24.0)
            mag = self.shake_trauma
            self.shake_offset = (random.uniform(-mag, mag), random.uniform(-mag, mag))
        else:
            self.shake_offset = (0, 0)

        self.particles = [p for p in self.particles if p.update(dt)]
        self.shockwaves = [s for s in self.shockwaves if s.update(dt)]
        self.slashes = [sl for sl in self.slashes if sl.update(dt)]

    def draw_particles(self):
        for s in self.shockwaves:
            s.draw(self.screen)
        for sl in self.slashes:
            sl.draw(self.screen)
        for p in self.particles:
            p.draw(self.screen)

    def get_tile_at(self, mouse_pos):
        mx, my = mouse_pos
        bx = self.board_x + int(self.shake_offset[0])
        by = self.board_y + int(self.shake_offset[1])
        if bx <= mx < bx + self.board_size and by <= my < by + self.board_size:
            c = (mx - bx) // self.tile_size
            r = (my - by) // self.tile_size
            if 0 <= r < N and 0 <= c < N:
                return (r, c)
        return None

    def draw_board(self, game, mouse_pos):
        self.process_vfx_events(game)

        bg = self.assets.get_game_background()
        if bg:
            self.screen.blit(bg, (0, 0))

        bx = self.board_x + int(self.shake_offset[0])
        by = self.board_y + int(self.shake_offset[1])

        border_rect = pygame.Rect(bx - 6, by - 6, self.board_size + 12, self.board_size + 12)
        pygame.draw.rect(self.screen, (59, 47, 28), border_rect, border_radius=8)
        pygame.draw.rect(self.screen, (22, 18, 12), border_rect, 2, border_radius=8)
        pygame.draw.rect(self.screen, (0, 0, 0), (bx, by, self.board_size, self.board_size))

        hovered_tile = None
        ts = self.tile_size

        for r in range(N):
            for c in range(N):
                tx = bx + c * ts
                ty = by + r * ts
                t_rect = pygame.Rect(tx, ty, ts, ts)

                if t_rect.collidepoint(mouse_pos):
                    hovered_tile = (r, c)

                is_center = LO <= r <= HI and LO <= c <= HI
                is_trench = (r < 2 or r > N - 3 or c < 2 or c > N - 3) and not is_center
                is_light = (r + c) % 2 == 0

                if is_center:
                    col = (125, 122, 99) if is_light else (79, 77, 61)
                elif is_trench:
                    col = (110, 90, 56) if is_light else (73, 58, 32)
                else:
                    col = (154, 132, 96) if is_light else (107, 86, 54)

                pygame.draw.rect(self.screen, col, t_rect)

                if is_center:
                    pygame.draw.rect(self.screen, (160, 60, 35), t_rect, 1)
                    sun_pulse = int(20 + 14 * math.sin(self.anim_time * 3.5 + (r + c) * 0.45))
                    sun_glow = pygame.Surface((ts, ts), pygame.SRCALPHA)
                    sun_glow.fill((255, 175, 45, sun_pulse))
                    self.screen.blit(sun_glow, (tx, ty))
                else:
                    pygame.draw.rect(self.screen, (35, 28, 18), t_rect, 1)

                if (r == 0 and c == N - 1) or (r == N - 1 and c == 0):
                    bastion_glow = int(140 + 60 * math.sin(self.anim_time * 4.0))
                    pygame.draw.rect(self.screen, (255, 235, 120, bastion_glow), t_rect, 2)
                    self.draw_vector_star(self.screen, tx + ts - 14, ty + 3, size=10, color=(255, 235, 120))
                    if random.random() < 0.08:
                        self.particles.append(Particle(
                            tx + random.randint(4, ts - 4),
                            ty + random.randint(4, ts - 4),
                            random.uniform(-4, 4), -18,
                            (255, 235, 140), life=0.55, size=2
                        ))

                if hovered_tile == (r, c) and not game.selected:
                    hover_surf = pygame.Surface((ts, ts), pygame.SRCALPHA)
                    hover_surf.fill((255, 255, 255, 35))
                    self.screen.blit(hover_surf, (tx, ty))
                    pygame.draw.rect(self.screen, (255, 235, 160, 100), t_rect, 1)

                if game.selected == (r, c):
                    pulse = math.sin(self.anim_time * 6.0)
                    alpha = int(120 + 35 * pulse)
                    highlight = pygame.Surface((ts, ts), pygame.SRCALPHA)
                    highlight.fill((255, 215, 0, alpha))
                    self.screen.blit(highlight, (tx, ty))

                    bracket_len = int(ts * 0.30)
                    bracket_off = int(2 + pulse * 1.5)
                    gold = (255, 235, 100)
                    pygame.draw.line(self.screen, gold, (tx + bracket_off, ty + bracket_off), (tx + bracket_off + bracket_len, ty + bracket_off), 2)
                    pygame.draw.line(self.screen, gold, (tx + bracket_off, ty + bracket_off), (tx + bracket_off, ty + bracket_off + bracket_len), 2)
                    pygame.draw.line(self.screen, gold, (tx + ts - bracket_off, ty + bracket_off), (tx + ts - bracket_off - bracket_len, ty + bracket_off), 2)
                    pygame.draw.line(self.screen, gold, (tx + ts - bracket_off, ty + bracket_off), (tx + ts - bracket_off, ty + bracket_off + bracket_len), 2)
                    pygame.draw.line(self.screen, gold, (tx + bracket_off, ty + ts - bracket_off), (tx + bracket_off + bracket_len, ty + ts - bracket_off), 2)
                    pygame.draw.line(self.screen, gold, (tx + bracket_off, ty + ts - bracket_off), (tx + bracket_off, ty + ts - bracket_off - bracket_len), 2)
                    pygame.draw.line(self.screen, gold, (tx + ts - bracket_off, ty + ts - bracket_off), (tx + ts - bracket_off - bracket_len, ty + ts - bracket_off), 2)
                    pygame.draw.line(self.screen, gold, (tx + ts - bracket_off, ty + ts - bracket_off), (tx + ts - bracket_off, ty + ts - bracket_off - bracket_len), 2)

                if (r, c) in game.moves:
                    target_piece = game.board[r][c]
                    if target_piece and target_piece != 'BLOCKED':
                        pulse = math.sin(self.anim_time * 8.0)
                        alpha = int(120 + 40 * pulse)
                        highlight = pygame.Surface((ts, ts), pygame.SRCALPHA)
                        highlight.fill((229, 57, 53, alpha))
                        self.screen.blit(highlight, (tx, ty))

                        b_len = int(ts * 0.28)
                        b_off = int(2 + pulse * 1.2)
                        red = (255, 60, 60)
                        pygame.draw.line(self.screen, red, (tx + b_off, ty + b_off), (tx + b_off + b_len, ty + b_off), 2)
                        pygame.draw.line(self.screen, red, (tx + b_off, ty + b_off), (tx + b_off, ty + b_off + b_len), 2)
                        pygame.draw.line(self.screen, red, (tx + ts - b_off, ty + b_off), (tx + ts - b_off - b_len, ty + b_off), 2)
                        pygame.draw.line(self.screen, red, (tx + ts - b_off, ty + b_off), (tx + ts - b_off, ty + b_off + b_len), 2)
                        pygame.draw.line(self.screen, red, (tx + b_off, ty + ts - b_off), (tx + b_off + b_len, ty + ts - b_off), 2)
                        pygame.draw.line(self.screen, red, (tx + b_off, ty + ts - b_off), (tx + b_off, ty + ts - b_off - b_len), 2)
                        pygame.draw.line(self.screen, red, (tx + ts - b_off, ty + ts - b_off), (tx + ts - b_off - b_len, ty + ts - b_off), 2)
                        pygame.draw.line(self.screen, red, (tx + ts - b_off, ty + ts - b_off), (tx + ts - b_off, ty + ts - b_off - b_len), 2)
                        pygame.draw.circle(self.screen, (255, 230, 230), (tx + ts // 2, ty + ts // 2), 2)
                    else:
                        pulse = math.sin(self.anim_time * 6.0)
                        highlight = pygame.Surface((ts, ts), pygame.SRCALPHA)
                        highlight.fill((76, 175, 80, 70))

                        sonar_progress = (self.anim_time * 1.2) % 1.0
                        sonar_r = int(ts * 0.15 + sonar_progress * (ts * 0.32))
                        sonar_a = int(180 * (1.0 - sonar_progress))
                        pygame.draw.circle(highlight, (120, 255, 140, sonar_a), (ts // 2, ts // 2), sonar_r, 1)

                        gem_r = int(ts * 0.16 + pulse * 1.5)
                        pygame.draw.circle(highlight, (165, 255, 170), (ts // 2, ts // 2), gem_r)
                        pygame.draw.circle(highlight, (255, 255, 255), (ts // 2, ts // 2), max(1, gem_r // 2))
                        self.screen.blit(highlight, (tx, ty))

                if game.active_card and game.ok_card_target(game.active_card, r, c):
                    c_pulse = math.sin(self.anim_time * 7.0)
                    highlight = pygame.Surface((ts, ts), pygame.SRCALPHA)
                    highlight.fill((0, 191, 255, int(110 + 35 * c_pulse)))
                    self.screen.blit(highlight, (tx, ty))
                    pygame.draw.rect(self.screen, (0, 220, 255), t_rect, 2)
                    self.draw_vector_gem(self.screen, tx + ts // 2 - 5, ty + ts // 2 - 5, size=10, color=(0, 220, 255))

                if game.deploy_index is not None and game.is_free(r, c) and game.home_zone(game.cur_code(), r, c):
                    highlight = pygame.Surface((ts, ts), pygame.SRCALPHA)
                    highlight.fill((255, 215, 0, 110))
                    self.screen.blit(highlight, (tx, ty))
                    pygame.draw.rect(self.screen, (255, 215, 0), t_rect, 1)

                sp = game.special[r][c]
                if sp:
                    self.draw_special(sp, tx, ty, ts)

                if game.board[r][c] == 'BLOCKED':
                    mcx = tx + ts // 2
                    mcy = ty + ts // 2
                    pygame.draw.circle(self.screen, (255, 80, 0), (mcx, mcy), int(ts * 0.35))
                    pygame.draw.circle(self.screen, (255, 180, 50), (mcx, mcy), int(ts * 0.22))
                    pygame.draw.circle(self.screen, (100, 30, 0), (mcx + 2, mcy - 2), 2)

                val = game.board[r][c]
                if val and val != 'BLOCKED':
                    anim_targets = {(a['tr'], a['tc']) for a in getattr(game, 'move_animations', [])}
                    if (r, c) not in anim_targets:
                        self.draw_piece(val, r, c, tx, ty, ts, game)

                for hr, hc, ht in game.hit_effects:
                    if hr == r and hc == c:
                        flash = pygame.Surface((ts, ts), pygame.SRCALPHA)
                        flash.fill((255, 255, 255, int(200 * (ht / 0.35))))
                        self.screen.blit(flash, (tx, ty))

                if game.flag['r'] == r and game.flag['c'] == c and not game.flag['carried']:
                    self.draw_sacred_flag(self.screen, tx + ts // 2, ty + ts // 2, size=int(ts * 0.85), anim_time=self.anim_time)
                    if random.random() < 0.22:
                        self.particles.append(Particle(
                            tx + ts // 2 + random.randint(-8, 8),
                            ty + ts // 2 + 6,
                            random.uniform(-8, 8), random.uniform(-35, -15),
                            (255, 215, 60), life=0.6, size=2, gravity=-10.0
                        ))

        for anim in getattr(game, 'move_animations', []):
            dur = max(0.001, anim.get('duration', 0.22))
            progress = min(1.0, max(0.0, anim.get('time', 0.0) / dur))
            ease = 1.0 - (1.0 - progress) ** 3
            fr, fc = anim['fr'], anim['fc']
            tr, tc = anim['tr'], anim['tc']
            fx = bx + fc * ts
            fy = by + fr * ts
            tx = bx + tc * ts
            ty = by + tr * ts
            cur_x = fx + (tx - fx) * ease
            cur_y = fy + (ty - fy) * ease

            f_code = anim['piece'][0]
            f_data = next((f for f in FACTIONS.values() if f['code'] == f_code), None)
            f_col = f_data['color'] if f_data else (255, 215, 0)

            trail = pygame.Surface((ts, ts), pygame.SRCALPHA)
            pygame.draw.circle(trail, (f_col[0], f_col[1], f_col[2], int(130 * (1.0 - progress))), (ts // 2, ts // 2), int(ts * 0.44))
            self.screen.blit(trail, (cur_x, cur_y))

            if progress < 0.90 and random.random() < 0.50:
                self.particles.append(Particle(
                    cur_x + ts // 2 + random.randint(-4, 4),
                    cur_y + ts // 2 + random.randint(-4, 4),
                    random.uniform(-10, 10), random.uniform(-10, 10),
                    f_col, life=0.35, size=2
                ))

            self.draw_piece_at_pixel(anim['piece'], tr, tc, cur_x, cur_y, ts, game, force_carrier=anim.get('carrier', False))

        return hovered_tile

    def draw_special(self, sp, tx, ty, ts):
        sp_size = int(ts * 0.82)
        sp_surf = self.assets.get_special_image(sp, size=(sp_size, sp_size)) or PieceGraphics.get_special_surface(sp, size=sp_size)
        px = tx + (ts - sp_surf.get_width()) // 2
        py = ty + (ts - sp_surf.get_height()) // 2
        self.screen.blit(sp_surf, (px, py))

    def draw_piece(self, piece_str, r, c, tx, ty, ts, game):
        self.draw_piece_at_pixel(piece_str, r, c, tx, ty, ts, game)

    def draw_piece_at_pixel(self, piece_str, r, c, px, py, ts, game, force_carrier=False):
        p, utype = piece_str.split('_')

        if (r, c) in game.shields:
            glow = pygame.Surface((ts, ts), pygame.SRCALPHA)
            glow_a = int(140 + 40 * math.sin(self.anim_time * 6.0))
            pygame.draw.circle(glow, (0, 191, 255, glow_a), (ts // 2, ts // 2), int(ts * 0.45), 3)
            self.screen.blit(glow, (px, py))

        if force_carrier or game.is_carrier(r, c):
            halo_size = int(ts * 0.95)
            halo_surf = pygame.Surface((halo_size, halo_size), pygame.SRCALPHA)
            h_center = halo_size // 2
            halo_a = int(140 + 50 * math.sin(self.anim_time * 6.0))
            pygame.draw.circle(halo_surf, (255, 215, 0, halo_a), (h_center, h_center), int(halo_size * 0.45), 2)
            for st_i in range(3):
                ang = self.anim_time * 3.0 + st_i * (2 * math.pi / 3)
                sx = int(h_center + math.cos(ang) * (halo_size * 0.44))
                sy = int(h_center + math.sin(ang) * (halo_size * 0.44))
                pygame.draw.circle(halo_surf, (255, 245, 170), (sx, sy), 2)
            self.screen.blit(halo_surf, (px + (ts - halo_size) // 2, py + (ts - halo_size) // 2))

        is_frozen = (r, c) in game.frozen and game.frozen[(r, c)]['active']

        piece_size = int(ts * 0.82)
        piece_surf = self.assets.get_piece_image(p, utype, size=(piece_size, piece_size)) or PieceGraphics.get_piece_surface(p, utype, size=piece_size)

        if is_frozen:
            piece_surf = piece_surf.copy()
            piece_surf.fill((160, 180, 220, 210), special_flags=pygame.BLEND_RGBA_MULT)

        pos_x = px + (ts - piece_surf.get_width()) // 2
        pos_y = py + (ts - piece_surf.get_height()) // 2
        self.screen.blit(piece_surf, (pos_x, pos_y))

        if is_frozen:
            frost = pygame.Surface((ts, ts), pygame.SRCALPHA)
            pygame.draw.line(frost, (180, 230, 255, 180), (ts // 4, ts // 4), (3 * ts // 4, 3 * ts // 4), 2)
            pygame.draw.line(frost, (180, 230, 255, 180), (3 * ts // 4, ts // 4), (ts // 4, 3 * ts // 4), 2)
            self.screen.blit(frost, (px, py))

        if force_carrier or game.is_carrier(r, c):
            self.draw_mini_flag(self.screen, px + ts - 10, py + 2, size=13, anim_time=self.anim_time)

        current_hp = game.hp.get((r, c), 1)
        hp_str = str(current_hp)
        hp_surf = self.font_hp.render(hp_str, True, (255, 255, 255))
        badge_w = hp_surf.get_width() + 6
        badge_h = 13
        hp_bg = pygame.Rect(px + ts - badge_w - 2, py + ts - badge_h - 1, badge_w, badge_h)
        pygame.draw.rect(self.screen, (0, 0, 0, 220), hp_bg, border_radius=3)
        pygame.draw.rect(self.screen, (255, 255, 255, 60), hp_bg, 1, border_radius=3)
        self.screen.blit(hp_surf, (hp_bg.x + 3, hp_bg.y - 1))

    def draw_hud(self, game, mouse_pos):
        right_x = 690
        panel_w = 560
        y = 10

        cur_f = FACTIONS[ORDER[game.idx]]
        is_human = game.is_human_turn()
        turn_str = f"Turno: {cur_f['name']}  ·  PA {game.ap}/2 {'(tú)' if is_human else '(IA)'}"
        banner_rect = pygame.Rect(right_x, y, panel_w, 34)
        pygame.draw.rect(self.screen, cur_f['bg'], banner_rect, border_radius=6)
        pygame.draw.rect(self.screen, cur_f['color'], banner_rect, 1, border_radius=6)
        pygame.draw.rect(self.screen, cur_f['color'], (right_x, y, 4, 34), border_radius=2)

        turn_lbl = self.font_header.render(turn_str, True, cur_f['color'])
        self.screen.blit(turn_lbl, (banner_rect.centerx - turn_lbl.get_width() // 2, banner_rect.centery - turn_lbl.get_height() // 2))

        y += 38

        lives_rect = pygame.Rect(right_x, y, panel_w, 74)
        pygame.draw.rect(self.screen, (26, 18, 14), lives_rect, border_radius=8)
        pygame.draw.rect(self.screen, (160, 50, 75), lives_rect, 1, border_radius=8)

        cur_lives = game.lives.get(game.human, 3)
        if cur_lives >= 3:
            tag_str = "ÓPTIMO"
            tag_col = (78, 205, 145)
            tag_bg = (20, 50, 35)
        elif cur_lives == 2:
            tag_str = "ALERTA"
            tag_col = (255, 215, 0)
            tag_bg = (60, 50, 15)
        else:
            tag_str = "PELIGRO"
            tag_col = (255, 50, 80)
            tag_bg = (70, 20, 25)

        cmd_name = FACTIONS[next(k for k in ORDER if FACTIONS[k]['code'] == game.human)]['name']
        lbl_cmd = self.font_bold.render(f"Comandante {cmd_name}:", True, (255, 215, 225))
        self.screen.blit(lbl_cmd, (right_x + 12, y + 6))

        tag_surf = self.font_badge.render(tag_str, True, tag_col)
        tag_rect = pygame.Rect(right_x + panel_w - tag_surf.get_width() - 24, y + 5, tag_surf.get_width() + 14, 16)
        pygame.draw.rect(self.screen, tag_bg, tag_rect, border_radius=8)
        pygame.draw.rect(self.screen, tag_col, tag_rect, 1, border_radius=8)
        pygame.draw.circle(self.screen, tag_col, (tag_rect.x + 6, tag_rect.centery), 3)
        self.screen.blit(tag_surf, (tag_rect.x + 12, tag_rect.y + 1))

        for i in range(5):
            hx = right_x + 12 + i * 18
            hy = y + 24
            self.draw_vector_heart(self.screen, hx, hy, size=15, filled=(i < cur_lives))

        cnt_lbl = self.font_small.render(f"({cur_lives}/5)", True, (255, 120, 140))
        self.screen.blit(cnt_lbl, (right_x + 106, y + 25))

        h_board = game.count_specials('H')
        i_board = game.count_specials('I')
        x_board = game.count_specials('X')

        self.draw_vector_heart(self.screen, right_x + 175, y + 25, size=13, filled=True, color=(255, 75, 110))
        h_lbl = self.font_small.render(f"{h_board} Vidas", True, (255, 190, 205))
        self.screen.blit(h_lbl, (right_x + 192, y + 25))

        self.draw_vector_lightning(self.screen, right_x + 265, y + 25, size=13)
        i_lbl = self.font_small.render(f"{i_board} Rayos", True, (255, 230, 160))
        self.screen.blit(i_lbl, (right_x + 282, y + 25))

        self.draw_vector_trap(self.screen, right_x + 355, y + 25, size=13)
        x_lbl = self.font_small.render(f"{x_board} Trampas", True, (255, 160, 160))
        self.screen.blit(x_lbl, (right_x + 372, y + 25))

        pill_w = (panel_w - 28) // 4
        for i, code in enumerate(['S', 'A', 'J', 'K']):
            px = right_x + 8 + i * (pill_w + 4)
            py = y + 44
            f_data = next(f for f in FACTIONS.values() if f['code'] == code)
            is_elim = any(k for k in game.eliminated if FACTIONS[k]['code'] == code)
            is_turn = game.cur_code() == code

            p_rect = pygame.Rect(px, py, pill_w, 24)
            p_bg = (45, 15, 15) if is_elim else ((35, 30, 20) if is_turn else (18, 16, 14))
            pygame.draw.rect(self.screen, p_bg, p_rect, border_radius=4)
            pygame.draw.rect(self.screen, f_data['color'] if not is_elim else (100, 50, 50), p_rect, 2 if is_turn else 1, border_radius=4)
            pygame.draw.rect(self.screen, f_data['color'], (px, py, 3, 24), border_radius=2)

            role = "(Tú)" if code == game.human else ("(Aliado)" if TEAM[code] == TEAM[game.human] else "(Enemigo)")
            txt = self.font_badge.render(f"{f_data['name'][:5]} {role}", True, f_data['color'])
            self.screen.blit(txt, (px + 6, py + 5))

            if is_elim:
                e_txt = self.font_badge.render("ELIMINADO", True, (255, 70, 70))
                self.screen.blit(e_txt, (px + pill_w - e_txt.get_width() - 4, py + 5))
            else:
                l_cnt = game.lives.get(code, 0)
                for k in range(min(5, l_cnt)):
                    self.draw_vector_heart(self.screen, px + pill_w - 6 - (min(5, l_cnt) - k) * 9, py + 7, size=8, filled=True, color=f_data['color'])

        y += 80

        oracle_h = 84
        oracle_rect = pygame.Rect(right_x, y, panel_w, oracle_h)
        pygame.draw.rect(self.screen, (16, 12, 24), oracle_rect, border_radius=8)
        pygame.draw.rect(self.screen, (168, 85, 247), oracle_rect, 1, border_radius=8)
        pygame.draw.rect(self.screen, (56, 189, 248), (right_x, y, 4, oracle_h), border_radius=2)

        orb_icon = self.assets.get_icon('btn_oracle', (24, 24))
        if orb_icon:
            pulse_a = int(120 + 70 * math.sin(self.anim_time * 4.0))
            orb_glow = pygame.Surface((28, 28), pygame.SRCALPHA)
            pygame.draw.circle(orb_glow, (168, 85, 247, pulse_a), (14, 14), 13)
            self.screen.blit(orb_glow, (right_x + 8, y + 4))
            self.screen.blit(orb_icon, (right_x + 10, y + 6))
            title_x = right_x + 38
        else:
            title_x = right_x + 12

        lbl_oracle = self.font_bold.render("ORÁCULO ANCESTRAL TÁCTICO", True, (240, 225, 255))
        self.screen.blit(lbl_oracle, (title_x, y + 8))

        status_str = self.oracle.get_status()
        if status_str == "Online":
            st_col = (56, 189, 248)
            st_bg = (15, 35, 50)
            st_text = "Sincronizado"
        elif status_str == "Analizando...":
            st_col = (255, 200, 50)
            st_bg = (55, 40, 15)
            st_text = "Meditando..."
        else:
            st_col = (192, 132, 252)
            st_bg = (38, 22, 55)
            st_text = "Modo Ancestral"

        st_surf = self.font_badge.render(st_text, True, st_col)
        st_rect = pygame.Rect(title_x + lbl_oracle.get_width() + 10, y + 8, st_surf.get_width() + 16, 16)
        pygame.draw.rect(self.screen, st_bg, st_rect, border_radius=8)
        pygame.draw.rect(self.screen, st_col, st_rect, 1, border_radius=8)
        pygame.draw.circle(self.screen, st_col, (st_rect.x + 6, st_rect.centery), 3)
        self.screen.blit(st_surf, (st_rect.x + 12, st_rect.y + 1))

        if status_str == "Analizando...":
            for wi in range(4):
                wh = int(4 + 8 * abs(math.sin(self.anim_time * 8.0 + wi * 0.8)))
                wx = st_rect.right + 8 + wi * 5
                wy = st_rect.centery - wh // 2
                pygame.draw.line(self.screen, (255, 215, 0), (wx, wy), (wx, wy + wh), 2)

        btn_oracle = pygame.Rect(right_x + panel_w - 175, y + 6, 165, 22)
        hover_oracle = btn_oracle.collidepoint(mouse_pos)
        or_bg = (120, 60, 190) if hover_oracle else (75, 35, 125)
        border_or = (230, 200, 255) if hover_oracle else (168, 85, 247)
        pygame.draw.rect(self.screen, or_bg, btn_oracle, border_radius=5)
        pygame.draw.rect(self.screen, border_or, btn_oracle, 1, border_radius=5)
        self.draw_vector_star(self.screen, btn_oracle.x + 8, btn_oracle.y + 5, size=11, color=(255, 235, 120))
        or_txt = self.font_badge.render("Consultar al Oráculo", True, (255, 255, 255))
        self.screen.blit(or_txt, (btn_oracle.x + 24, btn_oracle.centery - or_txt.get_height() // 2))

        speech_rect = pygame.Rect(right_x + 8, y + 32, panel_w - 16, 46)
        pygame.draw.rect(self.screen, (10, 8, 16), speech_rect, border_radius=6)
        pygame.draw.rect(self.screen, (75, 55, 105), speech_rect, 1, border_radius=6)
        pygame.draw.line(self.screen, (147, 51, 234, 140), (speech_rect.left + 8, speech_rect.top + 1), (speech_rect.right - 8, speech_rect.top + 1), 1)

        raw_advice = self.oracle.get_advice()
        lines = self.wrap_text(f"\"{raw_advice}\"", self.font_oracle_italic, speech_rect.width - 18, max_lines=2)
        for li, line_text in enumerate(lines):
            line_surf = self.font_oracle_italic.render(line_text, True, (240, 235, 250))
            self.screen.blit(line_surf, (speech_rect.x + 10, speech_rect.y + 5 + li * 18))

        y += 90

        cards_box = pygame.Rect(right_x, y, panel_w, 134)
        pygame.draw.rect(self.screen, (24, 20, 15), cards_box, border_radius=8)
        pygame.draw.rect(self.screen, (61, 49, 28), cards_box, 1, border_radius=8)

        self.draw_vector_star(self.screen, right_x + 12, y + 8, size=13, color=COLOR_TEXT_GOLD)
        lbl_cards = self.font_bold.render("MAZO TÁCTICO · HECHIZOS ANCESTRALES (1 USO)", True, COLOR_TEXT_GOLD)
        self.screen.blit(lbl_cards, (right_x + 30, y + 6))

        card_buttons = []
        cur_p = game.cur_code()
        from src.constants import FACTION_HANDS
        available_cards = FACTION_HANDS.get(cur_p, [])

        c_w = (panel_w - 32) // 3
        c_h = 100
        for ci, cid in enumerate(available_cards):
            c_data = CARDS[cid]
            is_used = cid in game.used_cards[cur_p]
            is_active = game.active_card == cid
            cx = right_x + 10 + ci * (c_w + 6)
            cy = y + 26
            cb_rect = pygame.Rect(cx, cy, c_w, c_h)
            card_buttons.append((cb_rect, cid))

            if is_used:
                bg = (18, 16, 14)
                border_col = (60, 50, 40)
            elif is_active:
                bg = (30, 48, 65)
                border_col = (0, 191, 255)
            else:
                bg = (36, 29, 21)
                border_col = cur_f['color']

            c_hover = cb_rect.collidepoint(mouse_pos) and not is_used
            if is_active:
                p_alpha = int(70 + 35 * math.sin(self.anim_time * 6.0))
                halo = pygame.Surface((cb_rect.width + 8, cb_rect.height + 8), pygame.SRCALPHA)
                pygame.draw.rect(halo, (0, 191, 255, p_alpha), (0, 0, cb_rect.width + 8, cb_rect.height + 8), border_radius=8)
                self.screen.blit(halo, (cb_rect.x - 4, cb_rect.y - 4))
            elif c_hover:
                halo = pygame.Surface((cb_rect.width + 6, cb_rect.height + 6), pygame.SRCALPHA)
                pygame.draw.rect(halo, (255, 215, 60, 40), (0, 0, cb_rect.width + 6, cb_rect.height + 6), border_radius=8)
                self.screen.blit(halo, (cb_rect.x - 3, cb_rect.y - 3))

            pygame.draw.rect(self.screen, bg, cb_rect, border_radius=6)
            pygame.draw.rect(self.screen, border_col, cb_rect, 2 if is_active or c_hover else 1, border_radius=6)

            gem_rect = pygame.Rect(cx + 6, cy + 4, 46, 14)
            pygame.draw.rect(self.screen, (0, 120, 220), gem_rect, border_radius=7)
            self.draw_vector_gem(self.screen, gem_rect.x + 5, gem_rect.y + 2, size=10)
            gem_txt = self.font_badge.render("1 PA", True, (255, 255, 255))
            self.screen.blit(gem_txt, (gem_rect.x + 18, gem_rect.y))

            type_txt = self.font_badge.render(c_data['type'], True, (173, 159, 136))
            self.screen.blit(type_txt, (cx + c_w - type_txt.get_width() - 8, cy + 5))

            art_rect = pygame.Rect(cx + 6, cy + 20, c_w - 12, 32)
            pygame.draw.rect(self.screen, (15, 12, 8), art_rect, border_radius=4)
            card_img = self.assets.get_card_image(cid, (art_rect.width - 2, art_rect.height - 2))
            if card_img:
                self.screen.blit(card_img, (art_rect.x + 1, art_rect.y + 1))
            else:
                icon_txt = self.font_header.render(c_data['name'][:3], True, COLOR_TEXT_GOLD)
                self.screen.blit(icon_txt, (art_rect.centerx - icon_txt.get_width() // 2, art_rect.centery - icon_txt.get_height() // 2))
            pygame.draw.rect(self.screen, (80, 65, 40), art_rect, 1, border_radius=4)

            c_name = self.font_bold.render(c_data['name'], True, (140, 130, 120) if is_used else COLOR_TEXT_GOLD)
            self.screen.blit(c_name, (cx + 6, cy + 56))

            desc_snip = c_data['desc'][:32] + ("..." if len(c_data['desc']) > 32 else "")
            d_txt = self.font_small.render(desc_snip, True, (190, 180, 170) if not is_used else (110, 100, 90))
            self.screen.blit(d_txt, (cx + 6, cy + 70))

            footer_str = "AGOTADO" if is_used else ("ACTIVO" if is_active else "1 USO")
            f_col = (255, 60, 60) if is_used else ((0, 200, 255) if is_active else (255, 215, 0))
            foot_txt = self.font_badge.render(footer_str, True, f_col)
            self.screen.blit(foot_txt, (cx + c_w // 2 - foot_txt.get_width() // 2, cy + 85))

        y += 140

        res_box = pygame.Rect(right_x, y, panel_w, 82)
        pygame.draw.rect(self.screen, (24, 20, 15), res_box, border_radius=8)
        pygame.draw.rect(self.screen, (61, 49, 28), res_box, 1, border_radius=8)

        self.draw_vector_shield(self.screen, right_x + 12, y + 8, size=13, color=COLOR_TEXT_GOLD)
        lbl_res = self.font_bold.render("TROPAS EN RESERVA · DESPLIEGUE TÁCTICO", True, COLOR_TEXT_GOLD)
        self.screen.blit(lbl_res, (right_x + 30, y + 6))

        deploy_buttons = []
        reserves = game.hand_reserves.get(cur_p, [])
        r_w = (panel_w - 32) // 3
        r_h = 48

        for di, utype in enumerate(reserves):
            rx = right_x + 10 + di * (r_w + 6)
            ry = y + 26
            r_rect = pygame.Rect(rx, ry, r_w, r_h)
            deploy_buttons.append((r_rect, di))

            is_sel = game.deploy_index == di
            r_hover = r_rect.collidepoint(mouse_pos)
            bg = (38, 48, 35) if is_sel else (36, 29, 21)
            b_col = (78, 205, 145) if is_sel else (COLOR_TEXT_GOLD if r_hover else cur_f['color'])

            if is_sel:
                p_alpha = int(70 + 35 * math.sin(self.anim_time * 6.0))
                halo = pygame.Surface((r_rect.width + 8, r_rect.height + 8), pygame.SRCALPHA)
                pygame.draw.rect(halo, (78, 205, 145, p_alpha), (0, 0, r_rect.width + 8, r_rect.height + 8), border_radius=8)
                self.screen.blit(halo, (r_rect.x - 4, r_rect.y - 4))
            elif r_hover:
                halo = pygame.Surface((r_rect.width + 6, r_rect.height + 6), pygame.SRCALPHA)
                pygame.draw.rect(halo, (255, 215, 60, 40), (0, 0, r_rect.width + 6, r_rect.height + 6), border_radius=8)
                self.screen.blit(halo, (r_rect.x - 3, r_rect.y - 3))

            pygame.draw.rect(self.screen, bg, r_rect, border_radius=6)
            pygame.draw.rect(self.screen, b_col, r_rect, 2 if is_sel or r_hover else 1, border_radius=6)

            mini_piece = self.assets.get_piece_image(cur_p, utype, size=(24, 24)) or PieceGraphics.get_piece_surface(cur_p, utype, size=24)
            self.screen.blit(mini_piece, (rx + 6, ry + (r_h - 24) // 2))

            u_name = self.font_bold.render(UNIT_NAMES[utype], True, COLOR_TEXT_LIGHT)
            self.screen.blit(u_name, (rx + 34, ry + 4))

            self.draw_vector_gem(self.screen, rx + 34, ry + 24, size=10)
            t_gem = self.font_badge.render(f"{UNIT_COST[utype]} PA", True, COLOR_TEXT_GOLD)
            self.screen.blit(t_gem, (rx + 47, ry + 22))

            self.draw_vector_sword(self.screen, rx + 78, ry + 24, size=10)
            t_atk = self.font_badge.render(f"{ATK[utype]}", True, (255, 140, 140))
            self.screen.blit(t_atk, (rx + 91, ry + 22))

            self.draw_vector_heart(self.screen, rx + 108, ry + 24, size=10, filled=True, color=(110, 230, 180))
            t_hp = self.font_badge.render(f"{MAX_HP[utype]}", True, (110, 230, 180))
            self.screen.blit(t_hp, (rx + 121, ry + 22))

        if not reserves:
            empty_txt = self.font_small.render("Sin tropas en reserva", True, (140, 130, 120))
            self.screen.blit(empty_txt, (right_x + 18, y + 36))

        y += 88

        log_box = pygame.Rect(right_x, y, panel_w, 76)
        pygame.draw.rect(self.screen, (10, 9, 6), log_box, border_radius=6)
        pygame.draw.rect(self.screen, (51, 43, 27), log_box, 1, border_radius=6)

        recent_logs = game.log_messages[-3:]
        for li, lmsg in enumerate(recent_logs):
            lt = self.font_small.render(f"> {lmsg}", True, (175, 165, 150))
            self.screen.blit(lt, (right_x + 8, y + 6 + li * 22))

        y += 82

        btn_end = pygame.Rect(right_x, y, 270, 40)
        btn_menu = pygame.Rect(right_x + 290, y, 270, 40)

        can_end = is_human
        end_hover = can_end and btn_end.collidepoint(mouse_pos)
        end_bg = (245, 205, 30) if end_hover else ((195, 150, 15) if can_end else (42, 36, 28))
        border_end = (255, 245, 160) if end_hover else ((230, 180, 20) if can_end else (65, 55, 42))

        if end_hover:
            glow_surf = pygame.Surface((btn_end.width + 6, btn_end.height + 6), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (255, 215, 60, 45), (0, 0, btn_end.width + 6, btn_end.height + 6), border_radius=8)
            self.screen.blit(glow_surf, (btn_end.x - 3, btn_end.y - 3))

        pygame.draw.rect(self.screen, end_bg, btn_end, border_radius=6)
        pygame.draw.rect(self.screen, border_end, btn_end, 2 if end_hover else 1, border_radius=6)
        self.draw_vector_sword(self.screen, btn_end.centerx - 85, btn_end.centery - 6, size=12, color=(12, 10, 5) if can_end else (110, 100, 90))
        end_txt = self.font_bold.render("TERMINAR TURNO", True, (12, 10, 5) if can_end else (120, 110, 100))
        self.screen.blit(end_txt, (btn_end.centerx - end_txt.get_width() // 2 + 10, btn_end.centery - end_txt.get_height() // 2))

        menu_hover = btn_menu.collidepoint(mouse_pos)
        menu_bg = (54, 44, 62) if menu_hover else (32, 26, 38)
        border_menu = (168, 85, 247) if menu_hover else (90, 75, 105)
        pygame.draw.rect(self.screen, menu_bg, btn_menu, border_radius=6)
        pygame.draw.rect(self.screen, border_menu, btn_menu, 2 if menu_hover else 1, border_radius=6)
        self.draw_vector_shield(self.screen, btn_menu.centerx - 70, btn_menu.centery - 7, size=13, color=(220, 205, 245) if menu_hover else (170, 155, 195))
        menu_txt = self.font_bold.render("PAUSA / MENÚ", True, (245, 240, 255) if menu_hover else COLOR_TEXT_LIGHT)
        self.screen.blit(menu_txt, (btn_menu.centerx - menu_txt.get_width() // 2 + 10, btn_menu.centery - menu_txt.get_height() // 2))

        return {
            'end_turn': btn_end,
            'menu': btn_menu,
            'cards': card_buttons,
            'deploy': deploy_buttons,
            'oracle': btn_oracle
        }

    def draw_tutorial(self, tutorial_controller):
        if tutorial_controller:
            return tutorial_controller.draw_tutorial_overlay(self.screen, self)
        return None

    def draw_floating_popups(self, game):
        ts = self.tile_size
        bx = self.board_x + int(self.shake_offset[0])
        by = self.board_y + int(self.shake_offset[1])
        for pop in game.floating_popups:
            wobble = math.sin(pop['time'] * 9.0) * 2.5
            px = bx + pop['c'] * ts + ts // 2 + wobble
            py = by + pop['r'] * ts - pop['y_offset']

            elapsed = 1.2 - pop['time']
            scale = 1.0
            if elapsed < 0.16:
                scale = 1.0 + 0.35 * (1.0 - elapsed / 0.16)

            text = pop['text']
            color = pop['color']

            txt_surf = self.font_bold.render(text, True, color)
            outline_surf = self.font_bold.render(text, True, (10, 8, 6))

            if scale > 1.02:
                nw = int(txt_surf.get_width() * scale)
                nh = int(txt_surf.get_height() * scale)
                txt_surf = pygame.transform.scale(txt_surf, (nw, nh))
                outline_surf = pygame.transform.scale(outline_surf, (nw, nh))

            gw = txt_surf.get_width()
            gh = txt_surf.get_height()
            draw_x = int(px - gw // 2)
            draw_y = int(py - gh // 2)

            for ox_s in (-1, 0, 1):
                for oy_s in (-1, 0, 1):
                    if ox_s != 0 or oy_s != 0:
                        self.screen.blit(outline_surf, (draw_x + ox_s, draw_y + oy_s))

            self.screen.blit(txt_surf, (draw_x, draw_y))
