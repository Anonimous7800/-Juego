import math
import pygame
from src.constants import FACTIONS

class PieceGraphics:
    _cache = {}

    @classmethod
    def get_piece_surface(cls, faction_code, piece_type, size=36):
        key = (faction_code, piece_type, size)
        if key in cls._cache:
            return cls._cache[key]

        hi_size = size * 2
        surf = pygame.Surface((hi_size, hi_size), pygame.SRCALPHA)

        faction = next(f for f in FACTIONS.values() if f['code'] == faction_code)
        color = faction['color']
        dark_col = faction['bg']

        cx = hi_size // 2
        cy = hi_size // 2

        if piece_type == 'P':
            cls._draw_soldier(surf, cx, cy, hi_size, color, dark_col)
        elif piece_type == 'R':
            cls._draw_tank(surf, cx, cy, hi_size, color, dark_col)
        elif piece_type == 'N':
            cls._draw_knight(surf, cx, cy, hi_size, color, dark_col)
        elif piece_type == 'B':
            cls._draw_medic(surf, cx, cy, hi_size, color, dark_col)
        elif piece_type == 'Q':
            cls._draw_officer(surf, cx, cy, hi_size, color, dark_col)
        elif piece_type == 'K':
            cls._draw_general(surf, cx, cy, hi_size, color, dark_col)

        final_surf = pygame.transform.smoothscale(surf, (size, size))
        cls._cache[key] = final_surf
        return final_surf

    @classmethod
    def _draw_soldier(cls, s, cx, cy, sz, col, dark):
        base_w = sz * 0.62
        base_h = sz * 0.12
        pygame.draw.rect(s, (0, 0, 0), (cx - base_w // 2 - 2, cy + sz * 0.28, base_w + 4, base_h + 4), border_radius=3)
        pygame.draw.rect(s, col, (cx - base_w // 2, cy + sz * 0.30, base_w, base_h), border_radius=3)

        body_pts = [
            (cx - sz * 0.12, cy - sz * 0.05),
            (cx + sz * 0.12, cy - sz * 0.05),
            (cx + sz * 0.24, cy + sz * 0.30),
            (cx - sz * 0.24, cy + sz * 0.30)
        ]
        pygame.draw.polygon(s, (0, 0, 0), [(x + (1 if x > cx else -1), y + 1) for x, y in body_pts])
        pygame.draw.polygon(s, col, body_pts)
        pygame.draw.polygon(s, dark, [(cx - sz * 0.16, cy + sz * 0.12), (cx + sz * 0.16, cy + sz * 0.12), (cx + sz * 0.20, cy + sz * 0.28), (cx - sz * 0.20, cy + sz * 0.28)])

        pygame.draw.ellipse(s, (0, 0, 0), (cx - sz * 0.18, cy - sz * 0.10, sz * 0.36, sz * 0.10))
        pygame.draw.ellipse(s, col, (cx - sz * 0.16, cy - sz * 0.09, sz * 0.32, sz * 0.08))

        head_r = sz * 0.17
        pygame.draw.circle(s, (0, 0, 0), (cx, int(cy - sz * 0.22)), int(head_r + 2))
        pygame.draw.circle(s, col, (cx, int(cy - sz * 0.22)), int(head_r))
        pygame.draw.line(s, (0, 0, 0), (cx - sz * 0.10, cy - sz * 0.22), (cx + sz * 0.10, cy - sz * 0.22), 2)

    @classmethod
    def _draw_tank(cls, s, cx, cy, sz, col, dark):
        tread_w = sz * 0.70
        tread_h = sz * 0.14
        pygame.draw.rect(s, (0, 0, 0), (cx - tread_w // 2 - 2, cy + sz * 0.26, tread_w + 4, tread_h + 4), border_radius=4)
        pygame.draw.rect(s, col, (cx - tread_w // 2, cy + sz * 0.28, tread_w, tread_h), border_radius=4)
        for wx in [-sz * 0.22, 0, sz * 0.22]:
            pygame.draw.circle(s, (0, 0, 0), (int(cx + wx), int(cy + sz * 0.35)), int(sz * 0.04))

        wall_pts = [
            (cx - sz * 0.24, cy - sz * 0.10),
            (cx + sz * 0.24, cy - sz * 0.10),
            (cx + sz * 0.28, cy + sz * 0.28),
            (cx - sz * 0.28, cy + sz * 0.28)
        ]
        pygame.draw.polygon(s, (0, 0, 0), [(x + (1 if x > cx else -1), y + 1) for x, y in wall_pts])
        pygame.draw.polygon(s, col, wall_pts)
        pygame.draw.rect(s, dark, (cx - sz * 0.16, cy + sz * 0.04, sz * 0.32, sz * 0.18), border_radius=2)
        pygame.draw.rect(s, (0, 0, 0), (cx - sz * 0.10, cy + sz * 0.08, sz * 0.20, sz * 0.05))

        top_w = sz * 0.58
        top_h = sz * 0.14
        top_y = cy - sz * 0.24
        pygame.draw.rect(s, (0, 0, 0), (cx - top_w // 2 - 2, top_y - 2, top_w + 4, top_h + 4))
        pygame.draw.rect(s, col, (cx - top_w // 2, top_y, top_w, top_h))
        cut_w = sz * 0.09
        cut_h = sz * 0.10
        pygame.draw.rect(s, (0, 0, 0), (cx - cut_w * 1.8, top_y, cut_w, cut_h))
        pygame.draw.rect(s, (0, 0, 0), (cx + cut_w * 0.8, top_y, cut_w, cut_h))

    @classmethod
    def _draw_knight(cls, s, cx, cy, sz, col, dark):
        base_w = sz * 0.62
        base_h = sz * 0.12
        pygame.draw.rect(s, (0, 0, 0), (cx - base_w // 2 - 2, cy + sz * 0.28, base_w + 4, base_h + 4), border_radius=3)
        pygame.draw.rect(s, col, (cx - base_w // 2, cy + sz * 0.30, base_w, base_h), border_radius=3)

        horse_pts = [
            (cx - sz * 0.18, cy + sz * 0.30),
            (cx - sz * 0.26, cy + sz * 0.08),
            (cx - sz * 0.34, cy - sz * 0.06),
            (cx - sz * 0.30, cy - sz * 0.18),
            (cx - sz * 0.16, cy - sz * 0.22),
            (cx - sz * 0.12, cy - sz * 0.34),
            (cx - sz * 0.04, cy - sz * 0.24),
            (cx + sz * 0.04, cy - sz * 0.20),
            (cx + sz * 0.14, cy - sz * 0.06),
            (cx + sz * 0.22, cy + sz * 0.12),
            (cx + sz * 0.24, cy + sz * 0.30)
        ]
        pygame.draw.polygon(s, (0, 0, 0), [(x + (1 if x > cx else -1), y + 1) for x, y in horse_pts])
        pygame.draw.polygon(s, col, horse_pts)

        pygame.draw.circle(s, (0, 0, 0), (int(cx - sz * 0.18), int(cy - sz * 0.14)), int(sz * 0.04))
        pygame.draw.line(s, (0, 0, 0), (cx - sz * 0.18, cy - sz * 0.14), (cx - sz * 0.30, cy - sz * 0.08), 2)
        for my in [-sz * 0.12, -sz * 0.02, sz * 0.08]:
            pygame.draw.line(s, dark, (cx + sz * 0.08, cy + my), (cx + sz * 0.18, cy + my + sz * 0.04), 2)

    @classmethod
    def _draw_medic(cls, s, cx, cy, sz, col, dark):
        base_w = sz * 0.60
        base_h = sz * 0.12
        pygame.draw.rect(s, (0, 0, 0), (cx - base_w // 2 - 2, cy + sz * 0.28, base_w + 4, base_h + 4), border_radius=3)
        pygame.draw.rect(s, col, (cx - base_w // 2, cy + sz * 0.30, base_w, base_h), border_radius=3)

        robe_pts = [
            (cx - sz * 0.14, cy - sz * 0.06),
            (cx + sz * 0.14, cy - sz * 0.06),
            (cx + sz * 0.24, cy + sz * 0.30),
            (cx - sz * 0.24, cy + sz * 0.30)
        ]
        pygame.draw.polygon(s, (0, 0, 0), [(x + (1 if x > cx else -1), y + 1) for x, y in robe_pts])
        pygame.draw.polygon(s, col, robe_pts)

        mitre_pts = [
            (cx - sz * 0.16, cy - sz * 0.06),
            (cx - sz * 0.18, cy - sz * 0.22),
            (cx, cy - sz * 0.36),
            (cx + sz * 0.18, cy - sz * 0.22),
            (cx + sz * 0.16, cy - sz * 0.06)
        ]
        pygame.draw.polygon(s, (0, 0, 0), [(x, y + 1) for x, y in mitre_pts])
        pygame.draw.polygon(s, col, mitre_pts)

        pygame.draw.circle(s, col, (cx, int(cy - sz * 0.36)), int(sz * 0.04))

        cw = sz * 0.06
        cl = sz * 0.22
        pygame.draw.rect(s, (255, 255, 255), (cx - cw // 2, cy + sz * 0.02, cw, cl), border_radius=1)
        pygame.draw.rect(s, (255, 255, 255), (cx - cl // 2, cy + sz * 0.08, cl, cw), border_radius=1)

    @classmethod
    def _draw_officer(cls, s, cx, cy, sz, col, dark):
        base_w = sz * 0.65
        base_h = sz * 0.12
        pygame.draw.rect(s, (0, 0, 0), (cx - base_w // 2 - 2, cy + sz * 0.28, base_w + 4, base_h + 4), border_radius=3)
        pygame.draw.rect(s, col, (cx - base_w // 2, cy + sz * 0.30, base_w, base_h), border_radius=3)

        body_pts = [
            (cx - sz * 0.16, cy - sz * 0.06),
            (cx + sz * 0.16, cy - sz * 0.06),
            (cx + sz * 0.26, cy + sz * 0.30),
            (cx - sz * 0.26, cy + sz * 0.30)
        ]
        pygame.draw.polygon(s, (0, 0, 0), [(x + (1 if x > cx else -1), y + 1) for x, y in body_pts])
        pygame.draw.polygon(s, col, body_pts)

        crown_base_y = cy - sz * 0.08
        points = [
            (cx - sz * 0.26, cy - sz * 0.30),
            (cx - sz * 0.13, cy - sz * 0.16),
            (cx, cy - sz * 0.35),
            (cx + sz * 0.13, cy - sz * 0.16),
            (cx + sz * 0.26, cy - sz * 0.30),
            (cx + sz * 0.18, crown_base_y),
            (cx - sz * 0.18, crown_base_y)
        ]
        pygame.draw.polygon(s, (0, 0, 0), [(x, y + 1) for x, y in points])
        pygame.draw.polygon(s, col, points)

        for px, py in [(cx - sz * 0.26, cy - sz * 0.30), (cx, cy - sz * 0.35), (cx + sz * 0.26, cy - sz * 0.30)]:
            pygame.draw.circle(s, (255, 255, 255), (int(px), int(py)), int(sz * 0.035))

        pygame.draw.circle(s, (255, 255, 255), (cx, int(cy + sz * 0.10)), int(sz * 0.05))

    @classmethod
    def _draw_general(cls, s, cx, cy, sz, col, dark):
        base_w = sz * 0.68
        base_h = sz * 0.10
        pygame.draw.rect(s, (0, 0, 0), (cx - base_w // 2 - 2, cy + sz * 0.30, base_w + 4, base_h + 4), border_radius=3)
        pygame.draw.rect(s, col, (cx - base_w // 2, cy + sz * 0.32, base_w, base_h), border_radius=3)
        pygame.draw.rect(s, col, (cx - sz * 0.24, cy + sz * 0.26, sz * 0.48, sz * 0.06), border_radius=2)

        body_pts = [
            (cx - sz * 0.22, cy - sz * 0.06),
            (cx + sz * 0.22, cy - sz * 0.06),
            (cx + sz * 0.28, cy + sz * 0.26),
            (cx - sz * 0.28, cy + sz * 0.26)
        ]
        pygame.draw.polygon(s, (0, 0, 0), [(x + (1 if x > cx else -1), y + 1) for x, y in body_pts])
        pygame.draw.polygon(s, col, body_pts)

        pygame.draw.circle(s, col, (int(cx - sz * 0.22), int(cy - sz * 0.04)), int(sz * 0.05))
        pygame.draw.circle(s, col, (int(cx + sz * 0.22), int(cy - sz * 0.04)), int(sz * 0.05))

        crown_pts = [
            (cx - sz * 0.22, cy - sz * 0.24),
            (cx - sz * 0.14, cy - sz * 0.14),
            (cx, cy - sz * 0.26),
            (cx + sz * 0.14, cy - sz * 0.14),
            (cx + sz * 0.22, cy - sz * 0.24),
            (cx + sz * 0.18, cy - sz * 0.06),
            (cx - sz * 0.18, cy - sz * 0.06)
        ]
        pygame.draw.polygon(s, (0, 0, 0), [(x, y + 1) for x, y in crown_pts])
        pygame.draw.polygon(s, col, crown_pts)

        cross_y = cy - sz * 0.32
        cw = sz * 0.05
        ch = sz * 0.12
        pygame.draw.rect(s, (255, 255, 255), (cx - cw // 2, cross_y - ch // 2, cw, ch))
        pygame.draw.rect(s, (255, 255, 255), (cx - ch // 2, cross_y - cw // 2, ch, cw))

        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            ex = cx + math.cos(rad) * sz * 0.08
            ey = (cy + sz * 0.10) + math.sin(rad) * sz * 0.08
            pygame.draw.line(s, (255, 255, 255), (cx, cy + sz * 0.10), (ex, ey), 1)
        pygame.draw.circle(s, (255, 255, 255), (cx, int(cy + sz * 0.10)), int(sz * 0.03))

    @classmethod
    def get_special_surface(cls, special_type, size=36):
        key = ("special", special_type, size)
        if key in cls._cache:
            return cls._cache[key]

        hi_size = size * 2
        surf = pygame.Surface((hi_size, hi_size), pygame.SRCALPHA)
        cx, cy = hi_size // 2, hi_size // 2

        if special_type == 'H':
            pygame.draw.circle(surf, (45, 10, 22, 220), (cx, cy), int(hi_size * 0.44))
            pygame.draw.circle(surf, (255, 60, 110), (cx, cy), int(hi_size * 0.44), 2)
            r = hi_size * 0.28
            pygame.draw.circle(surf, (255, 31, 75), (int(cx - r * 0.45), int(cy - r * 0.3)), int(r * 0.55))
            pygame.draw.circle(surf, (255, 31, 75), (int(cx + r * 0.45), int(cy - r * 0.3)), int(r * 0.55))
            pts = [
                (cx - r * 0.95, cy - r * 0.15),
                (cx + r * 0.95, cy - r * 0.15),
                (cx, cy + r * 0.85)
            ]
            pygame.draw.polygon(surf, (255, 31, 75), pts)
            pygame.draw.circle(surf, (255, 255, 255, 220), (int(cx - r * 0.45), int(cy - r * 0.45)), int(r * 0.16))

        elif special_type == 'I':
            pygame.draw.circle(surf, (40, 30, 5, 210), (cx, cy), int(hi_size * 0.44))
            pygame.draw.circle(surf, (255, 215, 0), (cx, cy), int(hi_size * 0.44), 2)
            bolt = [
                (cx + hi_size * 0.05, cy - hi_size * 0.38),
                (cx - hi_size * 0.28, cy + hi_size * 0.02),
                (cx - hi_size * 0.02, cy + hi_size * 0.02),
                (cx - hi_size * 0.10, cy + hi_size * 0.38),
                (cx + hi_size * 0.26, cy - hi_size * 0.04),
                (cx + hi_size * 0.02, cy - hi_size * 0.04)
            ]
            pygame.draw.polygon(surf, (255, 235, 50), bolt)
            pygame.draw.lines(surf, (255, 255, 255), False, bolt[:3], 2)

        elif special_type == 'X':
            pygame.draw.circle(surf, (22, 16, 12, 230), (cx, cy), int(hi_size * 0.44))
            pygame.draw.circle(surf, (255, 50, 50), (cx, cy), int(hi_size * 0.44), 2)
            bw = int(hi_size * 0.28)
            pygame.draw.line(surf, (230, 225, 215), (cx - bw, cy - bw), (cx + bw, cy + bw), 3)
            pygame.draw.line(surf, (230, 225, 215), (cx + bw, cy - bw), (cx - bw, cy + bw), 3)
            pygame.draw.circle(surf, (244, 239, 228), (cx, int(cy - hi_size * 0.06)), int(hi_size * 0.20))
            pygame.draw.rect(surf, (244, 239, 228), (cx - hi_size * 0.10, cy, int(hi_size * 0.20), int(hi_size * 0.14)), border_radius=2)
            pygame.draw.circle(surf, (24, 18, 14), (int(cx - hi_size * 0.08), int(cy - hi_size * 0.06)), int(hi_size * 0.05))
            pygame.draw.circle(surf, (24, 18, 14), (int(cx + hi_size * 0.08), int(cy - hi_size * 0.06)), int(hi_size * 0.05))

        elif special_type == 'T':
            pygame.draw.circle(surf, (10, 25, 45, 220), (cx, cy), int(hi_size * 0.44))
            pygame.draw.circle(surf, (56, 189, 248), (cx, cy), int(hi_size * 0.44), 2)
            pygame.draw.circle(surf, (96, 165, 250), (cx, cy), int(hi_size * 0.30), 2)
            pygame.draw.circle(surf, (192, 132, 252), (cx, cy), int(hi_size * 0.16), 2)
            pygame.draw.circle(surf, (255, 255, 255), (cx, cy), int(hi_size * 0.06))

        final_surf = pygame.transform.smoothscale(surf, (size, size))
        cls._cache[key] = final_surf
        return final_surf
