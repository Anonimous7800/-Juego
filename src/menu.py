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

        self.dragging_music = False
        self.dragging_sfx = False
        self.missions_scroll_y = 0.0
        self.max_missions_scroll = 260.0

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

    def scroll_missions(self, delta):
        self.missions_scroll_y = max(0.0, min(self.max_missions_scroll, self.missions_scroll_y - delta))

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

    def update(self, dt):
        self.time += dt
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

    def draw_main_menu(self, mouse_pos):
        self.draw_ambient_bg()

        title_txt = self.font_title_big.render("CHRONICLES OF TWO SUNS T2", True, (255, 225, 120))
        glow_txt = self.font_title_big.render("CHRONICLES OF TWO SUNS T2", True, (168, 85, 247))
        shadow_txt = self.font_title_big.render("CHRONICLES OF TWO SUNS T2", True, (0, 0, 0))

        tx = WINDOW_WIDTH // 2 - title_txt.get_width() // 2
        ty = 50
        self.screen.blit(shadow_txt, (tx + 3, ty + 3))
        self.screen.blit(glow_txt, (tx + 1, ty + 1))
        self.screen.blit(title_txt, (tx, ty))

        self.draw_vector_star(self.screen, tx - 36, ty + 12, size=24, color=(255, 215, 60))
        self.draw_vector_star(self.screen, tx + title_txt.get_width() + 12, ty + 12, size=24, color=(168, 85, 247))

        badge_w = 580
        badge_rect = pygame.Rect(WINDOW_WIDTH // 2 - badge_w // 2, ty + 56, badge_w, 28)
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

        plate_w, plate_h = 440, 440
        plate_x = WINDOW_WIDTH // 2 - plate_w // 2
        plate_y = 145
        plate_surf = pygame.Surface((plate_w, plate_h), pygame.SRCALPHA)
        pygame.draw.rect(plate_surf, (12, 9, 20, 195), (0, 0, plate_w, plate_h), border_radius=12)
        pygame.draw.rect(plate_surf, (190, 150, 80, 110), (0, 0, plate_w, plate_h), 1, border_radius=12)
        self.screen.blit(plate_surf, (plate_x, plate_y))

        btn_w, btn_h = 390, 40
        bx = WINDOW_WIDTH // 2 - btn_w // 2
        start_y = 155
        gap = 48

        buttons = {
            'play': pygame.Rect(bx, start_y, btn_w, btn_h),
            'tutorial': pygame.Rect(bx, start_y + gap, btn_w, btn_h),
            'characters': pygame.Rect(bx, start_y + gap * 2, btn_w, btn_h),
            'missions': pygame.Rect(bx, start_y + gap * 3, btn_w, btn_h),
            'settings': pygame.Rect(bx, start_y + gap * 4, btn_w, btn_h),
            'rules': pygame.Rect(bx, start_y + gap * 5, btn_w, btn_h),
            'credits': pygame.Rect(bx, start_y + gap * 6, btn_w, btn_h),
            'quit': pygame.Rect(bx, start_y + gap * 7, btn_w, btn_h)
        }

        self.draw_button(buttons['play'], "JUGAR PARTIDA BÉLICA", mouse_pos, primary=True, icon_name="btn_play")
        self.draw_button(buttons['tutorial'], "INSTRUCCIÓN MILITAR (TUTORIAL)", mouse_pos, icon_name="btn_tutorial")
        self.draw_button(buttons['characters'], "COMANDANTES Y FACCIONES", mouse_pos, icon_name="btn_characters")
        self.draw_button(buttons['missions'], "MISIONES Y RECOMPENSAS", mouse_pos, icon_name="btn_missions")
        self.draw_button(buttons['settings'], "AJUSTES DE AUDIO Y SISTEMA", mouse_pos, icon_name="btn_settings")
        self.draw_button(buttons['rules'], "ENCICLOPEDIA Y REGLAS", mouse_pos, icon_name="btn_rules")
        self.draw_button(buttons['credits'], "CRÉDITOS Y COMUNIDAD", mouse_pos, icon_name="btn_oracle")
        self.draw_button(buttons['quit'], "SALIR DEL JUEGO", mouse_pos, icon_name="btn_quit")

        ft_y = WINDOW_HEIGHT - 48
        factions_info = [
            ("Solcardena", (255, 215, 0)),
            ("Royaume D'Aurelium", (177, 156, 217)),
            ("Imperio de Varkhental", (255, 80, 80)),
            ("Imperio Sthalgard", (78, 205, 145))
        ]
        total_bar_w = 800
        start_f_x = WINDOW_WIDTH // 2 - total_bar_w // 2
        f_gap = total_bar_w // 4

        for fi, (fname, fcol) in enumerate(factions_info):
            fx = start_f_x + fi * f_gap
            pill_rect = pygame.Rect(fx, ft_y - 2, f_gap - 12, 22)
            pill_surf = pygame.Surface((pill_rect.width, pill_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(pill_surf, (18, 14, 26, 190), (0, 0, pill_rect.width, pill_rect.height), border_radius=11)
            pygame.draw.rect(pill_surf, (*fcol, 140), (0, 0, pill_rect.width, pill_rect.height), 1, border_radius=11)
            pygame.draw.circle(pill_surf, fcol, (10, pill_rect.height // 2), 4)
            self.screen.blit(pill_surf, (pill_rect.x, pill_rect.y))
            tag_surf = self.font_small.render(fname, True, fcol)
            self.screen.blit(tag_surf, (pill_rect.x + 20, pill_rect.centery - tag_surf.get_height() // 2))

        ft_txt = self.font_small.render("Chronicles Of Two Suns T2 · Pygame Edition · 60 FPS", True, (140, 130, 155))
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

    def draw_credits(self, mouse_pos):
        self.draw_ambient_bg()

        hdr = self.font_title.render("CRÉDITOS Y ORIGEN DE LA SAGA", True, COLOR_TEXT_GOLD)
        self.screen.blit(hdr, (WINDOW_WIDTH // 2 - hdr.get_width() // 2, 26))

        box_w, box_h = 1020, 560
        bx = WINDOW_WIDTH // 2 - box_w // 2
        by = 74

        c_box = pygame.Rect(bx, by, box_w, box_h)
        pygame.draw.rect(self.screen, (16, 13, 22), c_box, border_radius=12)
        pygame.draw.rect(self.screen, (180, 140, 60), c_box, 1, border_radius=12)
        pygame.draw.rect(self.screen, (255, 215, 60), (bx, by, box_w, 3), border_radius=2)

        left_x = bx + 36
        y = by + 20

        t1 = self.font_header.render("EL CONFLICTO DE LOS DOS SOLES", True, (255, 215, 120))
        t2 = self.font_bold.render("The Chronicles Of Two Suns", True, (180, 160, 220))
        self.screen.blit(t1, (left_x, y))
        self.screen.blit(t2, (left_x, y + 24))
        y += 54

        s1 = self.font_bold.render("IDEA ORIGINAL, CONCEPTO E HISTORIA", True, COLOR_TEXT_GOLD)
        self.screen.blit(s1, (left_x, y))
        y += 20
        a1 = self.font_body.render("• Josue Gomez.", True, COLOR_TEXT_LIGHT)
        self.screen.blit(a1, (left_x + 12, y))
        y += 28

        s2 = self.font_bold.render("DESARROLLO", True, COLOR_TEXT_GOLD)
        self.screen.blit(s2, (left_x, y))
        y += 20
        a2 = self.font_body.render("• Josue Gomez", True, COLOR_TEXT_LIGHT)
        a3 = self.font_body.render("• Oliver Camacho", True, COLOR_TEXT_LIGHT)
        self.screen.blit(a2, (left_x + 12, y))
        self.screen.blit(a3, (left_x + 12, y + 20))
        y += 48

        s3 = self.font_bold.render("UN JUEGO DE LA COMUNIDAD", True, COLOR_TEXT_GOLD)
        self.screen.blit(s3, (left_x, y))
        y += 20
        c_lines = [
            "Nacido del servidor de roleplay y Dungeons & Dragons",
            "que Josue fundó en 2018 bajo el alías de: Sadezu, y de su sueño",
            "de crear un videojuego estilo RPG de ese mundo."
        ]
        for cl in c_lines:
            cl_surf = self.font_small.render(cl, True, (215, 205, 225))
            self.screen.blit(cl_surf, (left_x + 12, y))
            y += 18

        right_col_x = bx + 530
        ry = by + 20

        s4 = self.font_bold.render("LA SAGA DE LA COMUNIDAD", True, COLOR_TEXT_GOLD)
        self.screen.blit(s4, (right_col_x, ry))
        ry += 22

        saga_entries = [
            ("The Abyss", "2018 - 2019"),
            ("The Exodus Chronicles", "2020 - 2024"),
            ("Soul Of Velkanor", "2024 - 2025"),
            ("The Chronicles Of Two Suns", "2026 -")
        ]
        for sname, syears in saga_entries:
            sn_surf = self.font_body.render(f"• {sname}", True, COLOR_TEXT_LIGHT)
            sy_surf = self.font_bold.render(syears, True, (255, 215, 100))
            self.screen.blit(sn_surf, (right_col_x + 12, ry))
            self.screen.blit(sy_surf, (right_col_x + 290, ry))
            ry += 22

        ry += 6
        saga_quotes = [
            "Todo lo vivido por los jugadores de las eras anteriores",
            "forma parte de la historia de este juego."
        ]
        for sq in saga_quotes:
            sq_surf = self.font_small.render(sq, True, (190, 175, 210))
            self.screen.blit(sq_surf, (right_col_x + 12, ry))
            ry += 18

        ry += 14
        s5 = self.font_bold.render("TECNOLOGÍA", True, COLOR_TEXT_GOLD)
        self.screen.blit(s5, (right_col_x, ry))
        ry += 20
        t_lines = [
            "• Programado en Python",
            "• Prototipo inicial creado con apoyo de Claude (Anthropic)"
        ]
        for tl in t_lines:
            tl_surf = self.font_body.render(tl, True, COLOR_TEXT_LIGHT)
            self.screen.blit(tl_surf, (right_col_x + 12, ry))
            ry += 20

        ry += 14
        s6 = self.font_bold.render("AGRADECIMIENTOS", True, COLOR_TEXT_GOLD)
        self.screen.blit(s6, (right_col_x, ry))
        ry += 20
        thx_lines = [
            "A cada miembro de la comunidad, de ayer y de hoy,",
            "por construir esta historia."
        ]
        for thx in thx_lines:
            thx_surf = self.font_small.render(thx, True, (225, 215, 235))
            self.screen.blit(thx_surf, (right_col_x + 12, ry))
            ry += 18

        ry += 14
        thanks_big = self.font_header.render("¡Gracias por jugar!", True, (255, 215, 80))
        self.screen.blit(thanks_big, (right_col_x + 110, ry))

        btn_back = pygame.Rect(WINDOW_WIDTH // 2 - 140, WINDOW_HEIGHT - 65, 280, 40)
        self.draw_button(btn_back, "VOLVER AL MENÚ", mouse_pos, icon_name="btn_back")

        return {'back': btn_back}

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
