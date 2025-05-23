class Square:
    def __init__(self, id, type):
        self.id = id
        self.type = type
        self.players = []
        self.next_squares = []
        self.recycle = False

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
            print(f"+3 de basura con id {self.id}")
            player.collect_trash(3)
