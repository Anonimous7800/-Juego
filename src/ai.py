import random
from collections import deque
from src.constants import N, TEAM, ATK, MAX_HP, UNIT_COST, FACTION_HANDS, MAX_LIVES
from src.settings import SettingsManager

class AIEngine:
    def __init__(self, board_game):
        self.game = board_game
        self.settings = SettingsManager()

    def get_bfs_path(self, start, target, ignore_team=None):
        if start == target:
            return [start]
        q = deque([(start[0], start[1], [start])])
        visited = {start}
        while q:
            cr, cc, path = q.popleft()
            if cr == target[0] and cc == target[1]:
                return path
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                nr, nc = cr + dr, cc + dc
                if 0 <= nr < N and 0 <= nc < N and (nr, nc) not in visited:
                    cell = self.game.board[nr][nc]
                    if cell == '' or (nr == target[0] and nc == target[1]) or (ignore_team and cell != 'BLOCKED' and TEAM.get(cell[0]) == ignore_team):
                        visited.add((nr, nc))
                        q.append((nr, nc, path + [(nr, nc)]))
        return []

    def get_tile_threat(self, r, c, my_team):
        max_threat = 0
        threat_count = 0
        for er in range(N):
            for ec in range(N):
                eval_piece = self.game.board[er][ec]
                if eval_piece and eval_piece != 'BLOCKED' and TEAM.get(eval_piece[0]) != my_team:
                    if max(abs(er - r), abs(ec - c)) <= 3:
                        moves = self.game.calc_moves(er, ec, eval_piece)
                        if (r, c) in moves:
                            threat_count += 1
                            max_threat = max(max_threat, ATK.get(eval_piece[2], 2))
        return threat_count, max_threat

    def think_and_execute(self):
        if self.game.game_over or self.game.is_human_turn():
            return False

        p = self.game.cur_code()
        team = TEAM[p]
        is_hard = self.settings.get("difficulty") == "Maestro"

        goal_r, goal_c = (N - 1, 0) if team == 1 else (0, N - 1)
        flag_carried = self.game.flag['carried']
        flag_by = self.game.flag['by']
        carrier_team = TEAM.get(flag_by) if flag_carried and flag_by else None
        carrier_r = self.game.flag['r']
        carrier_c = self.game.flag['c']
        ally_has_flag = flag_carried and carrier_team == team
        enemy_has_flag = flag_carried and carrier_team is not None and carrier_team != team

        def cheb(r1, c1, r2, c2):
            return max(abs(r1 - r2), abs(c1 - c2))

        carrier_victory_path = []
        carrier_corridor = set()
        if ally_has_flag:
            carrier_victory_path = self.get_bfs_path((carrier_r, carrier_c), (goal_r, goal_c), ignore_team=team)
            if carrier_victory_path:
                carrier_corridor = set(carrier_victory_path[1:6])

        threat_enemies_near_carrier = []
        if ally_has_flag:
            for er in range(N):
                for ec in range(N):
                    ep = self.game.board[er][ec]
                    if ep and ep != 'BLOCKED' and TEAM.get(ep[0]) != team:
                        if cheb(er, ec, carrier_r, carrier_c) <= 4:
                            threat_enemies_near_carrier.append((er, ec))

        best_move = None
        best_score = -1e9

        unit_vals = {'K': 350, 'Q': 200, 'R': 150, 'N': 110, 'B': 90, 'P': 55}

        for r in range(N):
            for c in range(N):
                val = self.game.board[r][c]
                if not self.game.is_own(val, p) or (r, c) in self.game.acted:
                    continue
                if (r, c) in self.game.frozen and self.game.frozen[(r, c)]['active']:
                    continue

                utype = val[2]
                carrier = self.game.is_carrier(r, c)
                my_hp = self.game.hp.get((r, c), MAX_HP[utype])
                my_atk = ATK.get(utype, 2)
                valid_moves = self.game.calc_moves(r, c, val)

                for (ar, ac) in valid_moves:
                    target_val = self.game.board[ar][ac]
                    is_friendly_target = bool(target_val and target_val != 'BLOCKED' and TEAM.get(target_val[0]) == team)
                    score = random.uniform(0, 1.5)

                    threat_count, max_threat = self.get_tile_threat(ar, ac, team)

                    if carrier:
                        if self.game.on_goal(p, ar, ac):
                            score += 100000.0
                        else:
                            old_gdist = cheb(r, c, goal_r, goal_c)
                            new_gdist = cheb(ar, ac, goal_r, goal_c)
                            score += 140.0 * (old_gdist - new_gdist)
                            if is_friendly_target and new_gdist < old_gdist:
                                score += 250.0
                            if threat_count > 0:
                                score -= 120.0 * threat_count
                                if my_hp <= max_threat:
                                    score -= 450.0
                    elif ally_has_flag:
                        if (r, c) in carrier_corridor:
                            if (ar, ac) not in carrier_corridor:
                                score += 420.0
                            elif is_friendly_target and (ar, ac) == (carrier_r, carrier_c):
                                old_c_dist = cheb(carrier_r, carrier_c, goal_r, goal_c)
                                new_c_dist = cheb(r, c, goal_r, goal_c)
                                if new_c_dist < old_c_dist:
                                    score += 650.0
                                else:
                                    score -= 200.0
                            else:
                                score -= 350.0
                        else:
                            if (ar, ac) in carrier_corridor:
                                score -= 400.0

                        if target_val and not is_friendly_target:
                            if (ar, ac) in threat_enemies_near_carrier:
                                score += 450.0
                                def_hp = self.game.hp.get((ar, ac), 1)
                                if def_hp <= my_atk:
                                    score += 200.0

                        escort_dist = cheb(ar, ac, carrier_r, carrier_c)
                        if escort_dist in (1, 2) and (ar, ac) not in carrier_corridor:
                            score += 95.0
                            if threat_enemies_near_carrier:
                                enemy_dists = [cheb(ar, ac, er, ec) for er, ec in threat_enemies_near_carrier]
                                score += 40.0 * (4.0 - min(enemy_dists))
                        elif escort_dist > 5:
                            old_edist = cheb(r, c, carrier_r, carrier_c)
                            score += 15.0 * (old_edist - escort_dist)

                        old_fwd = cheb(r, c, goal_r, goal_c)
                        new_fwd = cheb(ar, ac, goal_r, goal_c)
                        score += 18.0 * (old_fwd - new_fwd)
                    elif enemy_has_flag:
                        if (ar, ac) == (carrier_r, carrier_c):
                            score += 700.0
                            def_hp = self.game.hp.get((ar, ac), 1)
                            if def_hp <= my_atk:
                                score += 350.0
                        else:
                            old_ec_dist = cheb(r, c, carrier_r, carrier_c)
                            new_ec_dist = cheb(ar, ac, carrier_r, carrier_c)
                            score += 35.0 * (old_ec_dist - new_ec_dist)
                            enemy_goal = (0, N - 1) if carrier_team == 2 else (N - 1, 0)
                            if cheb(ar, ac, enemy_goal[0], enemy_goal[1]) <= cheb(carrier_r, carrier_c, enemy_goal[0], enemy_goal[1]):
                                score += 60.0
                    else:
                        if ar == carrier_r and ac == carrier_c:
                            score += 300.0
                        else:
                            old_flag_dist = cheb(r, c, carrier_r, carrier_c)
                            new_flag_dist = cheb(ar, ac, carrier_r, carrier_c)
                            score += 22.0 * (old_flag_dist - new_flag_dist)

                    if target_val and not is_friendly_target:
                        target_utype = target_val[2]
                        def_hp = self.game.hp.get((ar, ac), 1)
                        def_atk = ATK.get(target_utype, 2)
                        val_gain = unit_vals.get(target_utype, 50)
                        score += 50.0 + val_gain * 0.7
                        if def_hp <= my_atk:
                            score += 140.0 + val_gain * 0.5
                        else:
                            if my_hp <= def_atk:
                                if val_gain > unit_vals.get(utype, 50) + 50:
                                    score += 25.0
                                else:
                                    score -= 180.0
                    elif is_friendly_target:
                        if not ally_has_flag and not carrier:
                            score -= 20.0

                    if utype == 'K':
                        score -= 30.0
                        if my_hp <= 4:
                            if threat_count > 0:
                                score -= 350.0
                            else:
                                score += 40.0
                    elif utype == 'B':
                        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                            nr, nc = ar + dr, ac + dc
                            if 0 <= nr < N and 0 <= nc < N:
                                friend_adj = self.game.board[nr][nc]
                                if friend_adj and friend_adj != 'BLOCKED' and TEAM.get(friend_adj[0]) == team:
                                    f_hp = self.game.hp.get((nr, nc), 1)
                                    f_max = MAX_HP.get(friend_adj[2], 4)
                                    if f_hp < f_max:
                                        score += 30.0 * (f_max - f_hp)
                                        if self.game.is_carrier(nr, nc):
                                            score += 150.0

                    if not carrier and utype != 'K':
                        if threat_count > 0 and my_hp <= max_threat and (not target_val or is_friendly_target):
                            score -= 130.0

                    sp = self.game.special[ar][ac]
                    if sp == 'X':
                        score -= 250.0
                    elif sp == 'I':
                        score += 35.0
                    elif sp == 'H':
                        my_lives = self.game.lives[p]
                        if my_lives < MAX_LIVES or my_hp < MAX_HP[utype]:
                            score += 85.0
                        else:
                            score += 30.0
                    elif sp == 'T':
                        score += 15.0 if not carrier else -250.0

                    if score > best_score:
                        best_score = score
                        best_move = ('move', (r, c), (ar, ac))

        reserves = self.game.hand_reserves[p]
        if reserves and self.game.ap >= UNIT_COST.get(reserves[0], 1):
            best_dep_tile = None
            min_dep_dist = 1e9
            target_focus_r = carrier_r
            target_focus_c = carrier_c
            if ally_has_flag:
                target_focus_r = goal_r
                target_focus_c = goal_c
            for r in range(N):
                for c in range(N):
                    if self.game.is_free(r, c) and self.game.home_zone(p, r, c):
                        if (r, c) in carrier_corridor:
                            continue
                        d = cheb(r, c, target_focus_r, target_focus_c)
                        if d < min_dep_dist:
                            min_dep_dist = d
                            best_dep_tile = (r, c)
            if best_dep_tile:
                dep_score = 30.0 + random.uniform(0, 5)
                if dep_score > best_score:
                    best_score = dep_score
                    best_move = ('deploy', 0, best_dep_tile)

        for cid in FACTION_HANDS.get(p, []):
            if cid not in self.game.used_cards[p] and self.game.ap >= 1:
                if cid == 'AURA':
                    target_cand = None
                    if ally_has_flag:
                        target_cand = (carrier_r, carrier_c)
                    else:
                        for r in range(N):
                            for c in range(N):
                                val = self.game.board[r][c]
                                if self.game.is_own(val, p) and val.endswith('_K'):
                                    target_cand = (r, c)
                                    break
                    if target_cand and self.game.ok_card_target(cid, target_cand[0], target_cand[1]):
                        card_score = 320.0 if ally_has_flag else 90.0
                        if card_score > best_score:
                            best_score = card_score
                            best_move = ('card', cid, target_cand)
                elif cid == 'RECLUTA':
                    best_rec_tile = None
                    min_d = 1e9
                    for r in range(N):
                        for c in range(N):
                            if self.game.ok_card_target(cid, r, c) and (r, c) not in carrier_corridor:
                                d = cheb(r, c, carrier_r, carrier_c)
                                if d < min_d:
                                    min_d = d
                                    best_rec_tile = (r, c)
                    if best_rec_tile:
                        card_score = 45.0
                        if card_score > best_score:
                            best_score = card_score
                            best_move = ('card', cid, best_rec_tile)
                elif cid == 'GRILLETE' and enemy_has_flag:
                    if self.game.ok_card_target(cid, carrier_r, carrier_c):
                        card_score = 400.0
                        if card_score > best_score:
                            best_score = card_score
                            best_move = ('card', cid, (carrier_r, carrier_c))

        if not best_move:
            self.game.next_turn()
            return True

        action_type = best_move[0]
        if action_type == 'move':
            fr, fc = best_move[1]
            tr, tc = best_move[2]
            target_val = self.game.board[tr][tc]
            if target_val and target_val != 'BLOCKED':
                if TEAM.get(target_val[0]) == TEAM.get(self.game.board[fr][fc][0]):
                    self.game.swap_pieces(fr, fc, tr, tc)
                    self.game.audio.play_sfx('move')
                else:
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
