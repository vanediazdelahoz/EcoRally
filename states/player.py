class Player:
    def __init__(self, character):
        self.character = character
        self.position = None
        self.trash = 0
        self.badges = 0

    def move_to(self, square):
        if self.position:
            self.position.players.remove(self)
        self.position = square
        square.add_player(self)

    def collect_trash(self, amount):
        self.trash += amount

    def try_recycle(self):
        if self.trash >= 20:
            self.trash = self.trash - 20
            self.badges += 1
            print("Insignia obtenida")
        else:
            print("No hay suficiente basura")
