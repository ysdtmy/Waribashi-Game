import itertools
import random
import copy


class WaribashiGame():
    def __init__(self, player_n=2):
        assert player_n == 2, "Over the number of player"
        self.win_reward = 1.
        self.lose_reward = -1.
        self.non_reward = 0.
        self.player_n = player_n
        self.turn = 0
        self.render_field = [[1, 1] for p in range(self.player_n)]

    def render(self):
        print('***player1***')
        print('  R               L')
        print('  ' + str(self.render_field[1][0]) + '               ' + str(self.render_field[1][1]) + '  ')
        print()
        print('  ' + str(self.render_field[0][1]) + '               ' + str(self.render_field[0][0]) + '  ')
        print('  L               R')
        print('***player0***')

    def reset(self, silent= True):
        self.turn = 0
        self.render_field = [[1, 1] for p in range(self.player_n)]
        if silent:
            print('==ENV RESET==')
            self.render()
            print()
            return True
        return True

    def is_dead(self, checkedplayer, silent = True):
        winner = None
        is_dead = False
        checked_filed = self.render_field[checkedplayer]
        if max(checked_filed) == 0:
            is_dead = True
            winner = self.get_enemy(checkedplayer)
            if silent:
                print('player' + str(winner) + ' wins!!!!!')

        return is_dead, winner

    def get_enemy(self, player):
        enemy = 1
        if player == 1:
            enemy = 0

        return enemy

    def step(self, player, action, silent = True):
        assert self.turn == player, "invalid player action"

        legalactions = self.get_legal_action(player)
        assert action in legalactions, "Invalid action is chosen"

        code2attack = {
            # actioncode: (From myhand number, To enemy hand number)
            0: (0, 0)
            , 1: (0, 1)
            , 2: (1, 0)
            , 3: (1, 1)
            , 4: (0, 1)
            , 5: (1, 0)
        }

        def attack(player, action):
            attack_from = player
            attack_to = self.get_enemy(player)
            
            if action >= 4:
                attack_to = player

            attack_direction = code2attack[action]
            self.render_field[attack_to][attack_direction[1]] = self.render_field[attack_from][attack_direction[0]] +  self.render_field[attack_to][attack_direction[1]]


            
            return True

        def splits(player, action):
            myfield = self.render_field[player]
            alive_val = max(myfield)
            splitted_val = alive_val + action
            myfield = [splitted_val if val == alive_val else val for val in myfield]
            myfield = [abs(action) if val == 0 else val for val in myfield]
            self.render_field[player] = myfield
            

        if action >= 0:
            attack(player, action)


        else:
            splits(player, action)

        # over 4 value overwrite to 0
        for i in range(len(self.render_field)):
            for j in range(len(self.render_field[i])):
                if self.render_field[i][j] >= 5:
                    self.render_field[i][j] = 0

        is_dead,winner = self.is_dead(self.get_enemy(player))

        if silent:
            print('player' + str(player) + '  ' + 'action is ' + str(action))
            self.render()
            print()

        self.turn = self.get_enemy(player)

        return is_dead,winner

    def chage_turn(self):
        pass

    def get_player_field(self, player):
        player_filed = copy.deepcopy(self.render_field)
        player_filed.insert(0, player_filed[player])
        del player_filed[player + 1]
        return player_filed

    def get_legal_action(self, player, field=None):
        attack2code = {
            ('R', 'R'): 0
            , ('R', 'L'): 1
            , ('L', 'R'): 2
            , ('L', 'L'): 3
        }

        def get_alivehand(field):
            alivehand = []
            if field[0] > 0:
                alivehand.append('R')
            if field[1] > 0:
                alivehand.append('L')
            return alivehand

        legal_actions = []

        if field == None:
            p_field = self.get_player_field(player)
        else:
            p_field = field

        myfield = p_field[0]
        enfield = p_field[1]

        my_alivehand = get_alivehand(myfield)
        en_alivehand = get_alivehand(enfield)

        if len(my_alivehand) == 0 or len(en_alivehand) == 0:
            return None

        attack_variation = list(itertools.product(my_alivehand, en_alivehand))

        for attack in attack_variation:
            legal_actions.append(attack2code[attack])

        if len(my_alivehand) == 2:
            legal_actions.append(4)
            legal_actions.append(5)

        # Need to improve......
        elif len(my_alivehand) == 1:
            aliveval = max(myfield)
            for i in range(aliveval):
                if i == 0:
                    continue
                splitval = -1 * i
                legal_actions.append(splitval)

        return legal_actions


