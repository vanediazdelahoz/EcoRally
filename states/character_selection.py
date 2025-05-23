import pygame
from core.state import State
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from core.config import config  # Importar instancia config

class CharacterSelection(State):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont("Arial", 30)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.state_stack.pop()
    
    def update(self, dt):
        pass
    
    def render(self, screen):
        screen.fill((30, 30, 30))
        mode_text = "Modo: Jugador vs Máquina" if config.machine_mode else "Modo: Jugador vs Jugador"
        text_surface = self.font.render(mode_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text_surface, text_rect)
