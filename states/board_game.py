# Implementa la lógica principal del juego de mesa con tablero, casillas y jugadores

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from states.square import Square
from states.player import Player
from agent.dynaq_agent import DynaQAgent
import random

MODO_JUEGO = "humano_vs_agente"
MOSTRAR_DECISIONES_AGENTE = True

def create_board():

    # Crear casillas
    s0 = Square(0, "blue")
    s1 = Square(1, "red")
    s2 = Square(2, "blue")
    s3 = Square(3, "red")
    s4 = Square(4, "blue")
    s5 = Square(5, "green")
    s6 = Square(6, "red")
    s7 = Square(7, "purple")
    s8 = Square(8, "green")
    s9 = Square(9, "purple")
    s10 = Square(10, "green")
    s11 = Square(11, "red")
    s12 = Square(12, "green")
    s13 = Square(13, "blue")
    s14 = Square(14, "green")
    s15 = Square(15, "red")
    s16 = Square(16, "green")
    s17 = Square(17, "blue")
    s18 = Square(18, "red")
    s19 = Square(19, "green")
    s20 = Square(20, "purple")
    s21 = Square(21, "green")
    s22 = Square(22, "red")
    s23 = Square(23, "green")
    s24 = Square(24, "purple")
    s25 = Square(25, "green")
    s26 = Square(26, "green")
    s27 = Square(27, "red")
    s28 = Square(28, "green")
    s29 = Square(29, "blue")
    s30 = Square(30, "green")
    s31 = Square(31, "blue")
    s32 = Square(32, "purple")
    s33 = Square(33, "green")
    s34 = Square(34, "green")
    s35 = Square(35, "green")
    s36 = Square(36, "green")
    s37 = Square(37, "green")
    s38 = Square(38, "red")
    s39 = Square(39, "green")
    s40 = Square(40, "red")
    s41 = Square(41, "purple")
    s42 = Square(42, "green")
    s43 = Square(43, "green")
    s44 = Square(44, "blue")
    s45 = Square(45, "red")
    s46 = Square(46, "blue")
    s47 = Square(47, "green")
    s48 = Square(48, "purple")
    s49 = Square(49, "green")
    s50 = Square(50, "blue")
    s51 = Square(51, "green")
    s52 = Square(52, "purple")
    s53 = Square(53, "red")
    s54 = Square(54, "green")
    s55 = Square(55, "red")
    s56 = Square(56, "blue")
    s57 = Square(57, "green")
    s58 = Square(58, "red")
    s59 = Square(59, "green")
    s60 = Square(60, "purple")
    s61 = Square(61, "purple")
    s62 = Square(62, "blue")
    s63 = Square(63, "red")
    s64 = Square(64, "blue")
    s65 = Square(65, "green")
    s66 = Square(66, "purple")
    s67 = Square(67, "green")
    s68 = Square(68, "purple")
    s69 = Square(69, "green")

    # Conectar casillas
    s0.add_next_square(s1)
    s1.add_next_square(s2)
    s2.add_next_square(s3)
    s3.add_next_square(s4)
    s4.add_next_square(s5)
    s5.add_next_square(s6)
    s6.add_next_square(s7)
    s7.add_next_square(s8)
    s8.add_next_square(s9)
    s9.add_next_square(s10)
    s10.add_next_square(s11)
    s11.add_next_square(s12)
    s12.add_next_square(s13)
    s13.add_next_square(s14)
    s14.add_next_square(s15)
    s15.add_next_square(s16)  # 16 es casilla de bifurcación
    s16.add_next_square(s17)  # 17 empieza bifurcación izquierda de 16
    s17.add_next_square(s18)
    s18.add_next_square(s19)
    s19.add_next_square(s20)
    s20.add_next_square(s21)
    s21.add_next_square(s22)
    s22.add_next_square(s23)  # 23 es casilla de bifurcación
    s23.add_next_square(s24)  # 24 empieza bifurcación derecha de 23
    s24.add_next_square(s25)
    s25.add_next_square(s26)
    s26.add_next_square(s32)  # 32 es casilla de bifurcación
    s23.add_next_square(s27)  # 27 empieza bifurcación izquierda de 23
    s27.add_next_square(s28)
    s28.add_next_square(s29)
    s29.add_next_square(s30)
    s30.add_next_square(s31)
    s31.add_next_square(s32)  # 32 es casilla de bifurcación
    s16.add_next_square(s61)  # 61 empieza bifurcación derecha de 16
    s61.add_next_square(s62)
    s62.add_next_square(s63)
    s63.add_next_square(s64)
    s64.add_next_square(s65)
    s65.add_next_square(s66)
    s66.add_next_square(s67)
    s67.add_next_square(s68)
    s68.add_next_square(s69)
    s69.add_next_square(s0)
    s32.add_next_square(s33)  # 33 empieza bifurcación derecha de 32
    s33.add_next_square(s60)
    s60.add_next_square(s64)
    s32.add_next_square(s34)  # 34 empieza bifurcación izquierda de 32
    s34.add_next_square(s35)
    s35.add_next_square(s36)
    s36.add_next_square(s37)
    s37.add_next_square(s38)
    s38.add_next_square(s39)
    s39.add_next_square(s40)
    s40.add_next_square(s41)
    s41.add_next_square(s42)
    s42.add_next_square(s43)
    s43.add_next_square(s44)
    s44.add_next_square(s45)
    s45.add_next_square(s46)
    s46.add_next_square(s47)
    s47.add_next_square(s48)  # 48 es casilla de bifurcación
    s48.add_next_square(s49)  # 49 empieza bifurcación derecha de 48
    s49.add_next_square(s50)
    s50.add_next_square(s51)
    s51.add_next_square(s52)
    s52.add_next_square(s59)
    s59.add_next_square(s67)
    s48.add_next_square(s53)  # 53 empieza bifurcación izquierda de 48
    s53.add_next_square(s54)
    s54.add_next_square(s55)
    s55.add_next_square(s56)
    s56.add_next_square(s57)
    s57.add_next_square(s58)
    s58.add_next_square(s59)

    # Retornar todas las casillas como diccionario
    squares = {
        0: s0, 1: s1, 2: s2, 3: s3, 4: s4, 5: s5, 6: s6, 7: s7, 8: s8, 9: s9,
        10: s10, 11: s11, 12: s12, 13: s13, 14: s14, 15: s15, 16: s16, 17: s17,
        18: s18, 19: s19, 20: s20, 21: s21, 22: s22, 23: s23, 24: s24, 25: s25,
        26: s26, 27: s27, 28: s28, 29: s29, 30: s30, 31: s31, 32: s32, 33: s33,
        34: s34, 35: s35, 36: s36, 37: s37, 38: s38, 39: s39, 40: s40, 41: s41,
        42: s42, 43: s43, 44: s44, 45: s45, 46: s46, 47: s47, 48: s48, 49: s49,
        50: s50, 51: s51, 52: s52, 53: s53, 54: s54, 55: s55, 56: s56, 57: s57,
        58: s58, 59: s59, 60: s60, 61: s61, 62: s62, 63: s63, 64: s64, 65: s65,
        66: s66, 67: s67, 68: s68, 69: s69
    }
    
    return squares

