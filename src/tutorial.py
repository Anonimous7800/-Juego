import math
import pygame
from src.constants import (
    N, LO, HI, WINDOW_WIDTH, WINDOW_HEIGHT,
    COLOR_BG_DARK, COLOR_PANEL_BG, COLOR_PANEL_BORDER,
    COLOR_TEXT_LIGHT, COLOR_TEXT_GOLD, COLOR_TEXT_MUTED,
    FACTIONS, ORDER, TEAM, CARDS
)

class TutorialController:
    def __init__(self, game):
        self.game = game
        self.game.is_tutorial = True
        self.step = 1
        self.completed = False
        self.anim_time = 0.0

        self.step_titles = {
            1: "PASO 1/5: MOVIMIENTO TÁCTICO",
            2: "PASO 2/5: COMBATE CUERPO A CUERPO",
            3: "PASO 3/5: LA BANDERA SAGRADA",
            4: "PASO 4/5: HECHIZOS TÁCTICOS",
            5: "PASO 5/5: DESPLIEGUE DE RESERVAS",
            6: "¡ENTRENAMIENTO COMPLETADO!"
        }

        self.step_descriptions = {
            1: "Selecciona tu Soldado Solcárdena dorado en [13,7]. Los orbes verdes marcan las casillas a las que puedes desplazarte. Haz clic en la casilla marcada [12,7] para avanzar.",
            2: "¡Excelente! Un explorador lunar Aurélion se ha posicionado en [11,7]. Selecciona tu soldado y pulsa sobre la casilla enemiga resaltada en rojo para atacarlo.",
            3: "¡Enemigo derrotado! En el centro descansa la Bandera Sagrada [10,7]. Mueve tu tropa sobre ella para capturarla. Llevarla al bastión de tu base [15,0] te dará la victoria instantánea.",
            4: "En el panel derecho tienes tu Mazo Táctico de un solo uso. Selecciona la carta 'Aura Solar' y luego haz clic sobre tu soldado para envolverlo en un Escudo Divino protector.",
            5: "Cuando sufras bajas o necesites refuerzos, usa tus Tropas en Reserva. Selecciona un Soldado en la barra de reserva y haz clic en tu zona base [14,7] para desplegarlo.",
            6: "¡Magistral, Comandante! Has dominado el movimiento, el combate, la captura de reliquias, los hechizos y el despliegue. ¡El destino de los Dos Soles está en tus manos!"
        }

        self.setup_step(1)

    def setup_step(self, step):
        self.step = step
        self.game.is_tutorial = True
        self.game.idx = 0
        self.game.human = 'S'
        self.game.ap = 2
        self.game.acted.clear()
        self.game.selected = None
        self.game.moves = []

        if step == 1:
            self.game.board = [['' for _ in range(N)] for _ in range(N)]
            self.game.place_piece('S', 13, 7, 'P')
            self.game.hp[(13, 7)] = 5
            self.game.flag = {'r': 7, 'c': 8, 'carried': False, 'by': None}
            self.hint_piece = (13, 7)
            self.hint_target = (12, 7)

        elif step == 2:
            self.game.board[13][7] = ''
            self.game.place_piece('S', 12, 7, 'P')
            self.game.hp[(12, 7)] = 5
            self.game.place_piece('A', 11, 7, 'P')
            self.game.hp[(11, 7)] = 1
            self.hint_piece = (12, 7)
            self.hint_target = (11, 7)
            self.game.audio.play_sfx("select")

        elif step == 3:
            self.game.board[12][7] = ''
            self.game.place_piece('S', 11, 7, 'P')
            self.game.hp[(11, 7)] = 5
            self.game.flag = {'r': 10, 'c': 7, 'carried': False, 'by': None}
            self.hint_piece = (11, 7)
            self.hint_target = (10, 7)
            self.game.audio.play_sfx("flag")

        elif step == 4:
            self.game.board[11][7] = ''
            self.game.place_piece('S', 10, 7, 'P')
            self.game.hp[(10, 7)] = 5
            self.game.flag = {'r': 10, 'c': 7, 'carried': True, 'by': 'S'}
            self.game.used_cards['S'].clear()
            self.game.shields.clear()
            self.hint_piece = (10, 7)
            self.hint_target = None
            self.game.audio.play_sfx("card")

        elif step == 5:
            self.game.hand_reserves['S'] = ['P', 'P']
            self.hint_piece = None
            self.hint_target = (14, 7)
            self.game.audio.play_sfx("select")

        elif step == 6:
            self.completed = True
            self.hint_piece = None
            self.hint_target = None
            self.game.missions.add_progress("tutorial_grad", 1)
            self.game.audio.play_sfx("victory")

    def update(self, dt):
        self.anim_time += dt

        if self.step == 1:
            if self.game.board[12][7] == 'S_P':
                self.game.add_floating(12, 7, "¡MOVIMIENTO COMPLETADO!", (255, 215, 0))
                self.setup_step(2)
        elif self.step == 2:
            if self.game.board[11][7] == 'S_P':
                self.game.add_floating(11, 7, "¡ENEMIGO DERROTADO!", (255, 107, 107))
                self.setup_step(3)
        elif self.step == 3:
            if self.game.is_carrier(10, 7) or (self.game.flag['carried'] and self.game.flag['by'] == 'S'):
                self.game.add_floating(10, 7, "¡BANDERA CAPTURADA!", (255, 215, 0))
                self.setup_step(4)
        elif self.step == 4:
            if 'AURA' in self.game.used_cards['S'] or len(self.game.shields) > 0:
                self.game.add_floating(10, 7, "¡ESCUDO ACTIVADO!", (0, 191, 255))
                self.setup_step(5)
        elif self.step == 5:
            if self.game.board[14][7] == 'S_P':
                self.game.add_floating(14, 7, "¡TROPAS DESPLEGADAS!", (78, 205, 145))
                self.setup_step(6)

    def on_oracle_consulted(self):
        pass

    def draw_tutorial_overlay(self, screen, ui):
        ts = ui.tile_size
        bx = ui.board_x
        by = ui.board_y

        if self.hint_piece:
            pr, pc = self.hint_piece
            px = bx + pc * ts
            py = by + pr * ts
            halo = pygame.Surface((ts, ts), pygame.SRCALPHA)
            alpha = int(140 + 90 * math.sin(self.anim_time * 5.0))
            pygame.draw.circle(halo, (255, 215, 0, alpha), (ts // 2, ts // 2), int(ts * 0.46), 3)
            screen.blit(halo, (px, py))

        if self.hint_target:
            tr, tc = self.hint_target
            tx = bx + tc * ts
            ty = by + tr * ts
            target_glow = pygame.Surface((ts, ts), pygame.SRCALPHA)
            alpha = int(120 + 90 * math.cos(self.anim_time * 5.0))
            pygame.draw.rect(target_glow, (0, 215, 255, alpha), (0, 0, ts, ts), 3, border_radius=4)
            screen.blit(target_glow, (tx, ty))

            if self.hint_piece:
                pr, pc = self.hint_piece
                fx = bx + pc * ts + ts // 2
                fy = by + pr * ts + ts // 2
                gx = tx + ts // 2
                gy = ty + ts // 2
                arrow_t = (math.sin(self.anim_time * 6.0) + 1.0) * 0.5
                curr_ax = fx + (gx - fx) * arrow_t
                curr_ay = fy + (gy - fy) * arrow_t
                pygame.draw.circle(screen, (0, 240, 255), (int(curr_ax), int(curr_ay)), 4)

        dia_w = 608
        dia_h = 76
        dx = bx
        dy = by + ui.board_size + 8

        dia_rect = pygame.Rect(dx, dy, dia_w, dia_h)
        pygame.draw.rect(screen, (20, 16, 12), dia_rect, border_radius=8)
        pygame.draw.rect(screen, (180, 140, 60), dia_rect, 2, border_radius=8)
        pygame.draw.rect(screen, (255, 215, 60), (dx, dy, 4, dia_h), border_radius=2)

        content_x = dx + 18
        step_title_str = self.step_titles.get(self.step, f"PASO {self.step}")
        title_surf = ui.font_bold.render(step_title_str, True, (255, 215, 120))
        screen.blit(title_surf, (content_x, dy + 6))

        badge_txt = ui.font_small.render("● GUÍA DE ENTRENAMIENTO", True, (78, 205, 145))
        screen.blit(badge_txt, (content_x + title_surf.get_width() + 14, dy + 8))

        active_text = self.step_descriptions.get(self.step, "")
        words = active_text.split(' ')
        lines = []
        cur_line = []
        max_text_w = dia_w - 150
        for w in words:
            test_line = " ".join(cur_line + [w])
            if ui.font_small.size(test_line)[0] > max_text_w:
                lines.append(" ".join(cur_line))
                cur_line = [w]
            else:
                cur_line.append(w)
        if cur_line:
            lines.append(" ".join(cur_line))

        for li, l_str in enumerate(lines[:2]):
            line_surf = ui.font_small.render(l_str, True, (230, 225, 215))
            screen.blit(line_surf, (content_x, dy + 30 + li * 17))

        mouse_pos = pygame.mouse.get_pos()

        btn_next = pygame.Rect(dx + dia_w - 128, dy + 18, 118, 40)
        next_hover = btn_next.collidepoint(mouse_pos)
        next_bg = (245, 205, 30) if next_hover else (195, 150, 15)
        pygame.draw.rect(screen, next_bg, btn_next, border_radius=6)
        pygame.draw.rect(screen, (255, 235, 120) if next_hover else (130, 100, 10), btn_next, 1, border_radius=6)
        btn_txt_str = "CONTINUAR" if not self.completed else "A LA GUERRA"
        btn_txt = ui.font_bold.render(btn_txt_str, True, (12, 10, 5))
        screen.blit(btn_txt, (btn_next.centerx - btn_txt.get_width() // 2, btn_next.centery - btn_txt.get_height() // 2))

        return {'next': btn_next}
