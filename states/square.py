# Define las casillas del tablero

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

    def effect(self, player, silent_mode=False):
        if self.type == "green":
            player.collect_trash(3)
        elif self.type == "red":
            player.collect_trash(-3)
        elif self.type == "purple":
            dice = random.randint(1, 6)
            dicepurple = dice * 2
            player.collect_trash(dicepurple)