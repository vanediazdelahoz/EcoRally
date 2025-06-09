# Clase base para representar un estado del juego

class State:
    def __init__(self, game):
        self.game = game

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def render(self, screen):
        pass