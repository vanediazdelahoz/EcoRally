# Lógica del tablero principal

from square import Square
from player import Player
import random


def main():
    rounds = 5
    total_recylcing_points = 3

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
    s68.add_next_square(s69)
    s69.add_next_square(s0)
    s32.add_next_square(s33)  # 33 empieza bifurcación derecha de 32
    s32.add_next_square(s33)
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
    s52.add_next_square(s53)
    s53.add_next_square(s54)
    s54.add_next_square(s55)
    s55.add_next_square(s56)
    s56.add_next_square(s57)
    s57.add_next_square(s58)
    s58.add_next_square(s59)
    s59.add_next_square(s67)
    s48.add_next_square(s53)  # 53 empieza bifurcación izquierda de 48
    s53.add_next_square(s54)
    s54.add_next_square(s55)
    s55.add_next_square(s56)
    s56.add_next_square(s57)
    s57.add_next_square(s58)
    s58.add_next_square(s59)

    possible_recycling_points = [[s2, s4], [s13, s17], [s44], [s56]]

    # Definir puntos de reciclaje posibles
    def choose_recycle_points(pos_rec, total_rpoints):
        for _ in range(total_rpoints):
            x = random.randint(0, len(pos_rec) - 1)
            if len(pos_rec[x]) > 1:
                y = random.randint(0, len(pos_rec[x]) - 1)
                pos_rec[x][y].set_recycling_point()
                print(f"Punto de reciclaje en {pos_rec[x][y].id}")
                del pos_rec[x]
            else:
                pos_rec[x][0].set_recycling_point()
                print(f"Punto de reciclaje en {pos_rec[x][0].id}")
                del pos_rec[x]

    choose_recycle_points(possible_recycling_points, total_recylcing_points)

    # Crear jugador
    player1 = Player("Lulo")
    player2 = Player("Venado")
    while True:
        dice1 = random.randint(0, 5)
        dice2 = random.randint(0, 5)
        print(f"dado de {player1.character}: {dice1}")
        print(f"dado de {player2.character}: {dice2}")
        if dice1 > dice2:
            print(f"{player1.character} comienza")
            break
        elif dice2 > dice1:
            print(f"{player2.character} comienza")
            player1, player2 = player2, player1
            break
        else:
            print("Empate. Se lanzan los dados de nuevo")

    # Iniciar en start
    player1.move_to(s0)
    player2.move_to(s0)

    def move_player(player):
        if player.position.next_squares:
            if len(player.position.next_squares) > 1:
                print("Selecciona el camino:")
                for i in range(len(player.position.next_squares)):
                    print(f"{i} para id = {player.position.next_squares[i].id}")
                camino = int(input())
                player.move_to(player.position.next_squares[camino])
            else:
                player.move_to(player.position.next_squares[0])
            if player.position.recycle:
                player.try_recycle()

    # Moverse y recolectar basura
    def round(r, player1, player2):
        print(f"Ronda {r}")

        print(f"Turno de {player1.character}")
        dice = random.randint(0, 5)
        print(f"dado {dice}")
        for _ in range(dice + 1):
            move_player(player1)
        print(f"{player1.character} se movió a la casilla {player1.position.id}")
        player1.position.effect(player1)
        print(f"Basura: {player1.trash}, Insignias: {player1.badges}")

        print(f"Turno de {player2.character}")
        dice = random.randint(0, 5)
        print(f"dado {dice}")
        for _ in range(dice + 1):
            move_player(player2)
        print(f"{player2.character} se movió a la casilla {player2.position.id}")
        player2.position.effect(player2)
        print(f"Basura: {player2.trash}, Insignias: {player2.badges}")

    for r in range(rounds):
        round(r + 1, player1, player2)


if __name__ == "__main__":
    main()
