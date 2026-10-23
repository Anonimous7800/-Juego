import math
import random
import pygame
from src.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    COLOR_BG_DARK, COLOR_PANEL_BG, COLOR_PANEL_BORDER,
    COLOR_TEXT_LIGHT, COLOR_TEXT_GOLD, COLOR_TEXT_MUTED,
    FACTIONS, ORDER
)
from src.characters import CHARACTERS
from src.missions import MissionManager
from src.settings import SettingsManager
from src.audio import AudioManager
from src.piece_graphics import PieceGraphics
from src.asset_manager import AssetManager

class MenuManager:
    def __init__(self, screen):
        self.screen = screen
        self.assets = AssetManager()
        self.settings = SettingsManager()
        self.audio = AudioManager()
        self.missions = MissionManager()
        self.init_fonts()

        self.time = 0.0
        self.selected_character_id = 'S'
        self.mp_slots = {'S': 'human', 'A': 'human', 'J': 'ai', 'K': 'ai'}
        self.mp_preset = '1v1_duel'

        self.dragging_music = False
        self.dragging_sfx = False
        self.missions_scroll_y = 0.0
        self.max_missions_scroll = 260.0

        self.credits_scroll_y = 0.0
        self.credits_speed = 46.0
        self.credits_speed_mult = 1.0
        self.credits_paused = False
        self.credits_direction = 1
        self.credits_entrance_time = 0.0
        self.dragging_credits = False
        self.credits_surface = None
        self.credits_content_h = 1750
        self.credits_max_scroll = 1200.0
        self.credits_track_top = 0
        self.credits_track_h = 1
        self.credits_top_fade = None
        self.credits_bot_fade = None

        self.particles = [
            {
                'x': random.uniform(0, WINDOW_WIDTH),
                'y': random.uniform(0, WINDOW_HEIGHT),
                'speed': random.uniform(20, 50),
                'size': random.uniform(1.8, 3.8),
                'color': (255, 215, 80) if i % 2 == 0 else (195, 140, 255),
                'sway_freq': random.uniform(1.2, 2.5),
                'sway_amp': random.uniform(12, 28),
                'phase': random.uniform(0, 6.28)
            }
            for i in range(45)
        ]

    def reset_credits(self):
        self.credits_scroll_y = 0.0
        self.credits_paused = False
        self.credits_entrance_time = 0.0
        self.credits_direction = 1
        self.dragging_credits = False

    def toggle_credits_pause(self):
        self.credits_paused = not self.credits_paused

    def toggle_credits_speed(self):
        if self.credits_speed_mult == 1.0:
            self.credits_speed_mult = 1.75
        elif self.credits_speed_mult == 1.75:
            self.credits_speed_mult = 2.5
        else:
            self.credits_speed_mult = 1.0

    def toggle_credits_direction(self):
        self.credits_direction *= -1

    def scroll_credits(self, delta):
        if self.credits_max_scroll > 0:
            self.credits_scroll_y = max(0.0, min(self.credits_max_scroll, self.credits_scroll_y - delta))

    def update_credits_scroll_from_mouse(self, mouse_y):
        if self.credits_track_h <= 0 or self.credits_max_scroll <= 0:
            return
        pct = max(0.0, min(1.0, (mouse_y - self.credits_track_top) / float(self.credits_track_h)))
        self.credits_scroll_y = pct * self.credits_max_scroll

    def update_credits(self, dt):
        self.credits_entrance_time = min(1.0, self.credits_entrance_time + dt)
        if not self.credits_paused and self.credits_max_scroll > 0:
            self.credits_scroll_y += self.credits_speed * self.credits_speed_mult * self.credits_direction * dt
            if self.credits_scroll_y > self.credits_max_scroll:
                self.credits_scroll_y = self.credits_max_scroll
            elif self.credits_scroll_y < 0.0:
                self.credits_scroll_y = 0.0

    def scroll_missions(self, delta):
        self.missions_scroll_y = max(0.0, min(self.max_missions_scroll, self.missions_scroll_y - delta))

    def set_mp_preset(self, preset_id):
        self.mp_preset = preset_id
        if preset_id == '1v1_team':
            self.mp_slots = {'S': 'human', 'A': 'human', 'J': 'human', 'K': 'human'}
        elif preset_id == 'coop_2v2':
            self.mp_slots = {'S': 'human', 'A': 'ai', 'J': 'human', 'K': 'ai'}
        elif preset_id == '1v1_duel':
            self.mp_slots = {'S': 'human', 'A': 'human', 'J': 'ai', 'K': 'ai'}
        elif preset_id == '4p':
            self.mp_slots = {'S': 'human', 'A': 'human', 'J': 'human', 'K': 'human'}

    def toggle_mp_slot(self, cid):
        current = self.mp_slots.get(cid, 'human')
        self.mp_slots[cid] = 'ai' if current == 'human' else 'human'
        self.mp_preset = 'custom'

    def draw_vector_star(self, surface, x, y, size=16, color=(255, 215, 0)):
        cx = x + size // 2
        cy = y + size // 2
        pts = [
            (cx, y), (cx + 3, cy - 3), (x + size, cy), (cx + 3, cy + 3),
            (cx, y + size), (cx - 3, cy + 3), (x, cy), (cx - 3, cy - 3)
        ]
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 1)

    def init_fonts(self):
        pygame.font.init()
        self.font_title_big = pygame.font.SysFont("segoeui,consolas,arial", 44, bold=True)
        self.font_title = pygame.font.SysFont("segoeui,consolas,arial", 30, bold=True)
        self.font_header = pygame.font.SysFont("segoeui,consolas,arial", 22, bold=True)
        self.font_body = pygame.font.SysFont("segoeui,consolas,arial", 16)
        self.font_bold = pygame.font.SysFont("segoeui,consolas,arial", 16, bold=True)
        self.font_small = pygame.font.SysFont("segoeui,consolas,arial", 13)
        self.font_badge = pygame.font.SysFont("segoeui,consolas,arial", 12, bold=True)

    def update(self, dt):
        self.time += dt
        self.update_credits(dt)
        for p in self.particles:
            p['y'] -= p['speed'] * dt
            p['x'] += math.sin(self.time * p['sway_freq'] + p['phase']) * (p['sway_amp'] * dt)
            if p['y'] < -10:
                p['y'] = WINDOW_HEIGHT + 10
                p['x'] = random.uniform(0, WINDOW_WIDTH)

    def draw_ambient_bg(self):
        bg = self.assets.get_menu_background()
        if bg:
            self.screen.blit(bg, (0, 0))
        else:
            self.screen.fill(COLOR_BG_DARK)

        sol_pulse = 16 * math.sin(self.time * 2.2)
        sol_surf = pygame.Surface((280, 280), pygame.SRCALPHA)
        pygame.draw.circle(sol_surf, (255, 215, 60, 22), (140, 140), int(115 + sol_pulse))
        pygame.draw.circle(sol_surf, (255, 175, 20, 36), (140, 140), int(75 + sol_pulse * 0.5))
        self.screen.blit(sol_surf, (WINDOW_WIDTH // 2 - 200, 20))

        ame_pulse = 16 * math.cos(self.time * 2.2)
        ame_surf = pygame.Surface((280, 280), pygame.SRCALPHA)
        pygame.draw.circle(ame_surf, (190, 120, 255, 22), (140, 140), int(115 + ame_pulse))
        pygame.draw.circle(ame_surf, (140, 80, 230, 36), (140, 140), int(75 + ame_pulse * 0.5))
        self.screen.blit(ame_surf, (WINDOW_WIDTH // 2 - 80, 20))

        for p in self.particles:
            alpha = int(140 + 80 * math.sin(self.time * 3.0 + p['phase']))
            p_surf = pygame.Surface((int(p['size'] * 2 + 2), int(p['size'] * 2 + 2)), pygame.SRCALPHA)
            pygame.draw.circle(p_surf, (*p['color'], alpha), (int(p['size'] + 1), int(p['size'] + 1)), int(p['size']))
            self.screen.blit(p_surf, (int(p['x']), int(p['y'])))

    def draw_button(self, rect, text, mouse_pos, primary=False, color_override=None, icon_name=None):
        hover = rect.collidepoint(mouse_pos)

        icon_surf = None
        if icon_name:
            icon_surf = self.assets.get_icon(icon_name, size=(28, 28))

        btn_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        if primary:
            if hover:
                top_col = (255, 215, 45, 245)
                bot_col = (210, 160, 15, 245)
                border_col = (255, 245, 180)
                txt_col = (12, 10, 5)
            else:
                top_col = (225, 180, 30, 230)
                bot_col = (175, 130, 10, 230)
                border_col = (255, 215, 60)
                txt_col = (15, 12, 6)
        elif color_override:
            if hover:
                top_col = (color_override[0], color_override[1], color_override[2], 225)
                bot_col = (color_override[0]//2, color_override[1]//2, color_override[2]//2, 225)
                border_col = (255, 255, 255)
                txt_col = (255, 255, 255)
            else:
                top_col = (color_override[0]//2, color_override[1]//2, color_override[2]//2, 185)
                bot_col = (color_override[0]//3, color_override[1]//3, color_override[2]//3, 185)
                border_col = color_override
                txt_col = color_override
        else:
            if hover:
                top_col = (54, 44, 64, 235)
                bot_col = (30, 24, 38, 235)
                border_col = (255, 215, 90)
                txt_col = (255, 235, 140)
            else:
                top_col = (36, 28, 44, 210)
                bot_col = (20, 16, 26, 210)
                border_col = (140, 115, 85)
                txt_col = (230, 225, 215)

        for y in range(rect.height):
            interp = y / max(1, rect.height - 1)
            r = int(top_col[0] * (1 - interp) + bot_col[0] * interp)
            g = int(top_col[1] * (1 - interp) + bot_col[1] * interp)
            b = int(top_col[2] * (1 - interp) + bot_col[2] * interp)
            a = int(top_col[3] * (1 - interp) + bot_col[3] * interp)
            pygame.draw.line(btn_surf, (r, g, b, a), (3, y), (rect.width - 4, y))

        if hover:
            glow_surf = pygame.Surface((rect.width + 10, rect.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (255, 215, 60, 45), (0, 0, rect.width + 10, rect.height + 10), border_radius=10)
            self.screen.blit(glow_surf, (rect.x - 5, rect.y - 5))

        self.screen.blit(btn_surf, (rect.x, rect.y))

        pygame.draw.rect(self.screen, border_col, rect, 2 if hover else 1, border_radius=8)

        c_len = 6
        c_col = (255, 235, 120) if hover else (180, 150, 90)
        pygame.draw.line(self.screen, c_col, (rect.left + 2, rect.top + 2), (rect.left + 2 + c_len, rect.top + 2), 2)
        pygame.draw.line(self.screen, c_col, (rect.left + 2, rect.top + 2), (rect.left + 2, rect.top + 2 + c_len), 2)
        pygame.draw.line(self.screen, c_col, (rect.right - 3, rect.top + 2), (rect.right - 3 - c_len, rect.top + 2), 2)
        pygame.draw.line(self.screen, c_col, (rect.right - 3, rect.top + 2), (rect.right - 3, rect.top + 2 + c_len), 2)
        pygame.draw.line(self.screen, c_col, (rect.left + 2, rect.bottom - 3), (rect.left + 2 + c_len, rect.bottom - 3), 2)
        pygame.draw.line(self.screen, c_col, (rect.left + 2, rect.bottom - 3), (rect.left + 2, rect.bottom - 3 - c_len), 2)
        pygame.draw.line(self.screen, c_col, (rect.right - 3, rect.bottom - 3), (rect.right - 3 - c_len, rect.bottom - 3), 2)
        pygame.draw.line(self.screen, c_col, (rect.right - 3, rect.bottom - 3), (rect.right - 3, rect.bottom - 3 - c_len), 2)

        lbl = self.font_bold.render(text, True, txt_col)
        lbl_shadow = self.font_bold.render(text, True, (0, 0, 0))

        if icon_surf:
            total_content_w = icon_surf.get_width() + 12 + lbl.get_width()
            start_x = rect.centerx - total_content_w // 2
            icon_y = rect.centery - icon_surf.get_height() // 2
            lbl_y = rect.centery - lbl.get_height() // 2
            self.screen.blit(icon_surf, (start_x, icon_y))
            self.screen.blit(lbl_shadow, (start_x + icon_surf.get_width() + 13, lbl_y + 1))
            self.screen.blit(lbl, (start_x + icon_surf.get_width() + 12, lbl_y))
        else:
            self.screen.blit(lbl_shadow, (rect.centerx - lbl.get_width() // 2 + 1, rect.centery - lbl.get_height() // 2 + 1))
            self.screen.blit(lbl, (rect.centerx - lbl.get_width() // 2, rect.centery - lbl.get_height() // 2))

        return hover

    def draw_menu_duel_showcase(self, rect, mouse_pos):
        hover = rect.collidepoint(mouse_pos)
        surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        bg_col = (16, 12, 26, 215) if not hover else (24, 18, 36, 230)
        border_col = (168, 85, 247) if hover else (180, 140, 80)
        pygame.draw.rect(surf, bg_col, (0, 0, rect.width, rect.height), border_radius=12)
        pygame.draw.rect(surf, border_col, (0, 0, rect.width, rect.height), 2 if hover else 1, border_radius=12)
        pygame.draw.rect(surf, (255, 215, 60), (0, 0, rect.width, 4), border_top_left_radius=12, border_top_right_radius=12)
        self.screen.blit(surf, (rect.x, rect.y))

        t_lbl = self.font_bold.render("CHOQUE DE FACCIONES", True, COLOR_TEXT_GOLD)
        tx = rect.centerx - t_lbl.get_width() // 2
        self.screen.blit(t_lbl, (tx, rect.y + 14))
        self.draw_vector_star(self.screen, tx - 20, rect.y + 14, size=14, color=COLOR_TEXT_GOLD)
        self.draw_vector_star(self.screen, tx + t_lbl.get_width() + 6, rect.y + 14, size=14, color=COLOR_TEXT_GOLD)

        sub_lbl = self.font_small.render("Duelo Sagrado de Generales", True, (200, 190, 215))
        self.screen.blit(sub_lbl, (rect.centerx - sub_lbl.get_width() // 2, rect.y + 36))

        arena_y = rect.y + 145
        ped_rect = pygame.Rect(rect.centerx - 105, arena_y + 22, 210, 36)
        ped_surf = pygame.Surface((ped_rect.width, ped_rect.height), pygame.SRCALPHA)
        pygame.draw.ellipse(ped_surf, (28, 20, 42, 190), (0, 0, ped_rect.width, ped_rect.height))
        pygame.draw.ellipse(ped_surf, (168, 85, 247, 150), (0, 0, ped_rect.width, ped_rect.height), 2)
        self.screen.blit(ped_surf, (ped_rect.x, ped_rect.y))

        bob1 = math.sin(self.time * 3.5) * 5.0
        bob2 = math.cos(self.time * 3.5) * 5.0

        p1_x = rect.centerx - 72
        p1_y = arena_y - 25 + int(bob1)
        p2_x = rect.centerx + 18
        p2_y = arena_y - 25 + int(bob2)

        p1_surf = PieceGraphics.get_piece_surface('S', 'K', size=56)
        p2_surf = PieceGraphics.get_piece_surface('A', 'K', size=56)

        g1_surf = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.circle(g1_surf, (255, 215, 0, 70), (32, 32), 28)
        self.screen.blit(g1_surf, (p1_x - 4, p1_y - 4))
        self.screen.blit(p1_surf, (p1_x, p1_y))

        g2_surf = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.circle(g2_surf, (177, 156, 217, 70), (32, 32), 28)
        self.screen.blit(g2_surf, (p2_x - 4, p2_y - 4))
        self.screen.blit(p2_surf, (p2_x, p2_y))

        p1_hp_w = 40
        pygame.draw.rect(self.screen, (30, 20, 20), (p1_x + 8, p1_y - 12, p1_hp_w, 5), border_radius=2)
        pygame.draw.rect(self.screen, (78, 205, 145), (p1_x + 8, p1_y - 12, int(p1_hp_w * 0.85), 5), border_radius=2)

        p2_hp_w = 40
        pygame.draw.rect(self.screen, (30, 20, 20), (p2_x + 8, p2_y - 12, p2_hp_w, 5), border_radius=2)
        pygame.draw.rect(self.screen, (255, 78, 105), (p2_x + 8, p2_y - 12, int(p2_hp_w * 0.65), 5), border_radius=2)

        clash_x = rect.centerx
        clash_y = arena_y + 4
        pulse_r = int(14 + 6 * math.sin(self.time * 6.0))
        clash_surf = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(clash_surf, (255, 240, 150, 130), (25, 25), pulse_r)
        self.screen.blit(clash_surf, (clash_x - 25, clash_y - 25))

        vs_lbl = self.font_header.render("VS", True, (255, 235, 120))
        self.screen.blit(vs_lbl, (clash_x - vs_lbl.get_width() // 2, clash_y - vs_lbl.get_height() // 2))

        spark_angles = [0.0, 1.2, 2.4, 3.6, 4.8]
        for sa in spark_angles:
            dist = 16 + 10 * math.sin(self.time * 7.0 + sa)
            sx = clash_x + int(math.cos(sa + self.time * 2.0) * dist)
            sy = clash_y + int(math.sin(sa + self.time * 2.0) * dist)
            pygame.draw.circle(self.screen, (255, 230, 90), (sx, sy), 2)

        f1_lbl = self.font_small.render("Solcardena", True, (255, 215, 0))
        f2_lbl = self.font_small.render("Aurelium", True, (177, 156, 217))
        self.screen.blit(f1_lbl, (rect.centerx - 72, arena_y + 54))
        self.screen.blit(f2_lbl, (rect.centerx + 22, arena_y + 54))

        info_box = pygame.Rect(rect.x + 14, rect.bottom - 86, rect.width - 28, 70)
        pygame.draw.rect(self.screen, (10, 8, 16, 220), info_box, border_radius=8)
        pygame.draw.rect(self.screen, (60, 48, 75), info_box, 1, border_radius=8)

        b1_txt = self.font_small.render("Tablero Táctico 16×16", True, (255, 215, 80))
        b2_txt = self.font_small.render("Combate, Cartas & Trincheras", True, (220, 215, 235))
        b3_txt = self.font_badge.render("¡Captura la bandera y vence!", True, (140, 210, 255))
        self.screen.blit(b1_txt, (info_box.centerx - b1_txt.get_width() // 2, info_box.y + 8))
        self.screen.blit(b2_txt, (info_box.centerx - b2_txt.get_width() // 2, info_box.y + 28))
        self.screen.blit(b3_txt, (info_box.centerx - b3_txt.get_width() // 2, info_box.y + 48))

    def draw_main_menu(self, mouse_pos):
        self.draw_ambient_bg()

        l1_txt = self.font_title_big.render("CHRONICLES OF", True, (255, 225, 120))
        l1_glow = self.font_title_big.render("CHRONICLES OF", True, (168, 85, 247))
        l1_shadow = self.font_title_big.render("CHRONICLES OF", True, (0, 0, 0))

        l2_txt = self.font_title_big.render("TWO SUNS", True, (255, 215, 60))
        l2_glow = self.font_title_big.render("TWO SUNS", True, (236, 72, 153))
        l2_shadow = self.font_title_big.render("TWO SUNS", True, (0, 0, 0))

        t1_x = WINDOW_WIDTH // 2 - l1_txt.get_width() // 2
        t1_y = 20
        self.screen.blit(l1_shadow, (t1_x + 3, t1_y + 3))
        self.screen.blit(l1_glow, (t1_x + 1, t1_y + 1))
        self.screen.blit(l1_txt, (t1_x, t1_y))

        t2_x = WINDOW_WIDTH // 2 - l2_txt.get_width() // 2
        t2_y = 66
        self.screen.blit(l2_shadow, (t2_x + 3, t2_y + 3))
        self.screen.blit(l2_glow, (t2_x + 1, t2_y + 1))
        self.screen.blit(l2_txt, (t2_x, t2_y))

        self.draw_vector_star(self.screen, t1_x - 34, t1_y + 10, size=22, color=(255, 215, 60))
        self.draw_vector_star(self.screen, t1_x + l1_txt.get_width() + 12, t1_y + 10, size=22, color=(168, 85, 247))
        self.draw_vector_star(self.screen, t2_x - 30, t2_y + 10, size=18, color=(236, 72, 153))
        self.draw_vector_star(self.screen, t2_x + l2_txt.get_width() + 12, t2_y + 10, size=18, color=(255, 215, 60))

        btn_w, btn_h = 410, 48
        bx = WINDOW_WIDTH // 2 - btn_w // 2
        start_y = 175
        gap = 58

        plate_w, plate_h = 450, 196
        plate_x = WINDOW_WIDTH // 2 - plate_w // 2
        plate_y = start_y - 12
        plate_surf = pygame.Surface((plate_w, plate_h), pygame.SRCALPHA)
        pygame.draw.rect(plate_surf, (12, 9, 20, 195), (0, 0, plate_w, plate_h), border_radius=12)
        pygame.draw.rect(plate_surf, (190, 150, 80, 110), (0, 0, plate_w, plate_h), 1, border_radius=12)
        self.screen.blit(plate_surf, (plate_x, plate_y))

        buttons = {
            'play': pygame.Rect(bx, start_y, btn_w, btn_h),
            'tutorial': pygame.Rect(bx, start_y + gap, btn_w, btn_h),
            'multiplayer': pygame.Rect(bx, start_y + gap * 2, btn_w, btn_h),
            'characters': pygame.Rect(bx, start_y + gap * 2, btn_w, btn_h),
            'settings': pygame.Rect(32, 28, 175, 42),
            'rules': pygame.Rect(WINDOW_WIDTH - 207, 28, 175, 42),
            'quit': pygame.Rect(32, WINDOW_HEIGHT - 62, 175, 42),
            'credits': pygame.Rect(WINDOW_WIDTH - 207, WINDOW_HEIGHT - 62, 175, 42)
        }

        self.draw_button(buttons['play'], "JUGAR PARTIDA BÉLICA", mouse_pos, primary=True, icon_name="btn_play")
        self.draw_button(buttons['tutorial'], "TUTORIAL", mouse_pos, icon_name="btn_tutorial")
        self.draw_button(buttons['multiplayer'], "MODO MULTIJUGADOR LOCAL", mouse_pos, icon_name="btn_characters")
        self.draw_button(buttons['settings'], "AJUSTES", mouse_pos, icon_name="btn_settings")
        self.draw_button(buttons['rules'], "REGLAS", mouse_pos, icon_name="btn_rules")
        self.draw_button(buttons['quit'], "SALIR", mouse_pos, icon_name="btn_quit")
        self.draw_button(buttons['credits'], "CRÉDITOS", mouse_pos, icon_name="btn_oracle")

        showcase_rect = pygame.Rect(WINDOW_WIDTH - 290, 163, 260, 335)
        self.draw_menu_duel_showcase(showcase_rect, mouse_pos)

        factions_info = [
            ("Solcardena", (255, 215, 0)),
            ("Royaume D'Aurelium", (177, 156, 217)),
            ("Imperio de Varkhental", (255, 80, 80)),
            ("Imperio Sthalgard", (78, 205, 145))
        ]
        left_pill_x = 32
        pill_w = 175
        pill_h = 24
        pill_gap = 28
        for fi, (fname, fcol) in enumerate(factions_info):
            py = 78 + fi * pill_gap
            pill_rect = pygame.Rect(left_pill_x, py, pill_w, pill_h)
            pill_surf = pygame.Surface((pill_rect.width, pill_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(pill_surf, (18, 14, 26, 190), (0, 0, pill_rect.width, pill_rect.height), border_radius=11)
            pygame.draw.rect(pill_surf, (*fcol, 140), (0, 0, pill_rect.width, pill_rect.height), 1, border_radius=11)
            pygame.draw.circle(pill_surf, fcol, (10, pill_rect.height // 2), 4)
            self.screen.blit(pill_surf, (pill_rect.x, pill_rect.y))
            tag_surf = self.font_small.render(fname, True, fcol)
            self.screen.blit(tag_surf, (pill_rect.x + 20, pill_rect.centery - tag_surf.get_height() // 2))

        badge_w = 580
        badge_y = WINDOW_HEIGHT - 55
        badge_rect = pygame.Rect(WINDOW_WIDTH // 2 - badge_w // 2, badge_y, badge_w, 28)
        badge_surf = pygame.Surface((badge_w, 28), pygame.SRCALPHA)
        pygame.draw.rect(badge_surf, (15, 12, 24, 180), (0, 0, badge_w, 28), border_radius=14)
        pygame.draw.rect(badge_surf, (168, 85, 247, 120), (0, 0, badge_w, 28), 1, border_radius=14)
        self.screen.blit(badge_surf, (badge_rect.x, badge_rect.y))

        ai_dot_alpha = int(180 + 75 * math.sin(self.time * 4.0))
        dot_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(dot_surf, (56, 189, 248, ai_dot_alpha), (5, 5), 4)
        self.screen.blit(dot_surf, (badge_rect.x + 18, badge_rect.y + 9))

        sub_txt = self.font_small.render("4 NACIONES EN CONFLICTO   ·   TRINCHERAS 16×16   ·   CAMPO DE BATALLA SAGRADO", True, (220, 215, 240))
        self.screen.blit(sub_txt, (badge_rect.x + 36, badge_rect.y + 6))

        ft_txt = self.font_small.render("Chronicles Of Two Suns · Pygame Edition · 60 FPS", True, (140, 130, 155))
        self.screen.blit(ft_txt, (WINDOW_WIDTH // 2 - ft_txt.get_width() // 2, WINDOW_HEIGHT - 22))

        return buttons

    def draw_character_select(self, mouse_pos):
        self.draw_ambient_bg()

        hdr = self.font_title.render("ELIGE TU COMANDANTE DE GUERRA", True, COLOR_TEXT_GOLD)
        self.screen.blit(hdr, (WINDOW_WIDTH // 2 - hdr.get_width() // 2, 35))

        sub = self.font_body.render("Cada comandante otorga rasgos tácticos únicos a su ejército en batalla", True, COLOR_TEXT_MUTED)
        self.screen.blit(sub, (WINDOW_WIDTH // 2 - sub.get_width() // 2, 75))

        card_w, card_h = 270, 440
        start_x = (WINDOW_WIDTH - (card_w * 4 + 20 * 3)) // 2
        y = 120

        char_buttons = {}
        for i, cid in enumerate(['S', 'A', 'J', 'K']):
            cdata = CHARACTERS[cid]
            cx = start_x + i * (card_w + 20)
            c_rect = pygame.Rect(cx, y, card_w, card_h)
            char_buttons[cid] = c_rect

            is_selected = self.selected_character_id == cid
            hover = c_rect.collidepoint(mouse_pos)

            bg = (35, 30, 22) if is_selected else ((25, 22, 17) if hover else (18, 16, 13))
            border_col = cdata['color'] if is_selected else ((180, 160, 120) if hover else (50, 42, 30))

            pygame.draw.rect(self.screen, bg, c_rect, border_radius=10)
            pygame.draw.rect(self.screen, border_col, c_rect, 3 if is_selected else 1, border_radius=10)
            pygame.draw.rect(self.screen, cdata['color'], (cx, y, card_w, 5), border_top_left_radius=10, border_top_right_radius=10)

            pygame.draw.circle(self.screen, cdata['bg'], (cx + card_w // 2, y + 62), 40)
            pygame.draw.circle(self.screen, cdata['color'], (cx + card_w // 2, y + 62), 40, 2)
            gen_surf = PieceGraphics.get_piece_surface(cid, 'K', size=52)
            self.screen.blit(gen_surf, (cx + card_w // 2 - 26, y + 62 - 26))

            n_txt = self.font_header.render(cdata['name'].split(',')[0], True, cdata['color'])
            self.screen.blit(n_txt, (cx + card_w // 2 - n_txt.get_width() // 2, y + 115))

            f_txt = self.font_small.render(f"Facción: {cdata['faction']}", True, COLOR_TEXT_LIGHT)
            self.screen.blit(f_txt, (cx + card_w // 2 - f_txt.get_width() // 2, y + 142))

            t_txt = self.font_small.render(f"Equipo {cdata['team']}", True, (200, 180, 120))
            self.screen.blit(t_txt, (cx + card_w // 2 - t_txt.get_width() // 2, y + 162))

            t_box = pygame.Rect(cx + 12, y + 195, card_w - 24, 110)
            pygame.draw.rect(self.screen, (10, 8, 6), t_box, border_radius=6)
            pygame.draw.rect(self.screen, (45, 38, 28), t_box, 1, border_radius=6)

            tr_title = self.font_bold.render(f"✨ {cdata['trait_name']}", True, cdata['color'])
            self.screen.blit(tr_title, (cx + 18, y + 202))

            words = cdata['trait_desc'].split()
            lines = []
            cur_line = []
            for w in words:
                cur_line.append(w)
                if len(" ".join(cur_line)) > 26:
                    lines.append(" ".join(cur_line[:-1]))
                    cur_line = [w]
            if cur_line: lines.append(" ".join(cur_line))

            for li, line_str in enumerate(lines[:3]):
                lt = self.font_small.render(line_str, True, (200, 195, 185))
                self.screen.blit(lt, (cx + 18, y + 230 + li * 20))

            lore_snippet = cdata['lore'][:65] + "..."
            lore_txt = self.font_small.render(lore_snippet, True, (130, 120, 110))
            self.screen.blit(lore_txt, (cx + 12, y + 325))

            status = "SELECCIONADO" if is_selected else "CLIC PARA ELEGIR"
            s_col = cdata['color'] if is_selected else (140, 130, 120)
            tag_txt = self.font_bold.render(status, True, s_col)
            self.screen.blit(tag_txt, (cx + card_w // 2 - tag_txt.get_width() // 2, y + 395))

        btn_start = pygame.Rect(WINDOW_WIDTH // 2 - 180, WINDOW_HEIGHT - 110, 360, 48)
        btn_back = pygame.Rect(WINDOW_WIDTH // 2 - 180, WINDOW_HEIGHT - 55, 360, 38)

        self.draw_button(btn_start, "COMANDAR ESTA FACCIÓN", mouse_pos, primary=True, icon_name="btn_play")
        self.draw_button(btn_back, "VOLVER AL MENÚ", mouse_pos, icon_name="btn_back")

        return {
            'chars': char_buttons,
            'start': btn_start,
            'back': btn_back
        }

    def draw_multiplayer_menu(self, mouse_pos):
        self.draw_ambient_bg()

        hdr = self.font_title.render("MODO MULTIJUGADOR LOCAL (PASO Y JUEGA)", True, COLOR_TEXT_GOLD)
        self.screen.blit(hdr, (WINDOW_WIDTH // 2 - hdr.get_width() // 2, 22))

        sub = self.font_body.render("Comanda facciones con amigos en la misma pantalla · Asigna cada ejército a un Jugador o a la IA", True, COLOR_TEXT_MUTED)
        self.screen.blit(sub, (WINDOW_WIDTH // 2 - sub.get_width() // 2, 60))

        presets_info = [
            ('1v1_duel', "⚡ 1 vs 1 (Duelo Solar)"),
            ('coop_2v2', "🛡 2 vs 2 (Coop vs IA)"),
            ('1v1_team', "⚔ 1 vs 1 (Guerra Total)"),
            ('4p', "👑 4 Jugadores Humanos")
        ]

        preset_btns = {}
        total_p_w = 1120
        start_p_x = (WINDOW_WIDTH - total_p_w) // 2
        p_gap = 14
        p_btn_w = (total_p_w - p_gap * 3) // 4
        p_btn_h = 36
        p_y = 92

        for i, (pid, plabel) in enumerate(presets_info):
            px = start_p_x + i * (p_btn_w + p_gap)
            p_rect = pygame.Rect(px, p_y, p_btn_w, p_btn_h)
            preset_btns[pid] = p_rect

            is_active = self.mp_preset == pid
            hover = p_rect.collidepoint(mouse_pos)

            if is_active:
                bg = (60, 48, 20)
                border = COLOR_TEXT_GOLD
                txt_col = COLOR_TEXT_GOLD
            elif hover:
                bg = (35, 30, 24)
                border = (200, 180, 130)
                txt_col = (255, 240, 200)
            else:
                bg = (20, 18, 16)
                border = (65, 55, 45)
                txt_col = (180, 170, 160)

            pygame.draw.rect(self.screen, bg, p_rect, border_radius=6)
            pygame.draw.rect(self.screen, border, p_rect, 2 if is_active else 1, border_radius=6)

            lbl = self.font_bold.render(plabel, True, txt_col)
            self.screen.blit(lbl, (p_rect.centerx - lbl.get_width() // 2, p_rect.centery - lbl.get_height() // 2))

        card_w, card_h = 270, 360
        start_x = (WINDOW_WIDTH - (card_w * 4 + 20 * 3)) // 2
        cards_y = 140

        slot_buttons = {}
        for i, cid in enumerate(['S', 'A', 'J', 'K']):
            cdata = CHARACTERS[cid]
            cx = start_x + i * (card_w + 20)
            c_rect = pygame.Rect(cx, cards_y, card_w, card_h)
            slot_buttons[cid] = c_rect

            mode = self.mp_slots.get(cid, 'human')
            is_human = mode == 'human'
            hover = c_rect.collidepoint(mouse_pos)

            if is_human:
                bg = (32, 28, 20) if not hover else (40, 35, 25)
                border_col = cdata['color'] if hover else (210, 180, 110)
            else:
                bg = (18, 18, 22) if not hover else (24, 24, 30)
                border_col = (70, 80, 100) if hover else (45, 50, 65)

            pygame.draw.rect(self.screen, bg, c_rect, border_radius=10)
            pygame.draw.rect(self.screen, border_col, c_rect, 2 if hover else 1, border_radius=10)
            pygame.draw.rect(self.screen, cdata['color'], (cx, cards_y, card_w, 5), border_top_left_radius=10, border_top_right_radius=10)

            pygame.draw.circle(self.screen, cdata['bg'], (cx + card_w // 2, cards_y + 55), 36)
            pygame.draw.circle(self.screen, cdata['color'], (cx + card_w // 2, cards_y + 55), 36, 2)
            gen_surf = PieceGraphics.get_piece_surface(cid, 'K', size=46)
            self.screen.blit(gen_surf, (cx + card_w // 2 - 23, cards_y + 55 - 23))

            n_txt = self.font_header.render(cdata['name'].split(',')[0], True, cdata['color'])
            self.screen.blit(n_txt, (cx + card_w // 2 - n_txt.get_width() // 2, cards_y + 104))

            f_txt = self.font_small.render(f"{cdata['faction']}", True, COLOR_TEXT_LIGHT)
            self.screen.blit(f_txt, (cx + card_w // 2 - f_txt.get_width() // 2, cards_y + 128))

            t_txt = self.font_small.render(f"Equipo: {cdata['team']}", True, (200, 180, 120))
            self.screen.blit(t_txt, (cx + card_w // 2 - t_txt.get_width() // 2, cards_y + 148))

            toggle_box = pygame.Rect(cx + 16, cards_y + 185, card_w - 32, 90)
            if is_human:
                t_bg = (24, 50, 32)
                t_border = (78, 205, 145)
                m_title = "👤 JUGADOR HUMANO"
                m_color = (120, 255, 180)
                m_sub = "Control manual de tropas"
                m_sub2 = "Toma turnos y usa cartas"
            else:
                t_bg = (20, 24, 38)
                t_border = (90, 120, 170)
                m_title = "🤖 INTELIGENCIA ARTIFICIAL"
                m_color = (130, 180, 255)
                m_sub = "Controlado por la máquina"
                m_sub2 = "Tácticas automáticas de IA"

            pygame.draw.rect(self.screen, t_bg, toggle_box, border_radius=8)
            pygame.draw.rect(self.screen, t_border, toggle_box, 2, border_radius=8)

            mt_surf = self.font_bold.render(m_title, True, m_color)
            self.screen.blit(mt_surf, (toggle_box.centerx - mt_surf.get_width() // 2, toggle_box.y + 12))

            ms_surf = self.font_small.render(m_sub, True, (210, 210, 210))
            self.screen.blit(ms_surf, (toggle_box.centerx - ms_surf.get_width() // 2, toggle_box.y + 40))

            ms2_surf = self.font_small.render(m_sub2, True, (160, 160, 170))
            self.screen.blit(ms2_surf, (toggle_box.centerx - ms2_surf.get_width() // 2, toggle_box.y + 60))

            prompt_box = pygame.Rect(cx + 20, cards_y + 300, card_w - 40, 34)
            p_bg = (50, 42, 25) if hover else (25, 22, 18)
            pygame.draw.rect(self.screen, p_bg, prompt_box, border_radius=6)
            pygame.draw.rect(self.screen, (120, 100, 70), prompt_box, 1, border_radius=6)
            prompt_txt = self.font_badge.render("CLIC PARA ALTERNAR ROL ⟲", True, (240, 220, 160))
            self.screen.blit(prompt_txt, (prompt_box.centerx - prompt_txt.get_width() // 2, prompt_box.centery - prompt_txt.get_height() // 2))

        human_cnt = sum(1 for m in self.mp_slots.values() if m == 'human')
        ai_cnt = 4 - human_cnt
        summary_str = f"CONFIGURACIÓN: {human_cnt} Facciones Humanas · {ai_cnt} Facciones IA"
        sum_txt = self.font_header.render(summary_str, True, COLOR_TEXT_GOLD)
        self.screen.blit(sum_txt, (WINDOW_WIDTH // 2 - sum_txt.get_width() // 2, 518))

        btn_start = pygame.Rect(WINDOW_WIDTH // 2 - 200, 560, 400, 48)
        btn_back = pygame.Rect(WINDOW_WIDTH // 2 - 200, 620, 400, 38)

        self.draw_button(btn_start, "COMENZAR PARTIDA MULTIJUGADOR", mouse_pos, primary=True, icon_name="btn_play")
        self.draw_button(btn_back, "VOLVER AL MENÚ", mouse_pos, icon_name="btn_back")

        return {
            'presets': preset_btns,
            'slots': slot_buttons,
            'start': btn_start,
            'back': btn_back
        }

    def draw_missions(self, mouse_pos):
        self.draw_ambient_bg()

        hdr = self.font_title.render("MISIONES Y REGISTRO DE HAZAÑAS", True, COLOR_TEXT_GOLD)
        self.screen.blit(hdr, (WINDOW_WIDTH // 2 - hdr.get_width() // 2, 35))

        completed_cnt = self.missions.get_completed_count()
        all_missions = self.missions.get_all()
        total_cnt = len(all_missions)
        sub = self.font_body.render(f"Progreso Total: {completed_cnt} de {total_cnt} Misiones · Desplaza con Rueda del Ratón o Botones ▲ ▼", True, COLOR_TEXT_MUTED)
        self.screen.blit(sub, (WINDOW_WIDTH // 2 - sub.get_width() // 2, 75))

        view_x = 75
        view_y = 115
        view_w = 1080
        view_h = 490

        card_w = 515
        card_h = 125
        rows = (len(all_missions) + 1) // 2
        content_h = rows * (card_h + 16)
        self.max_missions_scroll = max(0.0, float(content_h - view_h + 20))

        self.screen.set_clip(pygame.Rect(view_x - 10, view_y, view_w + 20, view_h))

        for i, m in enumerate(all_missions):
            col = i % 2
            row = i // 2
            mx = view_x + col * (card_w + 25)
            my = view_y + row * (card_h + 16) - int(self.missions_scroll_y)

            m_rect = pygame.Rect(mx, my, card_w, card_h)
            bg = (22, 32, 20) if m['completed'] else (18, 14, 24)
            b_col = (78, 205, 145) if m['completed'] else (75, 60, 85)

            pygame.draw.rect(self.screen, bg, m_rect, border_radius=8)
            pygame.draw.rect(self.screen, b_col, m_rect, 1, border_radius=8)

            m_icon_key = m.get('icon', 'btn_missions')
            mic_surf = self.assets.get_icon(m_icon_key, (34, 34))
            if mic_surf:
                self.screen.blit(mic_surf, (mx + 14, my + 16))

            t_txt = self.font_bold.render(m['title'], True, (78, 205, 145) if m['completed'] else COLOR_TEXT_GOLD)
            self.screen.blit(t_txt, (mx + 60, my + 14))

            d_txt = self.font_small.render(m['desc'], True, COLOR_TEXT_LIGHT)
            self.screen.blit(d_txt, (mx + 60, my + 38))

            bar_w = 320
            bar_h = 12
            bx = mx + 60
            by = my + 64
            pct = min(1.0, m['progress'] / m['target'])

            pygame.draw.rect(self.screen, (10, 8, 14), (bx, by, bar_w, bar_h), border_radius=3)
            if pct > 0:
                fill_col = (78, 205, 145) if m['completed'] else (255, 215, 0)
                pygame.draw.rect(self.screen, fill_col, (bx, by, int(bar_w * pct), bar_h), border_radius=3)
            pygame.draw.rect(self.screen, (60, 50, 70), (bx, by, bar_w, bar_h), 1, border_radius=3)

            p_lbl = self.font_small.render(f"{m['progress']} / {m['target']}", True, COLOR_TEXT_LIGHT)
            self.screen.blit(p_lbl, (bx + bar_w + 10, by - 2))

            rew_txt = self.font_small.render(f"Recompensa: {m['reward']}", True, (220, 190, 120))
            self.screen.blit(rew_txt, (mx + 60, my + 88))

            st_txt = self.font_bold.render("COMPLETADA" if m['completed'] else "EN CURSO", True, (78, 205, 145) if m['completed'] else (160, 150, 140))
            self.screen.blit(st_txt, (mx + card_w - st_txt.get_width() - 14, my + 14))

        self.screen.set_clip(None)

        btn_scroll_up = pygame.Rect(WINDOW_WIDTH - 65, view_y + 40, 42, 42)
        btn_scroll_down = pygame.Rect(WINDOW_WIDTH - 65, view_y + 95, 42, 42)

        up_hover = btn_scroll_up.collidepoint(mouse_pos)
        pygame.draw.rect(self.screen, (48, 38, 58) if up_hover else (26, 20, 32), btn_scroll_up, border_radius=6)
        pygame.draw.rect(self.screen, (255, 215, 0) if up_hover else (80, 65, 95), btn_scroll_up, 1, border_radius=6)
        lbl_up = self.font_bold.render("▲", True, COLOR_TEXT_GOLD if up_hover else COLOR_TEXT_LIGHT)
        self.screen.blit(lbl_up, (btn_scroll_up.centerx - lbl_up.get_width() // 2, btn_scroll_up.centery - lbl_up.get_height() // 2))

        down_hover = btn_scroll_down.collidepoint(mouse_pos)
        pygame.draw.rect(self.screen, (48, 38, 58) if down_hover else (26, 20, 32), btn_scroll_down, border_radius=6)
        pygame.draw.rect(self.screen, (255, 215, 0) if down_hover else (80, 65, 95), btn_scroll_down, 1, border_radius=6)
        lbl_dn = self.font_bold.render("▼", True, COLOR_TEXT_GOLD if down_hover else COLOR_TEXT_LIGHT)
        self.screen.blit(lbl_dn, (btn_scroll_down.centerx - lbl_dn.get_width() // 2, btn_scroll_down.centery - lbl_dn.get_height() // 2))

        track_y = view_y + 155
        track_h = 240
        pygame.draw.rect(self.screen, (20, 16, 26), (WINDOW_WIDTH - 50, track_y, 12, track_h), border_radius=6)
        if self.max_missions_scroll > 0:
            thumb_h = max(28, int((view_h / content_h) * track_h))
            thumb_y = track_y + int((self.missions_scroll_y / self.max_missions_scroll) * (track_h - thumb_h))
            pygame.draw.rect(self.screen, (168, 85, 247), (WINDOW_WIDTH - 50, thumb_y, 12, thumb_h), border_radius=6)

        btn_back = pygame.Rect(WINDOW_WIDTH // 2 - 140, WINDOW_HEIGHT - 65, 280, 42)
        self.draw_button(btn_back, "VOLVER AL MENÚ", mouse_pos, icon_name="btn_back")

        return {'back': btn_back, 'scroll_up': btn_scroll_up, 'scroll_down': btn_scroll_down}

    def draw_settings(self, mouse_pos):
        self.draw_ambient_bg()

        hdr = self.font_title.render("AJUSTES DE AUDIO Y SISTEMA", True, COLOR_TEXT_GOLD)
        self.screen.blit(hdr, (WINDOW_WIDTH // 2 - hdr.get_width() // 2, 50))

        box_w, box_h = 600, 450
        bx = WINDOW_WIDTH // 2 - box_w // 2
        by = 120

        s_box = pygame.Rect(bx, by, box_w, box_h)
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, s_box, border_radius=10)
        pygame.draw.rect(self.screen, COLOR_PANEL_BORDER, s_box, 1, border_radius=10)

        y = by + 35
        m_lbl = self.font_header.render(f"Volumen de Música: {int(self.settings.get('music_volume') * 100)}%", True, COLOR_TEXT_LIGHT)
        self.screen.blit(m_lbl, (bx + 35, y))

        slider_music_rect = pygame.Rect(bx + 35, y + 36, 420, 12)
        pygame.draw.rect(self.screen, (40, 35, 25), slider_music_rect, border_radius=6)
        m_fill_w = int(420 * self.settings.get('music_volume'))
        pygame.draw.rect(self.screen, COLOR_TEXT_GOLD, (bx + 35, y + 36, m_fill_w, 12), border_radius=6)
        handle_m_rect = pygame.Rect(bx + 35 + m_fill_w - 9, y + 30, 18, 24)
        pygame.draw.rect(self.screen, (255, 255, 255), handle_m_rect, border_radius=4)

        y += 85
        s_lbl = self.font_header.render(f"Volumen de Efectos FX: {int(self.settings.get('sfx_volume') * 100)}%", True, COLOR_TEXT_LIGHT)
        self.screen.blit(s_lbl, (bx + 35, y))

        slider_sfx_rect = pygame.Rect(bx + 35, y + 36, 420, 12)
        pygame.draw.rect(self.screen, (40, 35, 25), slider_sfx_rect, border_radius=6)
        s_fill_w = int(420 * self.settings.get('sfx_volume'))
        pygame.draw.rect(self.screen, COLOR_TEXT_GOLD, (bx + 35, y + 36, s_fill_w, 12), border_radius=6)
        handle_s_rect = pygame.Rect(bx + 35 + s_fill_w - 9, y + 30, 18, 24)
        pygame.draw.rect(self.screen, (255, 255, 255), handle_s_rect, border_radius=4)

        btn_test = pygame.Rect(bx + 475, y + 25, 95, 34)
        self.draw_button(btn_test, "PROBAR", mouse_pos, icon_name="btn_play")

        y += 90
        diff_lbl = self.font_header.render("Dificultad de la IA Estratégica:", True, COLOR_TEXT_LIGHT)
        self.screen.blit(diff_lbl, (bx + 35, y))

        btn_diff_norm = pygame.Rect(bx + 35, y + 35, 160, 40)
        btn_diff_hard = pygame.Rect(bx + 215, y + 35, 160, 40)

        cur_diff = self.settings.get("difficulty")
        self.draw_button(btn_diff_norm, "NORMAL", mouse_pos, primary=(cur_diff == "Normal"))
        self.draw_button(btn_diff_hard, "MAESTRO", mouse_pos, primary=(cur_diff == "Maestro"))

        btn_back = pygame.Rect(WINDOW_WIDTH // 2 - 140, by + box_h + 25, 280, 42)
        self.draw_button(btn_back, "GUARDAR Y VOLVER", mouse_pos, icon_name="btn_back")

        return {
            'slider_music': slider_music_rect,
            'slider_sfx': slider_sfx_rect,
            'test_sound': btn_test,
            'diff_normal': btn_diff_norm,
            'diff_hard': btn_diff_hard,
            'back': btn_back
        }

    def draw_rules(self, mouse_pos):
        self.draw_ambient_bg()

        hdr = self.font_title.render("REGLAS Y GUÍA TÁCTICA", True, COLOR_TEXT_GOLD)
        self.screen.blit(hdr, (WINDOW_WIDTH // 2 - hdr.get_width() // 2, 35))

        box_w, box_h = 1000, 520
        bx = WINDOW_WIDTH // 2 - box_w // 2
        by = 85

        r_box = pygame.Rect(bx, by, box_w, box_h)
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, r_box, border_radius=10)
        pygame.draw.rect(self.screen, COLOR_PANEL_BORDER, r_box, 1, border_radius=10)

        sections = [
            ("I. OBJETIVO PRINCIPAL", [
                "• Conduce la Bandera Sagrada al bastión enemigo de tu meta (Esquina [15,0] para Alianza Solar, Esquina [0,15] para Eclipse).",
                "• O bien elimina a todos los Generales de los comandantes enemigos en combate.",
                "• Cada bando cuenta con Puntos de Acción (2 PA por turno) para mover, atacar o invocar."
            ]),
            ("II. TROPAS Y COMBATE", [
                "• Soldado (P): Avanza hasta 2 casillas. Ataque a 1 paso adyacente o diagonal (2 ATK, 3 HP).",
                "• Tanque (R): Se desplaza en línea recta hasta 6 casillas. Gran blindaje (4 ATK, 6 HP).",
                "• Caballería (N): Saltos en L y amplios ([1,2], [1,3], [2,3]). Ignora obstáculos (3 ATK, 4 HP).",
                "• Médico (B): Diagonal hasta 5 casillas. Cura pasivamente +1 HP a aliados vecinos cada turno (1 ATK, 3 HP).",
                "• General (K): Desplazamiento omnidireccional a 2 casillas. Si muere, ¡su facción es eliminada!"
            ]),
            ("III. VIDAS DE COMANDANTE Y OBJETOS DEL MAPA", [
                "• Cada Comandante posee 3 a 5 Vidas. Perder 2 soldados o una tropa mayor cuesta 1 Vida.",
                "• Esencia de Vida: Recogerla en el mapa suma +1 Vida de Comandante y cura +2 HP a la unidad.",
                "• Rayo Táctico: Otorga +1 de alcance extra al movimiento.",
                "• Trampa Mortal: Inmoviliza la tropa 1 turno y cuesta 1 Vida de Comandante al pisarla.",
                "• Portal Umbrío: Teletransporta de inmediato la pieza a los márgenes seguros del tablero."
            ])
        ]

        sy = by + 25
        for stitle, slines in sections:
            st = self.font_header.render(stitle, True, COLOR_TEXT_GOLD)
            self.screen.blit(st, (bx + 35, sy))
            sy += 30
            for line in slines:
                lt = self.font_body.render(line, True, COLOR_TEXT_LIGHT)
                self.screen.blit(lt, (bx + 45, sy))
                sy += 24
            sy += 16

        btn_back = pygame.Rect(WINDOW_WIDTH // 2 - 140, WINDOW_HEIGHT - 70, 280, 42)
        self.draw_button(btn_back, "VOLVER AL MENÚ", mouse_pos, icon_name="btn_back")

        return {'back': btn_back}

    def get_fade_surfaces(self, width, fade_h, bg_color=(16, 13, 22)):
        if (self.credits_top_fade is not None and 
            self.credits_top_fade.get_width() == width and 
            self.credits_top_fade.get_height() == fade_h):
            return self.credits_top_fade, self.credits_bot_fade

        top_fade = pygame.Surface((width, fade_h), pygame.SRCALPHA)
        bot_fade = pygame.Surface((width, fade_h), pygame.SRCALPHA)
        for y in range(fade_h):
            ratio = y / float(fade_h)
            alpha_top = int(255 * ((1.0 - ratio) ** 1.3))
            pygame.draw.line(top_fade, (*bg_color, alpha_top), (0, y), (width, y))
            alpha_bot = int(255 * (ratio ** 1.3))
            pygame.draw.line(bot_fade, (*bg_color, alpha_bot), (0, y), (width, y))

        self.credits_top_fade = top_fade
        self.credits_bot_fade = bot_fade
        return top_fade, bot_fade

    def build_credits_surface(self, content_w):
        est_h = 2400
        temp_surf = pygame.Surface((content_w, est_h), pygame.SRCALPHA)
        temp_surf.fill((16, 13, 22))

        cx = content_w // 2
        y = 35

        def draw_banner(y_pos, title, width=640):
            rx = cx - width // 2
            pill_surf = pygame.Surface((width, 28), pygame.SRCALPHA)
            pygame.draw.rect(pill_surf, (28, 20, 38, 230), (0, 0, width, 28), border_radius=14)
            pygame.draw.rect(pill_surf, (212, 175, 55, 180), (0, 0, width, 28), 1, border_radius=14)
            temp_surf.blit(pill_surf, (rx, y_pos))
            self.draw_vector_star(temp_surf, rx + 14, y_pos + 6, size=16, color=(255, 215, 60))
            self.draw_vector_star(temp_surf, rx + width - 30, y_pos + 6, size=16, color=(255, 215, 60))
            txt = self.font_bold.render(title, True, (255, 225, 120))
            temp_surf.blit(txt, (cx - txt.get_width() // 2, y_pos + 5))
            return y_pos + 42

        t_sh = self.font_title_big.render("CHRONICLES OF TWO SUNS", True, (0, 0, 0))
        t_gl = self.font_title_big.render("CHRONICLES OF TWO SUNS", True, (168, 85, 247))
        t_main = self.font_title_big.render("CHRONICLES OF TWO SUNS", True, (255, 220, 100))
        temp_surf.blit(t_sh, (cx - t_main.get_width() // 2 + 2, y + 2))
        temp_surf.blit(t_gl, (cx - t_main.get_width() // 2 + 1, y + 1))
        temp_surf.blit(t_main, (cx - t_main.get_width() // 2, y))
        self.draw_vector_star(temp_surf, cx - t_main.get_width() // 2 - 36, y + 8, size=22, color=(255, 215, 60))
        self.draw_vector_star(temp_surf, cx + t_main.get_width() // 2 + 14, y + 8, size=22, color=(168, 85, 247))
        y += 48

        sub1 = self.font_header.render("EL CONFLICTO DE LOS DOS SOLES", True, (215, 195, 245))
        temp_surf.blit(sub1, (cx - sub1.get_width() // 2, y))
        y += 30

        quote = self.font_small.render("«En la encrucijada de dos soles ardientes, el destino de cuatro imperios se decide en cada movimiento.»", True, (190, 180, 210))
        temp_surf.blit(quote, (cx - quote.get_width() // 2, y))
        y += 24

        pygame.draw.line(temp_surf, (180, 145, 65), (cx - 240, y + 6), (cx + 240, y + 6), 1)
        self.draw_vector_star(temp_surf, cx - 7, y, size=14, color=(255, 215, 60))
        y += 32

        y = draw_banner(y, "IDEA ORIGINAL, CONCEPTO E HISTORIA")
        c_box = pygame.Rect(cx - 390, y, 780, 80)
        pygame.draw.rect(temp_surf, (22, 18, 30), c_box, border_radius=10)
        pygame.draw.rect(temp_surf, (75, 60, 95), c_box, 1, border_radius=10)
        name1 = self.font_title.render("Josue Gomez", True, (255, 235, 150))
        alias1 = self.font_bold.render("(Fundador de la Saga · Alias: Sadezu)", True, (180, 150, 235))
        desc1 = self.font_body.render("Creador del universo, trasfondo mitológico, reglas de guerra y diseño narrativo original.", True, COLOR_TEXT_LIGHT)
        surf_w_names = name1.get_width() + alias1.get_width() + 10
        temp_surf.blit(name1, (cx - surf_w_names // 2, y + 14))
        temp_surf.blit(alias1, (cx - surf_w_names // 2 + name1.get_width() + 10, y + 20))
        temp_surf.blit(desc1, (cx - desc1.get_width() // 2, y + 48))
        y += 105

        y = draw_banner(y, "DESARROLLO DE SOFTWARE Y ARQUITECTURA")
        card_w = 425
        card_h = 88
        l_rect = pygame.Rect(cx - card_w - 12, y, card_w, card_h)
        pygame.draw.rect(temp_surf, (22, 18, 30), l_rect, border_radius=10)
        pygame.draw.rect(temp_surf, (75, 60, 95), l_rect, 1, border_radius=10)
        ln = self.font_header.render("Josue Gomez", True, (255, 220, 120))
        lr = self.font_small.render("Arquitectura del juego, balance táctico y combate", True, COLOR_TEXT_LIGHT)
        temp_surf.blit(ln, (l_rect.centerx - ln.get_width() // 2, y + 16))
        temp_surf.blit(lr, (l_rect.centerx - lr.get_width() // 2, y + 46))

        r_rect = pygame.Rect(cx + 12, y, card_w, card_h)
        pygame.draw.rect(temp_surf, (22, 18, 30), r_rect, border_radius=10)
        pygame.draw.rect(temp_surf, (75, 60, 95), r_rect, 1, border_radius=10)
        rn = self.font_header.render("Oliver Camacho", True, (255, 220, 120))
        rr = self.font_small.render("Desarrollo de software, sistemas de tablero y optimización", True, COLOR_TEXT_LIGHT)
        temp_surf.blit(rn, (r_rect.centerx - rn.get_width() // 2, y + 16))
        temp_surf.blit(rr, (r_rect.centerx - rr.get_width() // 2, y + 46))
        y += 112

        y = draw_banner(y, "EL ORIGEN: UNA SAGA COMUNITARIA (2018 - 2026+)")
        hist_box = pygame.Rect(cx - 435, y, 870, 116)
        pygame.draw.rect(temp_surf, (20, 16, 28), hist_box, border_radius=10)
        pygame.draw.rect(temp_surf, (160, 125, 60), hist_box, 1, border_radius=10)
        lines_h = [
            "Nacido en 2018 del servidor de roleplay y Dungeons & Dragons que Josue fundó bajo el alias de Sadezu,",
            "y de su gran sueño de crear un videojuego estilo RPG táctico ambientado en ese fascinante mundo.",
            "Cada partida, cada victoria y cada comandante a lo largo de 8 años vive en este tablero.",
            "«Todo lo vivido por los jugadores de las eras anteriores forma parte viva de la historia de este juego.»"
        ]
        hy = y + 14
        for idx, lh in enumerate(lines_h):
            col = (255, 220, 140) if idx == 3 else ((225, 220, 235) if idx < 2 else (200, 190, 215))
            fnt = self.font_bold if idx == 3 else self.font_small
            ls = fnt.render(lh, True, col)
            temp_surf.blit(ls, (cx - ls.get_width() // 2, hy))
            hy += 23
        y += 140

        y = draw_banner(y, "CRONOLOGÍA DE LAS CUATRO GRANDES ERAS")
        eras = [
            ("2018 – 2019", "THE ABYSS", "El surgimiento de las primeras fuerzas primordiales y la caída de los antiguos reinos.", (255, 215, 90)),
            ("2020 – 2024", "THE EXODUS CHRONICLES", "La gran migración de los pueblos, la lucha por recursos sagrados y el alzamiento de nuevas naciones.", (180, 160, 230)),
            ("2024 – 2025", "SOUL OF VELKANOR", "La encarnación del alma de Velkanor y las guerras de fuego y éter que fracturaron el continente.", (255, 100, 100)),
            ("2026 – PRESENTE", "THE CHRONICLES OF TWO SUNS", "El amanecer de los Dos Soles celestiales y el choque final entre cuatro grandes imperios.", (78, 205, 145))
        ]
        for dates, ename, edesc, ecol in eras:
            eb = pygame.Rect(cx - 435, y, 870, 52)
            pygame.draw.rect(temp_surf, (20, 16, 26), eb, border_radius=8)
            pygame.draw.rect(temp_surf, (*ecol, 140), eb, 1, border_radius=8)
            pygame.draw.rect(temp_surf, ecol, (eb.x, eb.y + 8, 4, 36), border_radius=2)
            d_surf = self.font_bold.render(dates, True, ecol)
            n_surf = self.font_header.render(ename, True, COLOR_TEXT_LIGHT)
            desc_surf = self.font_small.render(edesc, True, (195, 190, 210))
            temp_surf.blit(d_surf, (eb.x + 20, eb.y + 16))
            temp_surf.blit(n_surf, (eb.x + 180, eb.y + 14))
            temp_surf.blit(desc_surf, (eb.x + 400, eb.y + 18))
            y += 60
        y += 24

        y = draw_banner(y, "LAS CUATRO NACIONES Y SUS COMANDANTES")
        factions_data = [
            ("Solcardena", "Helio, el Heraldo Solar", "Comandante Supremo de la Luz · Maestros del honor y expansión", (255, 215, 0)),
            ("Royaume D'Aurelium", "Selene, Oráculo de las Mareas", "Reino Místico Lunar · Sabios alquimistas y devotos del éter", (177, 156, 217)),
            ("Imperio de Varkhental", "Ignis, Señor de la Ceniza", "Fuerza volcánica de acero y fuego · Guerreros de implacable disciplina", (255, 80, 80)),
            ("Imperio Sthalgard", "Kaelen, Guardia de Hierro", "Bastión esmeralda del norte · Titanes tácticos y defensa inexpugnable", (78, 205, 145))
        ]
        for idx, (fac_name, cmd_name, fac_desc, fac_col) in enumerate(factions_data):
            col_idx = idx % 2
            row_idx = idx // 2
            bx = cx - 435 if col_idx == 0 else cx + 10
            by_card = y + row_idx * 72
            fb = pygame.Rect(bx, by_card, 425, 64)
            pygame.draw.rect(temp_surf, (20, 16, 26), fb, border_radius=8)
            pygame.draw.rect(temp_surf, (*fac_col, 150), fb, 1, border_radius=8)
            pygame.draw.circle(temp_surf, fac_col, (fb.x + 18, fb.y + 20), 6)
            fn_s = self.font_bold.render(fac_name, True, fac_col)
            cn_s = self.font_small.render(f"Comandante: {cmd_name}", True, COLOR_TEXT_LIGHT)
            fd_s = self.font_small.render(fac_desc, True, (170, 165, 185))
            temp_surf.blit(fn_s, (fb.x + 32, fb.y + 11))
            temp_surf.blit(cn_s, (fb.x + 32, fb.y + 28))
            temp_surf.blit(fd_s, (fb.x + 32, fb.y + 44))
        y += 2 * 72 + 24

        y = draw_banner(y, "TECNOLOGÍA Y HERRAMIENTAS")
        tb = pygame.Rect(cx - 435, y, 870, 94)
        pygame.draw.rect(temp_surf, (20, 16, 28), tb, border_radius=8)
        pygame.draw.rect(temp_surf, (70, 60, 90), tb, 1, border_radius=8)
        tech_lines = [
            "• Programado íntegramente en Python con Pygame-CE a 60 FPS estables",
            "• Sistema de Inteligencia Artificial táctica con evaluación heurística posicional y perfiles por facción",
            "• Generación procedural de audio retro y sintetizador para efectos de impacto y batalla",
            "• Prototipo inicial y diseño conceptual desarrollado con apoyo de Claude (Anthropic)"
        ]
        ty = y + 10
        for tl in tech_lines:
            ts = self.font_small.render(tl, True, COLOR_TEXT_LIGHT)
            temp_surf.blit(ts, (tb.x + 24, ty))
            ty += 20
        y += 116

        y = draw_banner(y, "AGRADECIMIENTOS ESPECIALES")
        ab = pygame.Rect(cx - 435, y, 870, 84)
        pygame.draw.rect(temp_surf, (20, 16, 28), ab, border_radius=8)
        pygame.draw.rect(temp_surf, (180, 140, 60), ab, 1, border_radius=8)
        thx_lines = [
            "A cada miembro de la comunidad de ayer y de hoy por construir y preservar esta historia.",
            "A todos los jugadores por cada tirada de dados, cada duelo épico y por mantener vivo este sueño.",
            "¡Sin ustedes, este universo no existiría!"
        ]
        ay = y + 12
        for thx in thx_lines:
            asurf = self.font_body.render(thx, True, (255, 230, 180) if thx == thx_lines[-1] else COLOR_TEXT_LIGHT)
            temp_surf.blit(asurf, (cx - asurf.get_width() // 2, ay))
            ay += 23
        y += 110

        y += 20
        self.draw_vector_star(temp_surf, cx - 40, y + 4, size=18, color=(255, 215, 60))
        self.draw_vector_star(temp_surf, cx, y, size=24, color=(255, 235, 120))
        self.draw_vector_star(temp_surf, cx + 24, y + 4, size=18, color=(255, 215, 60))
        y += 38

        thx_big_sh = self.font_title_big.render("¡GRACIAS POR JUGAR!", True, (0, 0, 0))
        thx_big_gl = self.font_title_big.render("¡GRACIAS POR JUGAR!", True, (168, 85, 247))
        thx_big = self.font_title_big.render("¡GRACIAS POR JUGAR!", True, (255, 220, 80))
        temp_surf.blit(thx_big_sh, (cx - thx_big.get_width() // 2 + 2, y + 2))
        temp_surf.blit(thx_big_gl, (cx - thx_big.get_width() // 2 + 1, y + 1))
        temp_surf.blit(thx_big, (cx - thx_big.get_width() // 2, y))
        y += 48

        end_sub = self.font_header.render("CHRONICLES OF TWO SUNS · TEMPORADA 2", True, (215, 195, 245))
        temp_surf.blit(end_sub, (cx - end_sub.get_width() // 2, y))
        y += 30

        end_tag = self.font_small.render("«Que la gloria de los dos soles acompañe tu camino en el campo de batalla.»", True, (190, 180, 210))
        temp_surf.blit(end_tag, (cx - end_tag.get_width() // 2, y))
        y += 90

        final_h = y
        self.credits_content_h = final_h
        self.credits_surface = pygame.Surface((content_w, final_h), pygame.SRCALPHA)
        self.credits_surface.blit(temp_surf, (0, 0), (0, 0, content_w, final_h))
        self.credits_max_scroll = max(0.0, float(final_h - 505))

    def draw_credits(self, mouse_pos):
        self.draw_ambient_bg()

        anim_progress = min(1.0, self.credits_entrance_time / 0.5)
        slide_offset = int((1.0 - anim_progress) ** 2 * 60)

        hdr_y = 22 - slide_offset
        hdr = self.font_title.render("CRÉDITOS Y ORIGEN DE LA SAGA", True, COLOR_TEXT_GOLD)
        hdr_sh = self.font_title.render("CRÉDITOS Y ORIGEN DE LA SAGA", True, (0, 0, 0))
        tx = WINDOW_WIDTH // 2 - hdr.get_width() // 2
        self.screen.blit(hdr_sh, (tx + 2, hdr_y + 2))
        self.screen.blit(hdr, (tx, hdr_y))
        self.draw_vector_star(self.screen, tx - 32, hdr_y + 8, size=18, color=(255, 215, 60))
        self.draw_vector_star(self.screen, tx + hdr.get_width() + 14, hdr_y + 8, size=18, color=(168, 85, 247))

        box_w, box_h = 1040, 520
        bx = WINDOW_WIDTH // 2 - box_w // 2
        by = 68 - slide_offset

        c_box = pygame.Rect(bx, by, box_w, box_h)
        pygame.draw.rect(self.screen, (16, 13, 22), c_box, border_radius=12)
        pygame.draw.rect(self.screen, (180, 140, 60), c_box, 1, border_radius=12)
        pygame.draw.rect(self.screen, (255, 215, 60), (bx, by, box_w, 3), border_radius=2)

        bracket_len = 16
        c_gold = (255, 225, 120)
        pygame.draw.line(self.screen, c_gold, (bx + 2, by + 2), (bx + 2 + bracket_len, by + 2), 2)
        pygame.draw.line(self.screen, c_gold, (bx + 2, by + 2), (bx + 2, by + 2 + bracket_len), 2)
        pygame.draw.line(self.screen, c_gold, (bx + box_w - 3, by + 2), (bx + box_w - 3 - bracket_len, by + 2), 2)
        pygame.draw.line(self.screen, c_gold, (bx + box_w - 3, by + 2), (bx + box_w - 3, by + 2 + bracket_len), 2)
        pygame.draw.line(self.screen, c_gold, (bx + 2, by + box_h - 3), (bx + 2 + bracket_len, by + box_h - 3), 2)
        pygame.draw.line(self.screen, c_gold, (bx + 2, by + box_h - 3), (bx + 2, by + box_h - 3 - bracket_len), 2)
        pygame.draw.line(self.screen, c_gold, (bx + box_w - 3, by + box_h - 3), (bx + box_w - 3 - bracket_len, by + box_h - 3), 2)
        pygame.draw.line(self.screen, c_gold, (bx + box_w - 3, by + box_h - 3), (bx + box_w - 3, by + box_h - 3 - bracket_len), 2)

        vw = box_w - 34
        vh = box_h - 14
        vx = bx + 8
        vy = by + 7

        if self.credits_surface is None:
            self.build_credits_surface(vw)

        viewport_surf = pygame.Surface((vw, vh), pygame.SRCALPHA)
        viewport_surf.fill((16, 13, 22))

        viewport_surf.blit(self.credits_surface, (0, int(-self.credits_scroll_y)))

        fade_h = 55
        top_f, bot_f = self.get_fade_surfaces(vw, fade_h, (16, 13, 22))
        viewport_surf.blit(top_f, (0, 0))
        viewport_surf.blit(bot_f, (0, vh - fade_h))

        self.screen.blit(viewport_surf, (vx, vy))

        track_w = 8
        track_h = box_h - 32
        track_x = bx + box_w - 18
        track_y = by + 16
        self.credits_track_top = track_y
        self.credits_track_h = track_h

        track_rect = pygame.Rect(track_x, track_y, track_w, track_h)
        pygame.draw.rect(self.screen, (28, 22, 38), track_rect, border_radius=4)
        pygame.draw.rect(self.screen, (70, 55, 90), track_rect, 1, border_radius=4)

        thumb_h = max(32, int(track_h * (vh / max(vh, self.credits_content_h))))
        scroll_pct = self.credits_scroll_y / max(1.0, self.credits_max_scroll)
        thumb_y = track_y + int((track_h - thumb_h) * scroll_pct)
        thumb_rect = pygame.Rect(track_x, thumb_y, track_w, thumb_h)

        is_thumb_hover = thumb_rect.collidepoint(mouse_pos)
        thumb_col = (255, 215, 60) if (is_thumb_hover or self.dragging_credits) else (180, 140, 60)
        pygame.draw.rect(self.screen, thumb_col, thumb_rect, border_radius=4)

        btn_y = WINDOW_HEIGHT - 56
        btn_h = 38
        w_back = 190
        w_pause = 135
        w_dir = 145
        w_speed = 120
        w_restart = 130
        gap = 12

        total_dock_w = w_back + w_pause + w_dir + w_speed + w_restart + gap * 4
        start_dock_x = WINDOW_WIDTH // 2 - total_dock_w // 2

        btn_back = pygame.Rect(start_dock_x, btn_y, w_back, btn_h)
        btn_pause = pygame.Rect(start_dock_x + w_back + gap, btn_y, w_pause, btn_h)
        btn_dir = pygame.Rect(btn_pause.right + gap, btn_y, w_dir, btn_h)
        btn_speed = pygame.Rect(btn_dir.right + gap, btn_y, w_speed, btn_h)
        btn_restart = pygame.Rect(btn_speed.right + gap, btn_y, w_restart, btn_h)

        self.draw_button(btn_back, "VOLVER AL MENÚ", mouse_pos, icon_name="btn_back")
        pause_txt = "▶ REANUDAR" if self.credits_paused else "⏸ PAUSAR"
        self.draw_button(btn_pause, pause_txt, mouse_pos)
        dir_txt = "DIR: ↓ BAJAR" if self.credits_direction == 1 else "DIR: ↑ SUBIR"
        self.draw_button(btn_dir, dir_txt, mouse_pos)
        self.draw_button(btn_speed, f"VEL: {self.credits_speed_mult:g}x", mouse_pos)
        self.draw_button(btn_restart, "↺ REINICIAR", mouse_pos)

        hint_str = "Rueda del ratón [SCROLL] o flechas [↑/↓] para mover · [ESPACIO] pausar"
        hint_surf = self.font_small.render(hint_str, True, (150, 140, 170))
        self.screen.blit(hint_surf, (WINDOW_WIDTH // 2 - hint_surf.get_width() // 2, WINDOW_HEIGHT - 16))

        return {
            'back': btn_back,
            'pause': btn_pause,
            'direction': btn_dir,
            'speed': btn_speed,
            'restart': btn_restart,
            'scrollbar': track_rect,
            'track_top': track_y,
            'track_h': track_h
        }

    def draw_pause_modal(self, mouse_pos):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.screen.blit(overlay, (0, 0))

        mw, mh = 380, 280
        mx = WINDOW_WIDTH // 2 - mw // 2
        my = WINDOW_HEIGHT // 2 - mh // 2

        m_rect = pygame.Rect(mx, my, mw, mh)
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, m_rect, border_radius=12)
        pygame.draw.rect(self.screen, COLOR_TEXT_GOLD, m_rect, 2, border_radius=12)

        t_lbl = self.font_title.render("JUEGO EN PAUSA", True, COLOR_TEXT_GOLD)
        self.screen.blit(t_lbl, (mx + mw // 2 - t_lbl.get_width() // 2, my + 30))

        btn_resume = pygame.Rect(mx + 40, my + 95, 300, 44)
        btn_restart = pygame.Rect(mx + 40, my + 150, 300, 44)
        btn_quit = pygame.Rect(mx + 40, my + 205, 300, 44)

        self.draw_button(btn_resume, "CONTINUAR BATALLA", mouse_pos, primary=True, icon_name="btn_play")
        self.draw_button(btn_restart, "REINICIAR PARTIDA", mouse_pos, icon_name="btn_settings")
        self.draw_button(btn_quit, "SALIR AL MENÚ", mouse_pos, icon_name="btn_quit")

        return {
            'resume': btn_resume,
            'restart': btn_restart,
            'quit': btn_quit
        }

    def draw_game_over_modal(self, reason, mouse_pos, enemy_team=None):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 225))
        self.screen.blit(overlay, (0, 0))

        mw, mh = 520, 340
        mx = WINDOW_WIDTH // 2 - mw // 2
        my = WINDOW_HEIGHT // 2 - mh // 2

        m_rect = pygame.Rect(mx, my, mw, mh)
        pygame.draw.rect(self.screen, (34, 14, 18), m_rect, border_radius=12)
        pygame.draw.rect(self.screen, (255, 60, 60), m_rect, 3, border_radius=12)

        glow_surf = pygame.Surface((mw + 10, mh + 10), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (255, 50, 50, 40), (0, 0, mw + 10, mh + 10), border_radius=14)
        self.screen.blit(glow_surf, (mx - 5, my - 5))

        t_lbl = self.font_title_big.render("GAME OVER", True, (255, 65, 65))
        self.screen.blit(t_lbl, (mx + mw // 2 - t_lbl.get_width() // 2, my + 24))

        sub_txt = f"¡PERDISTE! Ganó el {enemy_team}" if enemy_team else "¡HAS PERDIDO LA BATALLA!"
        sub = self.font_header.render(sub_txt, True, (255, 215, 120))
        self.screen.blit(sub, (mx + mw // 2 - sub.get_width() // 2, my + 82))

        r_lines = []
        if len(reason) > 52:
            r_lines.append(reason[:50])
            r_lines.append(reason[50:105])
        else:
            r_lines.append(reason)

        for li, rl in enumerate(r_lines):
            r_lbl = self.font_body.render(rl.strip(), True, (230, 190, 190))
            self.screen.blit(r_lbl, (mx + mw // 2 - r_lbl.get_width() // 2, my + 118 + li * 22))

        btn_retry = pygame.Rect(mx + 70, my + 195, 380, 46)
        btn_menu = pygame.Rect(mx + 70, my + 255, 380, 46)

        self.draw_button(btn_retry, "REINTENTAR PARTIDA", mouse_pos, primary=True, icon_name="btn_play")
        self.draw_button(btn_menu, "VOLVER AL MENÚ PRINCIPAL", mouse_pos, icon_name="btn_quit")

        return {
            'retry': btn_retry,
            'menu': btn_menu
        }

    def draw_victory_modal(self, team_name, reason, mouse_pos):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))

        mw, mh = 520, 340
        mx = WINDOW_WIDTH // 2 - mw // 2
        my = WINDOW_HEIGHT // 2 - mh // 2

        m_rect = pygame.Rect(mx, my, mw, mh)
        pygame.draw.rect(self.screen, (30, 28, 15), m_rect, border_radius=12)
        pygame.draw.rect(self.screen, COLOR_TEXT_GOLD, m_rect, 3, border_radius=12)

        t_lbl = self.font_title.render("¡GLORIOSA VICTORIA!", True, COLOR_TEXT_GOLD)
        self.screen.blit(t_lbl, (mx + mw // 2 - t_lbl.get_width() // 2, my + 30))

        tm_lbl = self.font_header.render(team_name, True, (255, 255, 255))
        self.screen.blit(tm_lbl, (mx + mw // 2 - tm_lbl.get_width() // 2, my + 85))

        r_lbl = self.font_body.render(reason[:50], True, (230, 210, 150))
        self.screen.blit(r_lbl, (mx + mw // 2 - r_lbl.get_width() // 2, my + 125))

        btn_replay = pygame.Rect(mx + 70, my + 195, 380, 46)
        btn_menu = pygame.Rect(mx + 70, my + 255, 380, 46)

        self.draw_button(btn_replay, "JUGAR OTRA PARTIDA", mouse_pos, primary=True, icon_name="btn_play")
        self.draw_button(btn_menu, "VOLVER AL MENÚ PRINCIPAL", mouse_pos, icon_name="btn_quit")

        return {
            'replay': btn_replay,
            'menu': btn_menu
        }