class agent():
    def start_game(self):
        raise NotImplementedError()
    
    def mover(self):
        raise NotImplementedError()
    
    def reward(self):
        raise NotImplementedError()

class human(agent):
    
    def __init__(self):
        self.action_dict = {
            -3:'split 3'
            ,-2:'split 2'
            ,-1:'split 1'
            ,0:'S:right to E:right '
            ,1:'S:right to E:left '
            ,2:'S:left to E:right '
            ,3:'S:left to E:left '
            ,4:'S:right to S:left '
            ,5:'S:left to S:right '
            }
        
        self.int_list =[
            '-1'
            ,'-2'
            ,'-3'
            ,'0'
            ,'1'
            ,'2'
            ,'3'
            ,'4'
            ,'5'
        ]
    
    def start_game(self):
        pass
    
    def mover(self, state, actions, *args, **kwargs):
        print()
        print('Chose your action below!')
        print('*****legal action*****')
        for action in actions:
            action_exp = self.action_dict[action]
            print(str(action) + ':' + action_exp)
        
        while True:
            select_action = input()
            if select_action in self.int_list and int(select_action) in actions:
                break
            else:
                print('not legal action!! please enter action again')
        
        print()
        return int(select_action)




class Q_agent(agent):
    def __init__(self, gamma=0.5, alpha=0.3, epsilon=0.3):
        self.gamma = gamma
        self.alpha = alpha
        self.last_move = None
        self.epsilon = epsilon
        self.prev_state = None
        self.prev_action = None

    def start_game(self):
        self.last_move = None
        self.prev_state = None
        self.prev_action = None

    def get_qval(self, state, action, Qtable):
        qkey = ((state[0][0], state[0][1], state[1][0], state[1][1]), action)
        is_qkey = qkey in Qtable
        if is_qkey:
            q_val = Qtable[qkey]
        else:
            Qtable[qkey] = 0.
            q_val = 0.

        return q_val

    def get_bestaction(self, state, actions, Qtable):

        if len(actions) == 0:
            return None, 0.,

        q_val_dic = {}
        for action in actions:
            q_val = self.get_qval(state, action, Qtable)
            q_val_dic[action] = q_val

        best_actions = {}
        max_qval = max(q_val_dic.values())

        for key, val in q_val_dic.items():
            if val == max_qval:
                best_actions[key] = val

        bestaction = random.choice(list(best_actions.items()))
        best_action = bestaction[0]
        best_qval = bestaction[1]

        return best_action, best_qval

    def mover(self, state, actions, Qtable, silent = True):
        self.prev_state = copy.deepcopy(state)
        if random.random() < self.epsilon:
            if silent:
                print('random choice')
            action = random.choice(actions)
        else:
            if silent:
                print('greedy choice')
            action, _ = self.get_bestaction(state, actions, Qtable)
        # print('UPDATE' + str(self.player))
        self.prev_action = action
        self.last_move = action
        return action

    def reward(self, reward, field, legal_actions, Qtable):
        if self.last_move != None:
            Qtable = self.update(self.prev_state, self.prev_action, reward, field, legal_actions, Qtable)
        return Qtable

    def update(self, prev_state, prev_action, reward, resultstate, legal_actions, Qtable):
        pQ = self.get_qval(prev_state, prev_action, Qtable)

        if legal_actions == None:
            maxnewpQ = 0.

        else:
            _, maxnewpQ = self.get_bestaction(resultstate, legal_actions, Qtable)

        new_qval = pQ + self.alpha * ((reward + self.gamma * maxnewpQ) - pQ)
        Qtable[((prev_state[0][0], prev_state[0][1], prev_state[1][0], prev_state[1][1]), prev_action)] = new_qval
        # print(str([((prev_state[0][0], prev_state[0][1], prev_state[1][0], prev_state[1][1]), prev_action)]) + '=' + str(new_qval))
        return Qtable


