import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame

from src.constants import ORDER, FACTIONS, TEAM, UNIT_COST, N
from src.board import BoardGame
from src.ai import AIEngine
from src.tutorial import TutorialController
from src.menu import MenuManager
from main import ConflictoDosSoles, STATE_MENU, STATE_SETTINGS, STATE_RULES, STATE_CREDITS, STATE_MULTIPLAYER

try:
    import pytest
    @pytest.fixture(scope="module", autouse=True)
    def init_pygame():
        pygame.init()
        pygame.display.set_mode((1280, 720))
        yield
        pygame.quit()
except ImportError:
    pygame.init()
    pygame.display.set_mode((1280, 720))

def test_constants():
    assert len(ORDER) == 4
    for k in ORDER:
        assert k in FACTIONS
        assert 'code' in FACTIONS[k]
        code = FACTIONS[k]['code']
        assert code in TEAM
    assert UNIT_COST['P'] == 1
    assert UNIT_COST['Q'] == 2

def test_board_game_init():
    game = BoardGame(human_faction='S')
    assert game.cur_code() == 'S'
    assert game.is_human_turn() is True
    assert game.ap == 2
    assert game.game_over is False
    assert len(game.board) == N
    assert len(game.board[0]) == N

def test_board_multiplayer_turns():
    game = BoardGame(human_faction=['S', 'A'])
    assert game.cur_code() == 'S'
    assert game.is_human_turn() is True

    game.next_turn()
    assert game.cur_code() == 'A'
    assert game.is_human_turn() is True

    game.next_turn()
    assert game.cur_code() == 'J'
    assert game.is_human_turn() is False

    game.next_turn()
    assert game.cur_code() == 'K'
    assert game.is_human_turn() is False

def test_board_moves_and_actions():
    game = BoardGame(human_faction=['S', 'J'])
    game.place_piece('S', 5, 5, 'P')
    moves = game.calc_moves(5, 5, 'S_P')
    assert isinstance(moves, list)
    game.spend_ap(1)
    assert game.ap == 1

def test_ai_think():
    game = BoardGame(human_faction='S')
    game.next_turn()
    assert game.is_human_turn() is False
    ai = AIEngine(game)
    ai.think_and_execute()

def test_menu_navigation():
    surf = pygame.Surface((1280, 720))
    menu = MenuManager(surf)
    btns = menu.draw_main_menu((100, 100))
    assert 'play' in btns
    assert 'tutorial' in btns
    assert 'multiplayer' in btns
    assert 'settings' in btns
    assert 'rules' in btns
    assert 'credits' in btns
    assert 'quit' in btns

    menu.set_mp_preset('4p')
    assert all(m == 'human' for m in menu.mp_slots.values())
    menu.toggle_mp_slot('S')
    assert menu.mp_slots['S'] == 'ai'

def test_tutorial_controller():
    game = BoardGame(human_faction='S')
    game.is_tutorial = True
    tutorial = TutorialController(game)
    assert tutorial.step == 1
    tutorial.update(0.1)

def test_app_state_flow():
    app = ConflictoDosSoles()
    assert app.state == STATE_MENU

    btns = app.menu.draw_main_menu((100, 100))
    app.handle_click(btns['settings'].center)
    assert app.state == STATE_SETTINGS
    app.handle_escape()
    assert app.state == STATE_MENU

    btns = app.menu.draw_main_menu((100, 100))
    app.handle_click(btns['rules'].center)
    assert app.state == STATE_RULES
    app.handle_escape()
    assert app.state == STATE_MENU

    btns = app.menu.draw_main_menu((100, 100))
    app.handle_click(btns['credits'].center)
    assert app.state == STATE_CREDITS
    app.handle_escape()
    assert app.state == STATE_MENU

    btns = app.menu.draw_main_menu((100, 100))
    app.handle_click(btns['multiplayer'].center)
    assert app.state == STATE_MULTIPLAYER
