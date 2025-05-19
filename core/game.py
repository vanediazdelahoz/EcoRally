# Loop principal y manejador de estados

import pygame
from core.settings import FPS, SCREEN_WIDTH, SCREEN_HEIGHT
from core.state import State
from states.splash_screen import SplashScreen

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("EcoRally")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state_stack = []
        self.load_states()

    def load_states(self):
        splash_screen = SplashScreen(self)
        self.state_stack.append(splash_screen)

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.render()
            pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.state_stack[-1].handle_event(event)

    def update(self):
        self.state_stack[-1].update()

    def render(self):
        self.state_stack[-1].render(self.screen)