class GameMaster():
    def __init__(self, env, p0, p1 , **kwargs):
        self.p0 = p0
        self.p1 = p1
        self.env = env
        if 'Qtable' in kwargs:
            self.Qtable = kwargs['Qtable']
        else:
            self.Qtable = None

    def play_train(self, iter_num=100, t_max = 300, silent = True):
        _silent = silent
        for i in range(iter_num):
            if silent == False:
                _silent = False
                if  i % 1000 == 0:
                    _silent = True

            if _silent:
                print('-*-ROUND' + str(i) + '-*-')
                print()
                
            self.env.reset(silent=_silent)
            self.p0.start_game()
            self.p1.start_game()
            for t in range(t_max):
                if _silent:
                    print('==STEP' + str(t) + '==')
                if self.env.turn == 0:
                    self.thisturn = self.p0
                    self.notturn = self.p1
                else:
                    self.thisturn = self.p1
                    self.notturn = self.p0

                self.turn_playerfield = self.env.get_player_field(self.env.turn)            
                self.notturn_playerfield = self.env.get_player_field(self.env.get_enemy(self.env.turn))

                legal_actions = self.env.get_legal_action(self.env.turn)
                action = self.thisturn.mover(self.turn_playerfield, legal_actions, self.Qtable, silent = _silent)
                is_dead, _ = self.env.step(self.env.turn, action,silent=_silent)

                if is_dead:
                    legal_actions = []
                    self.new_notturn_playerfield = self.env.get_player_field(self.env.get_enemy(self.env.turn))
                    self.new_turn_playerfield = self.env.get_player_field(self.env.turn)
                    self.Qtable = self.thisturn.reward(self.env.win_reward, self.new_turn_playerfield, legal_actions, Qtable=self.Qtable)
                    self.Qtable = self.notturn.reward(self.env.lose_reward, self.new_notturn_playerfield, legal_actions, Qtable=self.Qtable)
                    break

                else:
                    self.new_notturn_playerfield = self.env.get_player_field(self.env.get_enemy(self.env.turn))
                    legal_actions = self.env.get_legal_action(self.env.get_enemy(self.env.turn))
                    self.Qtable = self.notturn.reward(self.env.non_reward, self.new_notturn_playerfield, legal_actions, Qtable=self.Qtable)
        
    def play(self, iter_num=100, t_max = 300, silent = True):
        _silent = silent
        win_dict = {-1:0,0:0,1:0}
        for i in range(iter_num):
            if silent == False:
                _silent = False
                if  i % 1000 == 0:
                    _silent = True

            if _silent:
                print('-*-ROUND' + str(i) + '-*-')
                print()

            self.env.reset(silent=_silent)
            self.p0.start_game()
            self.p1.start_game()
            for t in range(t_max):
                if _silent:
                    print('==STEP' + str(t) + '==')
                if self.env.turn == 0:
                    self.thisturn = self.p0
                    self.notturn = self.p1
                else:
                    self.thisturn = self.p1
                    self.notturn = self.p0
                    
                self.turn_playerfield = self.env.get_player_field(self.env.turn)            
                self.notturn_playerfield = self.env.get_player_field(self.env.get_enemy(self.env.turn))

                legal_actions = self.env.get_legal_action(self.env.turn)
                action = self.thisturn.mover(self.turn_playerfield, legal_actions, self.Qtable, silent = _silent)
                is_dead,winner = self.env.step(self.env.turn, action, silent = _silent)
                
                if is_dead:
                    win_dict[winner] = win_dict[winner] + 1
                    break
                
                if t == t_max -1:
                    print('Draw!!!!')
                    win_dict[-1] = win_dict[-1] + 1
        
        return win_dict
                


if __name__ == "__main__":
    env = WaribashiGame()
    p0 = Q_agent(0)
    p1 = Q_agent(1)
    Qtable = {}

    GM = GameMaster(env, p0, p1, iter_num=1, Qtable=Qtable)
    GM.play_train()
