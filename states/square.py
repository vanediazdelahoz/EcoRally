import random


class Square:
    def __init__(self, id, type):
        self.id = id
        self.type = type
        self.players = []
        self.next_squares = []
        self.recycle = False
        self.timeout = 0

    def add_player(self, player):
        self.players.append(player)

    def add_next_square(self, square):
        self.next_squares.append(square)

    def set_recycling_point(self):
        self.recycle = True

    def effect(self, player):
        # Basado en el tipo de casilla (designado por color) se activa un efecto
        if self.type == "blue":
            print("Casilla azul")
        elif self.type == "green":
            print(f"Casilla verde: Ganas 3 de basura")
            player.collect_trash(3)
        elif self.type == "red":
            print(f"Oh no… ¡Casilla roja! Has perdido 3 de basura.")
            player.collect_trash(-3)
        elif self.type == "purple":
            print("¡Casilla morada! Lanza el dado bonus:")
            dice = random.randint(1, 6)
            dicepurple = dice * 2
            print(f"Dado bonus {dice} →  +{dicepurple} de basura")
            player.collect_trash(dicepurple)
