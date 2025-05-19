# Clase base para todos los estados

class State:
    def __init__(self, game):
        self.game = game

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def render(self, screen):
        pass