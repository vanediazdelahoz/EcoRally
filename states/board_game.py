# Lógica del tablero principal

from square import Square
from player import Player
import random


def main():
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
    player = Player("EcoHéroe")

    # Iniciar en start
    player.move_to(start)
    print(f"{player.character} comienza en la casilla {player.position.id}")

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
    while True:
        dice = random.randint(0, 5)
        print(f"dado {dice}")
        for _ in range(dice + 1):
            move_player(player)
        print(f"{player.character} se movió a la casilla {player.position.id}")
        player.position.effect(player)
        print(f"Basura: {player.trash}, Insignias: {player.badges}")


if __name__ == "__main__":
    main()
