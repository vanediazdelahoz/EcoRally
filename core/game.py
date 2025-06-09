# Clase principal del juego

import pygame
from core.settings import FPS, SCREEN_WIDTH, SCREEN_HEIGHT
from states.splash_screen import SplashScreen
import ctypes

class Game:
    def __init__(self):

        user32 = ctypes.windll.user32

        self.display_width = user32.GetSystemMetrics(0)
        self.display_height = user32.GetSystemMetrics(1)
        
        self.screen = pygame.display.set_mode((self.display_width, self.display_height), pygame.NOFRAME)
        self.base_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        pygame.display.set_caption("EcoRally")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state_stack = []
        self.load_states()
        pygame.mixer.init()
        pygame.mixer.music.load("./assets/music/yeah_yuh.wav")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(loops=-1)

    def quit(self):
        pygame.quit()
        exit()

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
        dt = self.clock.get_time() / 1000
        self.state_stack[-1].update(dt)

    def render(self):
        # 1. Renderizar todo en la superficie lógica
        self.state_stack[-1].render(self.base_surface)

        # 2. Escalar conservando la proporción
        scale_w = self.display_width / SCREEN_WIDTH
        scale_h = self.display_height / SCREEN_HEIGHT
        scale = min(scale_w, scale_h)

        new_width = int(SCREEN_WIDTH * scale)
        new_height = int(SCREEN_HEIGHT * scale)

        scaled_surface = pygame.transform.smoothscale(self.base_surface, (new_width, new_height))

        # 3. Rellenar pantalla de negro
        self.screen.fill((0, 0, 0))

        # 4. Centrar la superficie escalada
        x = (self.display_width - new_width) // 2
        y = (self.display_height - new_height) // 2
        self.screen.blit(scaled_surface, (x, y))
