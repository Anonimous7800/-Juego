import sys
import pygame
from src.constants import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, TEAM_NAMES, TEAM, COLOR_BG_DARK
from src.settings import SettingsManager
from src.audio import AudioManager
from src.missions import MissionManager
from src.board import BoardGame
from src.ai import AIEngine
from src.ui import UIRenderer
from src.menu import MenuManager
from src.tutorial import TutorialController

STATE_MENU = "menu"
STATE_CHARACTERS = "characters"
STATE_MISSIONS = "missions"
STATE_SETTINGS = "settings"
STATE_RULES = "rules"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_TUTORIAL = "tutorial"
STATE_CREDITS = "credits"

class ConflictoDosSoles:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("☀ | Chronicles Of Two Suns T2")

        self.settings = SettingsManager()
        self.audio = AudioManager()
        self.missions = MissionManager()

        flags = pygame.DOUBLEBUF
        if self.settings.get("fullscreen", False):
            flags |= pygame.FULLSCREEN
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)
        self.clock = pygame.time.Clock()

        self.ui = UIRenderer(self.screen)
        self.menu = MenuManager(self.screen)

        self.game = None
        self.ai = None
        self.tutorial = None
        self.state = STATE_MENU
        self.ai_timer = 0.0

        self.audio.play_music("music_menu")

    def start_game(self, faction_code):
        self.game = BoardGame(human_faction=faction_code)
        self.ai = AIEngine(self.game)
        self.tutorial = None
        self.state = STATE_PLAYING
        self.ai_timer = 0.6
        self.audio.play_music("music_battle")
        self.audio.play_sfx("flag")
        self.ui.oracle.solicitar_consejo_async(self.game.get_oracle_state())

    def start_tutorial(self):
        self.game = BoardGame(human_faction='S')
        self.game.is_tutorial = True
        self.tutorial = TutorialController(self.game)
        self.ai = None
        self.state = STATE_TUTORIAL
        self.audio.play_music("music_battle")
        self.audio.play_sfx("select")

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.handle_escape()
                    elif self.state in (STATE_PLAYING, STATE_TUTORIAL) and self.game and self.game.is_human_turn():
                        if event.key == pygame.K_SPACE:
                            self.game.next_turn()
                            self.audio.play_sfx("select")
                        elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                            idx = event.key - pygame.K_1
                            from src.constants import FACTION_HANDS
                            hand = FACTION_HANDS.get(self.game.cur_code(), [])
                            if idx < len(hand):
                                cid = hand[idx]
                                if cid not in self.game.used_cards[self.game.cur_code()]:
                                    self.game.active_card = None if self.game.active_card == cid else cid
                                    self.game.deploy_index = None
                                    self.game.selected = None
                                    self.audio.play_sfx("card")
                elif event.type == pygame.MOUSEWHEEL:
                    if self.state == STATE_MISSIONS:
                        self.menu.scroll_missions(event.y * 36)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(mouse_pos)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.menu.dragging_music = False
                    self.menu.dragging_sfx = False
                elif event.type == pygame.MOUSEMOTION:
                    self.handle_mouse_drag(mouse_pos)

            self.menu.update(dt)
            if self.state == STATE_PLAYING and self.game:
                self.game.update(dt)
                self.ui.update_particles(dt)

                if not self.game.game_over and not self.game.is_human_turn() and self.ai:
                    self.ai_timer -= dt
                    if self.ai_timer <= 0:
                        self.ai.think_and_execute()
                        self.ai_timer = 0.55 if not self.settings.get("fast_ai", False) else 0.2
            elif self.state == STATE_TUTORIAL and self.game and self.tutorial:
                self.game.update(dt)
                self.tutorial.update(dt)
                self.ui.update_particles(dt)

            self.render(mouse_pos)
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def handle_escape(self):
        if self.state in (STATE_PLAYING, STATE_TUTORIAL):
            self.state = STATE_PAUSED
            self.audio.play_sfx("click")
        elif self.state == STATE_PAUSED:
            self.state = STATE_PLAYING if not self.tutorial else STATE_TUTORIAL
            self.audio.play_sfx("click")
        elif self.state in (STATE_CHARACTERS, STATE_MISSIONS, STATE_SETTINGS, STATE_RULES, STATE_CREDITS):
            self.state = STATE_MENU
            self.audio.play_sfx("click")

    def handle_mouse_drag(self, mouse_pos):
        if self.state == STATE_SETTINGS:
            if self.menu.dragging_music:
                slider_rect = pygame.Rect(WINDOW_WIDTH // 2 - 300 + 35, 120 + 35 + 36, 420, 12)
                pct = max(0.0, min(1.0, (mouse_pos[0] - slider_rect.x) / slider_rect.width))
                self.audio.set_music_volume(pct)
            elif self.menu.dragging_sfx:
                slider_rect = pygame.Rect(WINDOW_WIDTH // 2 - 300 + 35, 120 + 35 + 85 + 36, 420, 12)
                pct = max(0.0, min(1.0, (mouse_pos[0] - slider_rect.x) / slider_rect.width))
                self.audio.set_sfx_volume(pct)

    def handle_click(self, mouse_pos):
        if self.state == STATE_MENU:
            btns = self.menu.draw_main_menu(mouse_pos)
            if btns['play'].collidepoint(mouse_pos):
                self.audio.play_sfx("select")
                self.state = STATE_CHARACTERS
            elif btns['tutorial'].collidepoint(mouse_pos):
                self.audio.play_sfx("select")
                self.start_tutorial()
            elif btns['characters'].collidepoint(mouse_pos):
                self.audio.play_sfx("select")
                self.state = STATE_CHARACTERS
            elif btns['missions'].collidepoint(mouse_pos):
                self.audio.play_sfx("select")
                self.state = STATE_MISSIONS
            elif btns['settings'].collidepoint(mouse_pos):
                self.audio.play_sfx("select")
                self.state = STATE_SETTINGS
            elif btns['rules'].collidepoint(mouse_pos):
                self.audio.play_sfx("select")
                self.state = STATE_RULES
            elif btns.get('credits') and btns['credits'].collidepoint(mouse_pos):
                self.audio.play_sfx("select")
                self.state = STATE_CREDITS
            elif btns['quit'].collidepoint(mouse_pos):
                pygame.quit()
                sys.exit()

        elif self.state == STATE_CHARACTERS:
            ui = self.menu.draw_character_select(mouse_pos)
            for cid, rect in ui['chars'].items():
                if rect.collidepoint(mouse_pos):
                    self.menu.selected_character_id = cid
                    self.audio.play_sfx("select")
                    return
            if ui['start'].collidepoint(mouse_pos):
                self.start_game(self.menu.selected_character_id)
            elif ui['back'].collidepoint(mouse_pos):
                self.audio.play_sfx("click")
                self.state = STATE_MENU

        elif self.state == STATE_MISSIONS:
            ui = self.menu.draw_missions(mouse_pos)
            if ui['back'].collidepoint(mouse_pos):
                self.audio.play_sfx("click")
                self.state = STATE_MENU
            elif ui.get('scroll_up') and ui['scroll_up'].collidepoint(mouse_pos):
                self.audio.play_sfx("select")
                self.menu.scroll_missions(45)
            elif ui.get('scroll_down') and ui['scroll_down'].collidepoint(mouse_pos):
                self.audio.play_sfx("select")
                self.menu.scroll_missions(-45)

        elif self.state == STATE_SETTINGS:
            ui = self.menu.draw_settings(mouse_pos)
            if ui['slider_music'].collidepoint(mouse_pos):
                self.menu.dragging_music = True
                pct = max(0.0, min(1.0, (mouse_pos[0] - ui['slider_music'].x) / ui['slider_music'].width))
                self.audio.set_music_volume(pct)
            elif ui['slider_sfx'].collidepoint(mouse_pos):
                self.menu.dragging_sfx = True
                pct = max(0.0, min(1.0, (mouse_pos[0] - ui['slider_sfx'].x) / ui['slider_sfx'].width))
                self.audio.set_sfx_volume(pct)
            elif ui['test_sound'].collidepoint(mouse_pos):
                self.audio.play_sfx("victory")
            elif ui['diff_normal'].collidepoint(mouse_pos):
                self.settings.set("difficulty", "Normal")
                self.audio.play_sfx("click")
            elif ui['diff_hard'].collidepoint(mouse_pos):
                self.settings.set("difficulty", "Maestro")
                self.audio.play_sfx("click")
            elif ui['back'].collidepoint(mouse_pos):
                self.audio.play_sfx("click")
                self.state = STATE_MENU

        elif self.state == STATE_RULES:
            ui = self.menu.draw_rules(mouse_pos)
            if ui['back'].collidepoint(mouse_pos):
                self.audio.play_sfx("click")
                self.state = STATE_MENU

        elif self.state == STATE_CREDITS:
            ui = self.menu.draw_credits(mouse_pos)
            if ui.get('back') and ui['back'].collidepoint(mouse_pos):
                self.audio.play_sfx("click")
                self.state = STATE_MENU

        elif self.state == STATE_PAUSED:
            ui = self.menu.draw_pause_modal(mouse_pos)
            if ui['resume'].collidepoint(mouse_pos):
                self.audio.play_sfx("click")
                self.state = STATE_PLAYING if not self.tutorial else STATE_TUTORIAL
            elif ui['restart'].collidepoint(mouse_pos):
                if self.tutorial:
                    self.start_tutorial()
                else:
                    self.start_game(self.game.human)
            elif ui['quit'].collidepoint(mouse_pos):
                self.audio.play_sfx("click")
                self.state = STATE_MENU
                self.audio.play_music("music_menu")

        elif self.state in (STATE_PLAYING, STATE_TUTORIAL):
            if self.state == STATE_PLAYING and self.game.game_over:
                player_team = TEAM[self.game.human]
                if self.game.winner_team is not None and self.game.winner_team == player_team:
                    v_ui = self.menu.draw_victory_modal(TEAM_NAMES[self.game.winner_team], self.game.win_reason, mouse_pos)
                    if v_ui['replay'].collidepoint(mouse_pos):
                        self.start_game(self.game.human)
                    elif v_ui['menu'].collidepoint(mouse_pos):
                        self.state = STATE_MENU
                        self.audio.play_music("music_menu")
                    return
                else:
                    enemy = TEAM_NAMES[self.game.winner_team] if self.game.winner_team is not None else None
                    g_ui = self.menu.draw_game_over_modal(self.game.win_reason, mouse_pos, enemy_team=enemy)
                    if g_ui['retry'].collidepoint(mouse_pos):
                        self.start_game(self.game.human)
                    elif g_ui['menu'].collidepoint(mouse_pos):
                        self.state = STATE_MENU
                        self.audio.play_music("music_menu")
                    return

            if self.state == STATE_TUTORIAL and self.tutorial:
                t_ui = self.ui.draw_tutorial(self.tutorial)
                if isinstance(t_ui, dict):
                    if t_ui.get('next') and t_ui['next'].collidepoint(mouse_pos):
                        self.audio.play_sfx("select")
                        if self.tutorial.completed:
                            self.state = STATE_MENU
                            self.audio.play_music("music_menu")
                        else:
                            self.tutorial.setup_step(self.tutorial.step + 1)
                        return
                elif t_ui and t_ui.collidepoint(mouse_pos):
                    self.audio.play_sfx("select")
                    if self.tutorial.completed:
                        self.state = STATE_MENU
                        self.audio.play_music("music_menu")
                    else:
                        self.tutorial.setup_step(self.tutorial.step + 1)
                    return

            hud = self.ui.draw_hud(self.game, mouse_pos)

            if hud.get('oracle') and hud['oracle'].collidepoint(mouse_pos):
                self.audio.play_sfx("card")
                self.ui.oracle.solicitar_consejo_async(self.game.get_oracle_state())
                if self.state == STATE_TUTORIAL and self.tutorial:
                    self.tutorial.on_oracle_consulted()
                return

            if hud['end_turn'].collidepoint(mouse_pos) and self.game.is_human_turn():
                self.audio.play_sfx("select")
                self.game.next_turn()
                return
            elif hud['menu'].collidepoint(mouse_pos):
                self.audio.play_sfx("click")
                self.state = STATE_PAUSED
                return

            for cb_rect, cid in hud['cards']:
                if cb_rect.collidepoint(mouse_pos) and self.game.is_human_turn():
                    if cid not in self.game.used_cards[self.game.cur_code()]:
                        self.game.active_card = None if self.game.active_card == cid else cid
                        self.game.deploy_index = None
                        self.game.selected = None
                        self.audio.play_sfx("card")
                    return

            for d_rect, di in hud['deploy']:
                if d_rect.collidepoint(mouse_pos) and self.game.is_human_turn():
                    self.game.deploy_index = None if self.game.deploy_index == di else di
                    self.game.active_card = None
                    self.game.selected = None
                    self.audio.play_sfx("select")
                    return

            if self.game.is_human_turn():
                hovered = self.ui.get_tile_at(mouse_pos)
                if hovered:
                    r, c = hovered
                    self.handle_tile_click(r, c)

    def handle_tile_click(self, r, c):
        if self.game.deploy_index is not None:
            if self.game.is_free(r, c) and self.game.home_zone(self.game.cur_code(), r, c):
                self.game.deploy_reserve(r, c)
            return

        if self.game.active_card:
            self.game.use_card(r, c)
            return

        val = self.game.board[r][c]
        p = self.game.cur_code()

        if self.game.is_own(val, p):
            if (r, c) in self.game.acted and self.state != STATE_TUTORIAL:
                self.game.add_floating(r, c, "¡Ya actuó este turno!", (200, 150, 100))
                return
            if (r, c) in self.game.frozen and self.game.frozen[(r, c)]['active']:
                self.game.add_floating(r, c, "¡Inmovilizado!", (180, 180, 180))
                return
            self.game.selected = (r, c)
            self.game.moves = self.game.calc_moves(r, c, val)
            self.audio.play_sfx("select")
            return

        if self.game.selected and (r, c) in self.game.moves:
            fr, fc = self.game.selected
            if self.game.board[r][c] and self.game.board[r][c] != 'BLOCKED':
                self.game.attack(fr, fc, r, c)
            else:
                self.game.move_piece(fr, fc, r, c)
                self.audio.play_sfx("move")

            if self.state != STATE_TUTORIAL:
                self.game.acted.add((fr, fc))
                self.game.acted.add((r, c))
            self.game.selected = None
            self.game.moves = []
            self.game.spend_ap(1)

    def render(self, mouse_pos):
        self.screen.fill(COLOR_BG_DARK)

        if self.state == STATE_MENU:
            self.menu.draw_main_menu(mouse_pos)
        elif self.state == STATE_CHARACTERS:
            self.menu.draw_character_select(mouse_pos)
        elif self.state == STATE_MISSIONS:
            self.menu.draw_missions(mouse_pos)
        elif self.state == STATE_SETTINGS:
            self.menu.draw_settings(mouse_pos)
        elif self.state == STATE_RULES:
            self.menu.draw_rules(mouse_pos)
        elif self.state == STATE_CREDITS:
            self.menu.draw_credits(mouse_pos)
        elif self.state in (STATE_PLAYING, STATE_PAUSED, STATE_TUTORIAL):
            if self.game:
                self.ui.draw_board(self.game, mouse_pos)
                self.ui.draw_hud(self.game, mouse_pos)
                self.ui.draw_particles()
                self.ui.draw_floating_popups(self.game)

                if self.state == STATE_TUTORIAL and self.tutorial:
                    self.ui.draw_tutorial(self.tutorial)

                if self.state == STATE_PAUSED:
                    self.menu.draw_pause_modal(mouse_pos)
                elif self.game.game_over and self.state == STATE_PLAYING:
                    player_team = TEAM[self.game.human]
                    if self.game.winner_team is not None and self.game.winner_team == player_team:
                        self.menu.draw_victory_modal(TEAM_NAMES[self.game.winner_team], self.game.win_reason, mouse_pos)
                    elif self.game.winner_team is not None and self.game.winner_team != player_team:
                        self.menu.draw_game_over_modal(self.game.win_reason, mouse_pos, enemy_team=TEAM_NAMES[self.game.winner_team])
                    else:
                        self.menu.draw_game_over_modal(self.game.win_reason, mouse_pos)

if __name__ == "__main__":
    game_app = ConflictoDosSoles()
    game_app.run()
