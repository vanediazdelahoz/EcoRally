# Pantalla de entrada: fondo y "presiona Enter"

import pygame
from core.state import State
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, GREEN, YELLOW
from core.utils import load_font

class SplashScreen(State):
    def __init__(self, game):
        super().__init__(game)

        # Fuentes
        self.title_font = load_font("assets/fonts/PressStart2P-Regular.ttf", 50)
        self.subtitle_font = load_font("assets/fonts/PublicPixel.ttf", 20)
        self.instruction_font = load_font("assets/fonts/mc-ten-lowercase-alt.ttf", 30)

        # Fondo del cielo
        self.bg_base = pygame.image.load("assets/images/Sky_sky2.png").convert()
        self.sky_height = self.bg_base.get_height()

        # Capa de árboles con transparencia y escalado proporcional
        self.bg_trees_original = pygame.image.load("assets/images/forest_long.png").convert_alpha()

        desired_width = 600  # ancho deseado
        original_width = self.bg_trees_original.get_width()
        original_height = self.bg_trees_original.get_height()
        scale_factor = desired_width / original_width
        desired_height = int(original_height * scale_factor)

        self.bg_trees = pygame.transform.smoothscale(self.bg_trees_original, (desired_width, desired_height))
        self.trees_height = desired_height
        self.bg_trees_y = self.sky_height - self.trees_height
        self.bg_scroll_x = 0
        self.bg_scroll_speed = 1  # Velocidad de desplazamiento

        # Rectángulo negro debajo de los árboles
        self.black_rect = pygame.Rect(
            0,
            self.bg_trees_y + self.trees_height,
            SCREEN_WIDTH,
            SCREEN_HEIGHT - (self.bg_trees_y + self.trees_height)
        )

        # Título y subtítulo
        self.title = self.title_font.render("EcoRally", True, GREEN)
        self.title_rect = self.title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 5))

        self.subtitle = self.subtitle_font.render("Recicla y Haz la Diferencia", True, YELLOW)
        self.subtitle_rect = self.subtitle.get_rect(center=(SCREEN_WIDTH // 2, (SCREEN_HEIGHT // 5) + 50))

        # Barra verde de instrucción (encima del rectángulo negro)
        self.bar_height = 40
        self.bar_rect = pygame.Rect(0, SCREEN_HEIGHT - 50 - self.bar_height, SCREEN_WIDTH, self.bar_height)
        self.bar_color = GREEN

        # Texto de instrucción dentro de la barra verde
        self.press_enter = self.instruction_font.render("Presiona ENTER para continuar", True, WHITE)
        self.press_enter_rect = self.press_enter.get_rect(
            midleft=(20, SCREEN_HEIGHT - 55 - (self.bar_height // 2))
        )

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            from states.main_menu import MainMenu
            new_state = MainMenu(self.game)
            self.game.state_stack.append(new_state)

    def update(self):
        self.bg_scroll_x -= self.bg_scroll_speed
        if self.bg_scroll_x <= -self.bg_trees.get_width():
            self.bg_scroll_x = 0

    def render(self, screen):
        # Fondo del cielo
        screen.blit(self.bg_base, (0, 0))

        # Árboles en scroll horizontal
        screen.blit(self.bg_trees, (self.bg_scroll_x, self.bg_trees_y))
        screen.blit(self.bg_trees, (self.bg_scroll_x + self.bg_trees.get_width(), self.bg_trees_y))

        # Rectángulo negro debajo de los árboles
        pygame.draw.rect(screen, BLACK, self.black_rect)

        # Título y subtítulo encima del fondo
        screen.blit(self.title, self.title_rect)
        screen.blit(self.subtitle, self.subtitle_rect)

        # Barra verde con instrucción
        pygame.draw.rect(screen, self.bar_color, self.bar_rect)
        screen.blit(self.press_enter, self.press_enter_rect)

