# Menú principal (jugar, info, créditos, etc.)

import pygame
from core.state import State
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, GREEN

class MainMenu(State):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, 48)
        self.options = ["Jugar", "Créditos", "Más Información", "Salir"]
        self.selected = 0
        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.background.fill(BLACK)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self.select_option()

    def select_option(self):
        if self.selected == 0:  # Jugar
            from states.mode_selection import ModeSelection
            new_state = ModeSelection(self.game)
            self.game.state_stack.append(new_state)
        elif self.selected == 1:  # Créditos
            from states.credits import Credits
            new_state = Credits(self.game)
            self.game.state_stack.append(new_state)
        elif self.selected == 2:  # Más Información
            from states.info_screen import InfoScreen
            new_state = InfoScreen(self.game)
            self.game.state_stack.append(new_state)
        elif self.selected == 3:  # Salir
            self.game.running = False

    def update(self):
        pass

    def render(self, screen):
        screen.blit(self.background, (0, 0))
        for i, option in enumerate(self.options):
            color = GREEN if i == self.selected else WHITE
            text = self.font.render(option, True, color)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 60))
            screen.blit(text, rect)