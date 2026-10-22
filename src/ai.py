import random
from src.constants import N, TEAM, ATK, MAX_HP, UNIT_COST, FACTION_HANDS, MAX_LIVES
from src.settings import SettingsManager

class AIEngine:
    def __init__(self, board_game):
        self.game = board_game
        self.settings = SettingsManager()

    def think_and_execute(self):
        if self.game.game_over or self.game.is_human_turn():
            return False

        p = self.game.cur_code()
        team = TEAM[p]
        is_hard = self.settings.get("difficulty") == "Maestro"

        best_move = None
        best_score = -1e9

        def cheb(r1, c1, r2, c2):
            return max(abs(r1 - r2), abs(c1 - c2))

        def goal_dist(r, c):
            return cheb(r, c, N - 1, 0) if team == 1 else cheb(r, c, 0, N - 1)

        flag_r, flag_c = self.game.flag['r'], self.game.flag['c']

        for r in range(N):
            for c in range(N):
                val = self.game.board[r][c]
                if not self.game.is_own(val, p) or (r, c) in self.game.acted:
                    continue
                if (r, c) in self.game.frozen and self.game.frozen[(r, c)]['active']:
                    continue

                utype = val[2]
                carrier = self.game.is_carrier(r, c)
                valid_moves = self.game.calc_moves(r, c, val)

                for (ar, ac) in valid_moves:
                    target_val = self.game.board[ar][ac]
                    score = random.uniform(0, 3)

                    if target_val:
                        target_utype = target_val[2]
                        def_hp = self.game.hp.get((ar, ac), 1)
                        my_atk = ATK[utype]
                        score += 40 + my_atk * 5
                        if target_utype == 'K':
                            score += 150
                        if def_hp <= my_atk:
                            score += 50
                        else:
                            score -= ATK[target_utype] * 5
                        if carrier:
                            score -= 30
                    elif utype == 'K':
                        score -= 5

                    if carrier:
                        score += 70 * (goal_dist(r, c) - goal_dist(ar, ac))
                        if self.game.on_goal(p, ar, ac):
                            score += 10000
                    elif not self.game.flag['carried']:
                        score += 15 * (cheb(r, c, flag_r, flag_c) - cheb(ar, ac, flag_r, flag_c))
                        if ar == flag_r and ac == flag_c:
                            score += 110
                    else:
                        if TEAM[self.game.flag['by']] != team:
                            score += 18 * (cheb(r, c, flag_r, flag_c) - cheb(ar, ac, flag_r, flag_c))

                    sp = self.game.special[ar][ac]
                    if sp == 'X':
                        score -= 45
                    elif sp == 'I':
                        score += 18
                    elif sp == 'H':
                        my_lives = self.game.lives[p]
                        score += (85 if my_lives <= 2 else 45)
                    elif sp == 'T' and not carrier:
                        score += 12

                    if score > best_score:
                        best_score = score
                        best_move = ('move', (r, c), (ar, ac))

        reserves = self.game.hand_reserves[p]
        if reserves and self.game.ap >= UNIT_COST[reserves[0]]:
            best_dep_tile = None
            min_dist = 1e9
            for r in range(N):
                for c in range(N):
                    if self.game.is_free(r, c) and self.game.home_zone(p, r, c):
                        d = cheb(r, c, flag_r, flag_c)
                        if d < min_dist:
                            min_dist = d
                            best_dep_tile = (r, c)
            if best_dep_tile:
                dep_score = 15 + random.uniform(0, 5)
                if dep_score > best_score:
                    best_score = dep_score
                    best_move = ('deploy', 0, best_dep_tile)

        for cid in FACTION_HANDS.get(p, []):
            if cid not in self.game.used_cards[p] and self.game.ap >= 1:
                if cid == 'AURA':
                    for r in range(N):
                        for c in range(N):
                            if self.game.is_own(self.game.board[r][c], p):
                                if self.game.is_carrier(r, c) or self.game.board[r][c].endswith('_K'):
                                    card_score = 75
                                    if card_score > best_score:
                                        best_score = card_score
                                        best_move = ('card', cid, (r, c))
                elif cid == 'RECLUTA':
                    for r in range(N):
                        for c in range(N):
                            if self.game.ok_card_target(cid, r, c):
                                card_score = 25
                                if card_score > best_score:
                                    best_score = card_score
                                    best_move = ('card', cid, (r, c))

        if not best_move:
            self.game.next_turn()
            return True

        action_type = best_move[0]
        if action_type == 'move':
            fr, fc = best_move[1]
            tr, tc = best_move[2]
            if self.game.board[tr][tc] and self.game.board[tr][tc] != 'BLOCKED':
                self.game.attack(fr, fc, tr, tc)
            else:
                self.game.move_piece(fr, fc, tr, tc)
                self.game.audio.play_sfx('move')
            self.game.acted.add((fr, fc))
            self.game.acted.add((tr, tc))
            self.game.spend_ap(1)
        elif action_type == 'deploy':
            idx = best_move[1]
            r, c = best_move[2]
            self.game.deploy_index = idx
            self.game.deploy_reserve(r, c)
        elif action_type == 'card':
            cid = best_move[1]
            r, c = best_move[2]
            self.game.active_card = cid
            self.game.use_card(r, c)

        return True
