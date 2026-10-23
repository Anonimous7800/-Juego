import random
from src.constants import (
    N, LO, HI, FACTIONS, ORDER, TEAM, TEAM_NAMES,
    ATK, MAX_HP, UNIT_COST, UNIT_NAMES, FWD, ALL_DIRS, KNIGHT_JUMPS,
    CARDS, FACTION_HANDS, MAX_LIVES, INIT_LIVES
)
from src.characters import CHARACTERS
from src.audio import AudioManager
from src.missions import MissionManager

class BoardGame:
    def __init__(self, human_faction='S'):
        self.audio = AudioManager()
        self.missions = MissionManager()
        if isinstance(human_faction, (list, tuple, set)):
            self.human_factions = set(human_faction)
            self.human = next(iter(self.human_factions)) if self.human_factions else 'S'
        else:
            self.human_factions = {human_faction}
            self.human = human_faction
        self.character = CHARACTERS.get(self.human, CHARACTERS['S'])

        self.board = [['' for _ in range(N)] for _ in range(N)]
        self.special = [['' for _ in range(N)] for _ in range(N)]
        self.hp = {}
        self.shields = {}
        self.frozen = {}
        self.ranged = {}
        self.acted = set()

        is_single_human = len(self.human_factions) == 1
        self.lives = {
            'S': INIT_LIVES + (1 if ('S' in self.human_factions and is_single_human) else 0),
            'A': INIT_LIVES + (1 if ('A' in self.human_factions and is_single_human) else 0),
            'J': INIT_LIVES + (1 if ('J' in self.human_factions and is_single_human) else 0),
            'K': INIT_LIVES + (1 if ('K' in self.human_factions and is_single_human) else 0)
        }
        self.pawn_deaths = {'S': 0, 'A': 0, 'J': 0, 'K': 0}
        self.eliminated = set()

        self.idx = 0
        self.turn_count = 0
        self.ap = 2
        self.game_over = False
        self.winner_team = None
        self.win_reason = ""

        self.selected = None
        self.moves = []
        self.active_card = None
        self.deploy_index = None

        self.used_cards = {p: set() for p in ['S', 'A', 'J', 'K']}
        self.hand_reserves = {p: ['P', 'P'] for p in ['S', 'A', 'J', 'K']}

        self.flag = {'r': 7, 'c': 8, 'carried': False, 'by': None}

        self.log_messages = []
        self.floating_popups = []
        self.hit_effects = []
        self.move_animations = []
        self.vfx_events = []

        self.setup_board()
        self.gen_specials()
        self.log("¡La Guerra de los Dos Soles ha comenzado! Bandera lista en el centro [7,8].")

    def cur_faction(self):
        return ORDER[self.idx]

    def cur_code(self):
        return FACTIONS[self.cur_faction()]['code']

    def get_character(self, code):
        return CHARACTERS.get(code, CHARACTERS.get(self.human, CHARACTERS['S']))

    def is_human_turn(self):
        return not self.game_over and self.cur_code() in self.human_factions

    def log(self, msg):
        self.log_messages.append(msg)
        if len(self.log_messages) > 100:
            self.log_messages.pop(0)

    def add_floating(self, r, c, text, color=(255, 215, 0)):
        self.floating_popups.append({
            'r': r,
            'c': c,
            'text': text,
            'color': color,
            'time': 1.2,
            'y_offset': 0.0
        })

    def is_in_grid(self, r, c):
        return 0 <= r < N and 0 <= c < N and self.board[r][c] is not None

    def is_free(self, r, c):
        return self.is_in_grid(r, c) and self.board[r][c] == ''

    def in_center(self, r, c):
        return LO <= r <= HI and LO <= c <= HI

    def is_corner(self, r, c):
        return (r == 0 and c == N - 1) or (r == N - 1 and c == 0)

    def on_goal(self, p, r, c):
        if TEAM[p] == 1:
            return r == N - 1 and c == 0
        else:
            return r == 0 and c == N - 1

    def is_carrier(self, r, c):
        return self.flag['carried'] and self.flag['r'] == r and self.flag['c'] == c

    def is_own(self, val, p):
        return bool(val and val != 'BLOCKED' and val.startswith(p + '_'))

    def home_zone(self, p, r, c):
        if p == 'S': return r >= N - 2 and c < N // 2
        if p == 'A': return r <= 1 and c >= N // 2
        if p == 'J': return c <= 1 and r >= N // 2
        if p == 'K': return c >= N - 2 and r < N // 2
        return False

    def setup_board(self):
        back = ['R', 'N', 'K', 'Q', 'B']
        for i, t in enumerate(back):
            self.place_piece('S', 15, 3 + i, t)
            self.place_piece('J', 8 + i, 0, t)
            self.place_piece('A', 0, 12 - i, t)
            self.place_piece('K', 7 - i, 15, t)

        for i in range(4):
            self.place_piece('S', 14, 3 + i, 'P')
            self.place_piece('J', 8 + i, 1, 'P')
            self.place_piece('A', 1, 12 - i, 'P')
            self.place_piece('K', 7 - i, 14, 'P')

    def place_piece(self, p, r, c, t='P'):
        self.board[r][c] = f"{p}_{t}"
        base_hp = MAX_HP[t]
        if p in self.human_factions and t == 'P' and self.get_character(p).get('extra_pawn_hp', 0):
            base_hp += self.get_character(p)['extra_pawn_hp']
        self.hp[(r, c)] = base_hp

    def count_specials(self, t):
        cnt = 0
        for r in range(N):
            for c in range(N):
                if self.special[r][c] == t:
                    cnt += 1
        return cnt

    def gen_specials(self):
        for r in range(N):
            for c in range(N):
                self.special[r][c] = ''
        valid = []
        for r in range(1, N - 1):
            for c in range(1, N - 1):
                if self.board[r][c] == '' and not self.is_corner(r, c) and not (r == self.flag['r'] and c == self.flag['c']):
                    valid.append((r, c))
        random.shuffle(valid)
        items = ['H']*5 + ['I']*4 + ['X']*3 + ['T']*2
        for it in items:
            if valid:
                r, c = valid.pop()
                self.special[r][c] = it

    def spawn_single_special(self, t, notify=False):
        valid = []
        for r in range(1, N - 1):
            for c in range(1, N - 1):
                if self.board[r][c] == '' and not self.special[r][c] and not self.is_corner(r, c) and not (r == self.flag['r'] and c == self.flag['c']):
                    valid.append((r, c))
        if valid:
            r, c = random.choice(valid)
            self.special[r][c] = t
            if notify:
                names = {'H': 'Vida ❤️', 'I': 'Rayo ⚡', 'X': 'Trampa ☠', 'T': 'Portal 🌀'}
                self.add_floating(r, c, f"¡{names.get(t, 'Item')}!", (255, 215, 0))
                self.log(f"✨ ¡Ha aparecido {names.get(t, t)} en el mapa [{r},{c}]!")
                self.audio.play_sfx('card')
            return (r, c)
        return None

    def calc_moves(self, r, c, piece):
        p, utype = piece.split('_')
        out = []
        boost = 1 if (r, c) in self.ranged else 0

        def is_foe(a, b):
            if not self.is_in_grid(a, b): return False
            val = self.board[a][b]
            return val != '' and val != 'BLOCKED' and TEAM[val[0]] != TEAM[p] and (a, b) not in self.shields

        def slide(dirs, max_dist):
            for dr, dc in dirs:
                for k in range(1, max_dist + 1):
                    a, b = r + dr * k, c + dc * k
                    if self.is_free(a, b):
                        out.append((a, b))
                        continue
                    if is_foe(a, b):
                        out.append((a, b))
                    break

        def is_ally(a, b):
            if not self.is_in_grid(a, b): return False
            val = self.board[a][b]
            return val != '' and val != 'BLOCKED' and TEAM[val[0]] == TEAM[p]

        carrier = self.is_carrier(r, c)
        if utype == 'P' and not carrier:
            dr, dc = FWD[p]
            for k in range(1, 3 + boost):
                a, b = r + dr * k, c + dc * k
                if self.is_free(a, b):
                    out.append((a, b))
                else:
                    break
            for x, y in ALL_DIRS:
                a, b = r + x, c + y
                if is_foe(a, b):
                    out.append((a, b))
                elif self.is_free(a, b) and not (x == dr and y == dc):
                    out.append((a, b))
        elif utype == 'N':
            for dr, dc in KNIGHT_JUMPS:
                a, b = r + dr, c + dc
                if self.is_free(a, b) or is_foe(a, b):
                    out.append((a, b))
            if boost:
                slide(ALL_DIRS, 1)
        elif utype == 'R':
            slide(ALL_DIRS[:4], 6 + boost)
        elif utype == 'B':
            slide(ALL_DIRS[4:], 5 + boost)
        elif utype == 'Q':
            slide(ALL_DIRS, 6 + boost)
        else:
            slide(ALL_DIRS, 2 + boost)

        if carrier or any(self.is_carrier(r + dr, c + dc) for dr, dc in ALL_DIRS if self.is_in_grid(r + dr, c + dc)):
            for dr, dc in ALL_DIRS:
                a, b = r + dr, c + dc
                if is_ally(a, b):
                    if (a, b) not in out:
                        out.append((a, b))

        if carrier:
            out = [m for m in out if max(abs(r - m[0]), abs(c - m[1])) <= 2]
        return out

    def swap_pieces(self, r1, c1, r2, c2):
        piece1 = self.board[r1][c1]
        piece2 = self.board[r2][c2]
        if not piece1 or not piece2 or piece1 == 'BLOCKED' or piece2 == 'BLOCKED':
            return
        c1_carrier = self.is_carrier(r1, c1)
        c2_carrier = self.is_carrier(r2, c2)

        self.board[r1][c1] = piece2
        self.board[r2][c2] = piece1

        hp1 = self.hp.pop((r1, c1), MAX_HP[piece1[2]])
        hp2 = self.hp.pop((r2, c2), MAX_HP[piece2[2]])
        self.hp[(r1, c1)] = hp2
        self.hp[(r2, c2)] = hp1

        s1 = self.shields.pop((r1, c1), None)
        s2 = self.shields.pop((r2, c2), None)
        if s1: self.shields[(r2, c2)] = s1
        if s2: self.shields[(r1, c1)] = s2

        f1 = self.frozen.pop((r1, c1), None)
        f2 = self.frozen.pop((r2, c2), None)
        if f1: self.frozen[(r2, c2)] = f1
        if f2: self.frozen[(r1, c1)] = f2

        rg1 = self.ranged.pop((r1, c1), None)
        rg2 = self.ranged.pop((r2, c2), None)
        if rg1: self.ranged[(r2, c2)] = rg1
        if rg2: self.ranged[(r1, c1)] = rg2

        if c1_carrier:
            self.flag['r'] = r2
            self.flag['c'] = c2
        elif c2_carrier:
            self.flag['r'] = r1
            self.flag['c'] = c1

        self.move_animations.append({
            'piece': piece1, 'fr': r1, 'fc': c1, 'tr': r2, 'tc': c2,
            'time': 0.0, 'duration': 0.22, 'carrier': c1_carrier
        })
        self.move_animations.append({
            'piece': piece2, 'fr': r2, 'fc': c2, 'tr': r1, 'tc': c1,
            'time': 0.0, 'duration': 0.22, 'carrier': c2_carrier
        })

        self.add_floating(r2, c2, "¡DAR PASO! 🏃", (78, 205, 145))
        self.log(f"🔄 ¡{UNIT_NAMES[piece2[2]]} da paso a {UNIT_NAMES[piece1[2]]}!")

        if self.flag['carried']:
            cr, cc = self.flag['r'], self.flag['c']
            if self.on_goal(self.flag['by'], cr, cc):
                self.trigger_win(TEAM[self.flag['by']], "¡Llevaron la bandera sagrada al bastión de su base 🏳️!")

    def move_piece(self, fr, fc, r, c, by_card=False):
        piece = self.board[fr][fc]
        if not piece or piece == 'BLOCKED':
            return
        p = piece[0]
        was_carrier = self.is_carrier(fr, fc)

        self.ranged.pop((fr, fc), None)
        self.ranged.pop((r, c), None)
        self.frozen.pop((r, c), None)

        if (fr, fc) in self.hp:
            self.hp[(r, c)] = self.hp.pop((fr, fc))
        if (fr, fc) in self.shields:
            self.shields[(r, c)] = self.shields.pop((fr, fc))

        self.board[r][c] = piece
        self.board[fr][fc] = ''

        self.move_animations.append({
            'piece': piece,
            'fr': fr,
            'fc': fc,
            'tr': r,
            'tc': c,
            'time': 0.0,
            'duration': 0.22,
            'carrier': was_carrier
        })

        if was_carrier:
            self.flag['r'] = r
            self.flag['c'] = c
        elif self.flag['r'] == r and self.flag['c'] == c:
            self.flag['carried'] = True
            self.flag['by'] = p
            self.audio.play_sfx('flag')
            self.vfx_events.append({'type': 'flag_pickup', 'r': r, 'c': c, 'p': p})
            self.vfx_events.append({'type': 'shake', 'trauma': 4.0})
            self.log(f"🚩 ¡{FACTIONS[ORDER[self.idx]]['name']} ha tomado la bandera sagrada!")
            self.add_floating(r, c, "¡BANDERA CAPTURADA!", (255, 215, 0))
            if p in self.human_factions:
                self.missions.add_progress("flag_bearer", 1)

        sp = self.special[r][c]
        if not by_card and sp and not self.game_over:
            if sp == 'H':
                cur_l = self.lives[p]
                if cur_l < MAX_LIVES:
                    self.lives[p] += 1
                cur_hp = self.hp.get((r, c), 1)
                self.hp[(r, c)] = min(MAX_HP[piece[2]], cur_hp + 2)
                self.audio.play_sfx('life')
                self.vfx_events.append({'type': 'pickup_special', 'r': r, 'c': c, 'sp': 'H'})
                self.add_floating(r, c, "+1 ❤️ VIDA (+2 HP)", (255, 50, 100))
                self.log(f"💖 ¡{FACTIONS[ORDER[self.idx]]['name']} recogió Esencia de Vida! (+1 Vida: {self.lives[p]}/{MAX_LIVES})")
                self.special[r][c] = ''
                if p in self.human_factions:
                    self.missions.add_progress("heart_collector", 1)
            elif sp == 'I':
                self.ranged[(r, c)] = 1
                self.audio.play_sfx('card')
                self.vfx_events.append({'type': 'pickup_special', 'r': r, 'c': c, 'sp': 'I'})
                self.add_floating(r, c, "⚡ +1 ALCANCE", (255, 200, 0))
                self.log(f"⚡ ¡{FACTIONS[ORDER[self.idx]]['name']} recogió Impulso Táctico (+1 Alcance)!")
                self.special[r][c] = ''
            elif sp == 'X':
                if p in self.human_factions and self.get_character(p).get('trap_immune', False):
                    self.add_floating(r, c, "¡INMUNE A TRAMPA!", (78, 205, 145))
                    self.log(f"🛡️ Paso Sombrío: ¡{self.get_character(p)['name']} anuló la trampa mortal!")
                else:
                    self.frozen[(r, c)] = {'p': p, 'active': False}
                    self.audio.play_sfx('trap')
                    self.vfx_events.append({'type': 'pickup_special', 'r': r, 'c': c, 'sp': 'X'})
                    self.vfx_events.append({'type': 'shake', 'trauma': 5.0})
                    self.add_floating(r, c, "☠ TRAMPA -1 VIDA", (255, 40, 40))
                    self.lose_life(p, "pisar trampa mortal")
                self.special[r][c] = ''
            elif sp == 'T' and not was_carrier:
                rim = []
                for a in range(N):
                    for b in range(N):
                        if (a == 0 or b == 0 or a == N - 1 or b == N - 1) and self.board[a][b] == '':
                            rim.append((a, b))
                if rim:
                    tr, tc = random.choice(rim)
                    self.board[tr][tc] = piece
                    self.board[r][c] = ''
                    self.hp[(tr, tc)] = self.hp.pop((r, c), MAX_HP[piece[2]])
                    if (r, c) in self.shields:
                        self.shields[(tr, tc)] = self.shields.pop((r, c))
                    self.audio.play_sfx('portal')
                    self.vfx_events.append({'type': 'teleport_burst', 'r': tr, 'c': tc})
                    self.add_floating(tr, tc, "🌀 VÓRTICE", (56, 189, 248))
                    self.log(f"🌀 ¡Vórtice dimensional teletransportó la tropa a [{tr},{tc}]!")

        if self.flag['carried'] and was_carrier and self.on_goal(self.flag['by'], self.flag['r'], self.flag['c']):
            self.trigger_win(TEAM[self.flag['by']], "¡Llevaron la bandera sagrada al bastión de su base 🏳️!")

    def attack(self, fr, fc, tr, tc):
        att_piece = self.board[fr][fc]
        def_piece = self.board[tr][tc]
        if not att_piece or not def_piece or att_piece == 'BLOCKED' or def_piece == 'BLOCKED':
            return
        p_att = att_piece[0]
        p_def = def_piece[0]

        att_power = ATK[att_piece[2]]
        self.hit_effects.append((tr, tc, 0.35))
        self.vfx_events.append({'type': 'slash', 'fr': fr, 'fc': fc, 'tr': tr, 'tc': tc, 'p': p_att})
        self.vfx_events.append({'type': 'impact', 'r': tr, 'c': tc, 'p': p_att, 'power': att_power})
        self.vfx_events.append({'type': 'shake', 'trauma': 3.5})

        self.hp[(tr, tc)] = self.hp.get((tr, tc), 1) - att_power
        self.audio.play_sfx('attack')
        self.add_floating(tr, tc, f"-{att_power} HP", (255, 80, 80))
        self.log(f"⚔️ {UNIT_NAMES[att_piece[2]]} ataca a {UNIT_NAMES[def_piece[2]]} (-{att_power} HP)")

        if self.hp[(tr, tc)] <= 0:
            self.audio.play_sfx('death')
            self.vfx_events.append({'type': 'death_burst', 'r': tr, 'c': tc, 'p': p_def})
            self.vfx_events.append({'type': 'shake', 'trauma': 6.0})
            self.log(f"☠️ {UNIT_NAMES[def_piece[2]]} ha sido destruido en batalla.")
            self.handle_piece_loss(p_def, def_piece[2])

            if p_att in self.human_factions:
                self.missions.add_progress("first_blood", 1)
                if def_piece[2] == 'K':
                    self.missions.add_progress("general_slayer", 1)
                if self.get_character(p_att).get('kill_ap_bonus', 0):
                    self.ap += self.get_character(p_att)['kill_ap_bonus']
                    self.add_floating(fr, fc, "+1 PA FURIA", (255, 107, 107))

            if random.random() < 0.50:
                loot = 'H' if random.random() < 0.65 else 'I'
                self.spawn_single_special(loot, notify=True)

            self.move_piece(fr, fc, tr, tc)
            return

        def_power = ATK[def_piece[2]]
        self.hit_effects.append((fr, fc, 0.35))
        self.vfx_events.append({'type': 'slash', 'fr': tr, 'fc': tc, 'tr': fr, 'tc': fc, 'p': p_def})
        self.vfx_events.append({'type': 'impact', 'r': fr, 'c': fc, 'p': p_def, 'power': def_power})
        self.vfx_events.append({'type': 'shake', 'trauma': 3.5})

        self.hp[(fr, fc)] = self.hp.get((fr, fc), 1) - def_power
        self.add_floating(fr, fc, f"-{def_power} HP", (255, 150, 50))
        self.log(f"🛡️ {UNIT_NAMES[def_piece[2]]} contraataca (-{def_power} HP)")

        if self.hp[(fr, fc)] <= 0:
            self.audio.play_sfx('death')
            self.vfx_events.append({'type': 'death_burst', 'r': fr, 'c': fc, 'p': p_att})
            self.vfx_events.append({'type': 'shake', 'trauma': 6.0})
            self.log(f"☠️ {UNIT_NAMES[att_piece[2]]} cayó en el contraataque.")
            self.handle_piece_loss(p_att, att_piece[2])
            self.board[fr][fc] = ''
            self.hp.pop((fr, fc), None)
            self.shields.pop((fr, fc), None)
            if self.is_carrier(fr, fc):
                self.flag['carried'] = False

    def handle_piece_loss(self, p, utype):
        if utype == 'K':
            self.eliminate(p, "su General Supremo ha caído en combate")
            return
        if utype == 'P':
            self.pawn_deaths[p] = self.pawn_deaths.get(p, 0) + 1
            if self.pawn_deaths[p] % 2 == 0:
                self.lose_life(p, "caída de 2 soldados en el frente")
            else:
                self.log(f"⚠️ Soldado de {FACTIONS[ORDER[self.idx]]['name']} abatido (1/2 para perder Vida).")
        else:
            self.lose_life(p, f"pérdida de {UNIT_NAMES[utype]}")

    def lose_life(self, p, reason):
        if self.lives[p] > 0:
            self.lives[p] -= 1
            self.audio.play_sfx('death')
            self.vfx_events.append({'type': 'shake', 'trauma': 4.5})
            self.log(f"💔 Comandante pierde 1 Vida ({reason}). Vidas restantes: {self.lives[p]}/{MAX_LIVES}")
            if self.lives[p] <= 0:
                self.eliminate(p, f"agotó todas sus Vidas de Comandante ({reason})")

    def eliminate(self, p, why="ha caído"):
        faction_key = None
        for k in ORDER:
            if FACTIONS[k]['code'] == p:
                faction_key = k
                break
        if not faction_key or faction_key in self.eliminated:
            return
        self.eliminated.add(faction_key)

        for r in range(N):
            for c in range(N):
                if self.is_own(self.board[r][c], p):
                    self.board[r][c] = ''
                    self.hp.pop((r, c), None)
                    self.shields.pop((r, c), None)
                    self.ranged.pop((r, c), None)
                    self.frozen.pop((r, c), None)

        if self.flag['by'] == p:
            self.flag['carried'] = False

        self.audio.play_sfx('death')
        self.vfx_events.append({'type': 'shake', 'trauma': 6.0})
        self.add_floating(7, 7, f"💀 ¡{FACTIONS[faction_key]['name']} ELIMINADO!", (255, 50, 50))
        self.log(f"💀 ¡ELIMINADO! {FACTIONS[faction_key]['name']} ha sido destruido ({why}).")

        if p in self.human_factions and len(self.human_factions) <= 1:
            self.trigger_game_over(f"Tu facción ha caído: {why}")
            return

        alive = [k for k in ORDER if k not in self.eliminated]
        alive_teams = set(TEAM[FACTIONS[k]['code']] for k in alive)
        if len(alive_teams) == 1:
            winning_t = next(iter(alive_teams))
            self.trigger_win(winning_t, "¡Todos los comandantes enemigos han sido eliminados!")

    def trigger_win(self, winning_team, reason):
        if self.game_over: return
        self.game_over = True
        self.winner_team = winning_team
        self.win_reason = reason
        human_teams = set(TEAM[f] for f in self.human_factions)
        is_multiplayer = len(self.human_factions) > 1

        if is_multiplayer or (winning_team in human_teams):
            self.audio.play_sfx('victory')
            self.vfx_events.append({'type': 'victory_burst', 'team': winning_team})
            self.vfx_events.append({'type': 'shake', 'trauma': 8.0})
            self.log(f"🏆 ¡VICTORIA! {TEAM_NAMES[winning_team]} {reason}")
            if self.lives.get(self.human, 0) >= 4:
                self.missions.add_progress("flawless_victory", 1)
        else:
            self.audio.play_sfx('gameover')
            self.vfx_events.append({'type': 'shake', 'trauma': 6.0})
            self.log(f"💀 GAME OVER · PERDISTE: {TEAM_NAMES[winning_team]} se alzó con la victoria. {reason}")

    def trigger_game_over(self, reason):
        if self.game_over: return
        self.game_over = True
        self.win_reason = reason
        self.audio.play_sfx('gameover')
        self.log(f"💀 DERROTA: {reason}")

    def next_turn(self):
        self.selected = None
        self.moves = []
        self.ap = 2
        self.acted.clear()
        self.deploy_index = None
        self.active_card = None

        if self.game_over: return

        while True:
            self.idx = (self.idx + 1) % 4
            if ORDER[self.idx] not in self.eliminated:
                break

        self.turn_count += 1
        cur = self.cur_code()

        to_del_shields = [k for k, v in self.shields.items() if v == cur]
        for k in to_del_shields:
            del self.shields[k]

        to_del_frozen = []
        for k, v in self.frozen.items():
            if v['p'] == cur and v['active']:
                to_del_frozen.append(k)
            elif v['p'] == cur:
                v['active'] = True
        for k in to_del_frozen:
            del self.frozen[k]

        heal_amt = 1 + (1 if cur in self.human_factions and self.get_character(cur).get('medic_bonus', 0) else 0)
        for r in range(N):
            for c in range(N):
                val = self.board[r][c]
                if self.is_own(val, cur) and val[2] == 'B':
                    for dr, dc in ALL_DIRS:
                        a, b = r + dr, c + dc
                        if self.is_in_grid(a, b) and self.board[a][b] and self.board[a][b] != 'BLOCKED':
                            if TEAM[self.board[a][b][0]] == TEAM[cur]:
                                max_h = MAX_HP[self.board[a][b][2]]
                                self.hp[(a, b)] = min(max_h, self.hp.get((a, b), 1) + heal_amt)

        if self.turn_count % 10 == 0:
            self.gen_specials()
            self.log("🌪️ ¡Objetos y Vidas sagradas se han redistribuido por el mapa!")
        elif self.count_specials('H') < 4 and self.turn_count % 2 == 0:
            self.spawn_single_special('H')

    def spend_ap(self, amount=1):
        self.ap -= amount
        if self.ap <= 0 and not self.game_over:
            if getattr(self, 'is_tutorial', False):
                self.ap = 2
                self.acted.clear()
            else:
                self.next_turn()

    def ok_card_target(self, card_id, r, c):
        if not self.is_in_grid(r, c): return False
        val = self.board[r][c]
        p = self.cur_code()
        mine = self.is_own(val, p)
        foe = val != '' and val != 'BLOCKED' and TEAM[val[0]] != TEAM[p]
        pawn = val.endswith('_P')
        sel = self.selected

        if card_id == 'MARCHA':
            dr, dc = FWD[p]
            if not sel: return mine and pawn and self.is_free(r + dr, c + dc)
            a, b = sel
            n = (r - a) * dr if dr else (c - b) * dc
            if not (c == b if dr else r == a) or n < 1 or n > 6: return False
            for i in range(1, n + 1):
                if not self.is_free(a + dr * i, b + dc * i): return False
            return True
        elif card_id == 'AURA':
            return mine
        elif card_id == 'IMPACTO':
            return val == '' and not self.is_corner(r, c) and not (self.flag['r'] == r and self.flag['c'] == c)
        elif card_id == 'TRANSMUTA':
            return mine and (not (sel[0] == r and sel[1] == c) if sel else pawn)
        elif card_id == 'RECLUTA':
            return val == '' and self.home_zone(p, r, c) and not (self.flag['r'] == r and self.flag['c'] == c)
        elif card_id == 'ASCENSO':
            return mine and pawn
        elif card_id == 'CENIZA':
            return foe and pawn and (r, c) not in self.shields
        elif card_id == 'GRILLETE':
            return foe and not val.endswith('_K') and (r, c) not in self.shields
        elif card_id == 'VIENTO':
            dist = max(abs(r - self.flag['r']), abs(c - self.flag['c']))
            return val == '' and not self.flag['carried'] and dist <= 3 and not self.is_corner(r, c)
        elif card_id == 'EMBOSCADA':
            return val == '' and not self.special[r][c] and not self.is_corner(r, c) and not (self.flag['r'] == r and self.flag['c'] == c)
        elif card_id == 'HURTO':
            dist = max(abs(r - self.flag['r']), abs(c - self.flag['c']))
            return mine and self.flag['carried'] and TEAM[self.flag['by']] != TEAM[p] and dist == 1
        elif card_id == 'PORTAL':
            return (val == '' and self.in_center(r, c) and not (self.flag['r'] == r and self.flag['c'] == c)) if sel else (mine and not val.endswith('_K') and not self.is_carrier(r, c))
        return False

    def use_card(self, r, c):
        cid = self.active_card
        p = self.cur_code()
        if not self.ok_card_target(cid, r, c): return

        if cid in ('MARCHA', 'TRANSMUTA', 'PORTAL') and not self.selected:
            self.selected = (r, c)
            return

        a, b = self.selected if self.selected else (None, None)
        d = self.board[r][c]

        if cid in ('MARCHA', 'PORTAL'):
            self.move_piece(a, b, r, c, by_card=True)
        elif cid == 'AURA':
            self.shields[(r, c)] = p
            self.add_floating(r, c, "🛡️ ESCUDO DIVINO", (255, 215, 0))
        elif cid == 'IMPACTO':
            self.board[r][c] = 'BLOCKED'
            self.add_floating(r, c, "☄️ METEORITO", (255, 100, 0))
        elif cid == 'TRANSMUTA':
            piece_a = self.board[a][b]
            piece_b = self.board[r][c]
            self.board[a][b] = piece_b
            self.board[r][c] = piece_a
            self.hp[(a, b)], self.hp[(r, c)] = self.hp.get((r, c), 1), self.hp.get((a, b), 1)
        elif cid == 'RECLUTA':
            self.board[r][c] = f"{p}_P"
            self.hp[(r, c)] = MAX_HP['P']
            self.add_floating(r, c, "📯 REFUERZO", (78, 205, 145))
        elif cid == 'ASCENSO':
            self.board[r][c] = f"{p}_B"
            self.hp[(r, c)] = MAX_HP['B']
            self.add_floating(r, c, "🌙 ASCENSO MÉDICO", (177, 156, 217))
        elif cid == 'CENIZA':
            victim_p = d[0]
            self.board[r][c] = ''
            self.hp.pop((r, c), None)
            if self.is_carrier(r, c): self.flag['carried'] = False
            self.audio.play_sfx('death')
            self.handle_piece_loss(victim_p, 'P')
            self.add_floating(r, c, "🔥 CALCINADO", (255, 50, 50))
        elif cid == 'GRILLETE':
            self.frozen[(r, c)] = {'p': d[0], 'active': True}
            self.add_floating(r, c, "⛓️ INMOVILIZADO", (160, 160, 160))
        elif cid == 'VIENTO':
            self.flag['r'] = r
            self.flag['c'] = c
            self.add_floating(r, c, "🌪️ BANDERA DESPLAZADA", (255, 200, 0))
        elif cid == 'EMBOSCADA':
            self.special[r][c] = 'X'
            self.add_floating(r, c, "☠ TRAMPA TENDIDA", (255, 40, 40))
        elif cid == 'HURTO':
            self.flag['r'] = r
            self.flag['c'] = c
            self.flag['carried'] = True
            self.flag['by'] = p
            self.add_floating(r, c, "🗝️ BANDERA ROBADA", (255, 215, 0))

        self.used_cards[p].add(cid)
        self.audio.play_sfx('card')
        self.vfx_events.append({'type': 'spell_cast', 'cid': cid, 'r': r, 'c': c, 'p': p})
        trauma = 4.5 if cid in ('IMPACTO', 'CENIZA', 'VIENTO') else 2.5
        self.vfx_events.append({'type': 'shake', 'trauma': trauma})
        self.log(f"✨ {FACTIONS[ORDER[self.idx]]['name']} invocó hechizo: {CARDS[cid]['name']}")
        if p in self.human_factions:
            self.missions.add_progress("spellmaster", 1)

        self.active_card = None
        self.selected = None
        self.spend_ap(1)

    def deploy_reserve(self, r, c):
        p = self.cur_code()
        if self.is_free(r, c) and self.home_zone(p, r, c) and self.deploy_index is not None:
            unit_type = self.hand_reserves[p].pop(self.deploy_index)
            self.place_piece(p, r, c, unit_type)
            self.acted.add((r, c))
            cost = UNIT_COST[unit_type]
            self.audio.play_sfx('select')
            self.vfx_events.append({'type': 'deploy_burst', 'r': r, 'c': c, 'p': p})
            self.log(f"🛡️ Despliegue de {UNIT_NAMES[unit_type]} en [{r},{c}].")
            self.deploy_index = None
            self.spend_ap(cost)

    def update(self, dt):
        for pop in list(self.floating_popups):
            pop['time'] -= dt
            pop['y_offset'] += dt * 35
            if pop['time'] <= 0:
                self.floating_popups.remove(pop)

        for hit in list(self.hit_effects):
            r, c, t = hit
            t -= dt
            self.hit_effects.remove(hit)
            if t > 0:
                self.hit_effects.append((r, c, t))

        for anim in list(self.move_animations):
            anim['time'] += dt
            if anim['time'] >= anim['duration']:
                self.move_animations.remove(anim)

    def get_oracle_state(self):
        cur_f_key = ORDER[self.idx]
        cur_f_name = FACTIONS[cur_f_key]['name']
        active_code = self.cur_code() if self.cur_code() in self.human_factions else self.human
        active_f_key = next(k for k in ORDER if FACTIONS[k]['code'] == active_code)
        human_name = FACTIONS[active_f_key]['name']

        flag_info = "En el centro sagrado [7,8]"
        if self.flag['carried']:
            carrier_faction = FACTIONS[next(k for k in ORDER if FACTIONS[k]['code'] == self.flag['by'])]['name']
            flag_info = f"Portada por {carrier_faction}"

        enemy_count = 0
        for r in range(N):
            for c in range(N):
                p = self.board[r][c]
                if p and p[0] != active_code and TEAM[p[0]] != TEAM[active_code]:
                    if LO - 1 <= r <= HI + 1 and LO - 1 <= c <= HI + 1:
                        enemy_count += 1

        available_cards = [CARDS[cid]['name'] for cid in FACTION_HANDS.get(active_code, []) if cid not in self.used_cards[active_code]]

        return {
            'turno_nombre': cur_f_name,
            'humano_nombre': human_name,
            'vidas_restantes': self.lives.get(active_code, 3),
            'ap': self.ap,
            'bandera_info': flag_info,
            'bandera_llevada': self.flag['carried'],
            'portador_es_aliado': self.flag['carried'] and TEAM[self.flag['by']] == TEAM[active_code],
            'enemigos_cercanos': enemy_count,
            'cartas_disponibles': ", ".join(available_cards) if available_cards else "Ninguna (Agotadas)"
        }
