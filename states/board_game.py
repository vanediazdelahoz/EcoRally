# Lógica del tablero principal

from square import Square
from player import Player
import random


def main():
    rounds = 5

    # Crear casillas
    start = Square(0, "blue")
    green1 = Square(1, "green")
    green2 = Square(2, "green")
    recycle = Square(3, "blue")
    recycle.set_recycling_point()

    # Conectar casillas (grafo simple)
    start.add_next_square(green1)
    green1.add_next_square(green2)
    green1.add_next_square(recycle)
    green2.add_next_square(start)
    recycle.add_next_square(start)

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
            print(f"{player2.character} comienza.")
            player1, player2 = player2, player1
            break
        else:
            print("Empate. Se lanzan los dados de nuevo")

    # Iniciar en start
    player1.move_to(start)
    player2.move_to(start)

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