def setup_recycling_points(squares, total_recycling_points=3, silent_mode=False):

    possible_recycling_points = [
        [squares[2], squares[4]], 
        [squares[13], squares[17]], 
        [squares[44]], 
        [squares[56]]
    ]

    def choose_recycle_points(pos_rec, total_rpoints):
        rpoints = []
        pos_rec_copy = [group[:] for group in pos_rec]
        for _ in range(total_rpoints):
            if not pos_rec_copy:
                break
            x = random.randint(0, len(pos_rec_copy) - 1)
            if len(pos_rec_copy[x]) > 1:
                y = random.randint(0, len(pos_rec_copy[x]) - 1)
                rpoints.append(pos_rec_copy[x][y])
                pos_rec_copy[x][y].set_recycling_point()
                if not silent_mode:
                    print(f"Punto de Reciclaje en la casilla {pos_rec_copy[x][y].id}")
                del pos_rec_copy[x]
            else:
                rpoints.append(pos_rec_copy[x][0])
                pos_rec_copy[x][0].set_recycling_point()
                if not silent_mode:
                    print(f"Punto de Reciclaje en la casilla {pos_rec_copy[x][0].id}")
                del pos_rec_copy[x]
        return rpoints

    return choose_recycle_points(possible_recycling_points, total_recycling_points)

def BoardGame(use_agent=None, train_agent=None, agent=None, silent_mode=False):
    
    if use_agent is None:
        use_agent = (MODO_JUEGO == "humano_vs_agente")
    
    if train_agent is None:
        train_agent = False
    
    rounds = 10
    total_recylcing_points = 3
    recycle_timeout = 2
    initial_trash = 10

    # Usar la función para crear el tablero
    squares = create_board()
    
    # Configurar puntos de reciclaje
    recycling_points = setup_recycling_points(squares, total_recylcing_points, silent_mode)

    # Crear jugadores
    player1 = Player("1")
    player2 = Player("2")
    player1.trash = initial_trash
    player2.trash = initial_trash
    
    # Configurar agente
    if use_agent:
        if agent is None:
            game_agent = DynaQAgent(train_mode=train_agent)
            if not train_agent:
                game_agent.epsilon = 0.0
                
                # Cargar política entrenada
                model_path = "agent/agent_policy.pkl"
                game_agent.load_policy(model_path)
        else:
            game_agent = agent
            if not train_agent:
                game_agent.epsilon = 0.0
    else:
        game_agent = None
    
    agent_state = None
    agent_action = None
    
    while True:
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        if dice2 > dice1:
            player1, player2 = player2, player1
            break

    player1.move_to(squares[0])
    player2.move_to(squares[0])

    def move_player(player, timeout, is_agent_turn=False, current_round=1):
        nonlocal agent_state, agent_action
        
        if player.position.next_squares:
            if len(player.position.next_squares) > 1:
                if is_agent_turn and game_agent:
                    state = game_agent.encode_state(
                        player.position, 
                        rounds - current_round + 1,
                        player.trash, 
                        recycling_points,
                        player.badges,
                        player1.badges if player == player2 else player2.badges
                    )
                    possible_actions = list(range(len(player.position.next_squares)))
                    action = game_agent.get_action(state, possible_actions)
                    
                    if train_agent:
                        agent_state = state
                        agent_action = action
                        game_agent.last_trash = player.trash
                        game_agent.last_badges = player.badges
                    
                    camino = action
                else:
                    if not silent_mode:
                        if camino not in range(len(player.position.next_squares)):
                            camino = 0
                    else:
                        camino = random.choice(range(len(player.position.next_squares)))
                    
                player.move_to(player.position.next_squares[camino])
            else:
                player.move_to(player.position.next_squares[0])
        
        # Aplicar efecto de la casilla
        if player.position.recycle:
            player.try_recycle(timeout, silent_mode)
        
        if is_agent_turn and game_agent and train_agent and agent_state is not None:
            opponent = player1 if player == player2 else player2
            reward = game_agent.calculate_reward(player, opponent, recycling_points)
            
            new_state = game_agent.encode_state(
                player.position, 
                rounds - current_round + 1,
                player.trash, 
                recycling_points,
                player.badges,
                opponent.badges
            )
            
            next_possible_actions = list(range(len(player.position.next_squares))) if player.position.next_squares else [0]
            game_agent.update(agent_state, agent_action, new_state, reward, next_possible_actions)

    def round(r, player1, player2, timeout, rpoints):

        # Turno del jugador 1
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        dice = dice1 + dice2
        for _ in range(dice):
            move_player(player1, timeout, is_agent_turn=False, current_round=r)
        player1.position.effect(player1, silent_mode)

        # Turno del jugador 2
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        dice = dice1 + dice2
        for _ in range(dice):
            move_player(player2, timeout, is_agent_turn=use_agent, current_round=r)
        player2.position.effect(player2, silent_mode)
        
        for i in rpoints:
            if i.timeout > 0:
                i.timeout += -1

    for r in range(rounds):
        round(r + 1, player1, player2, recycle_timeout, recycling_points)

    player2_won = False
    if (player2.badges > player1.badges):
        player2_won = True
    else:
        if (player2.trash > player1.trash):
            player2_won = True
    
    if use_agent and train_agent and game_agent:
        game_agent.end_episode(player2_won)
    
    return player2_won if use_agent else None

if __name__ == "__main__":
    BoardGame()