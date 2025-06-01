# states/mode_selection.py

import pygame
from core.config import config
from core.state import State
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from core.utils import load_font


class ModeSelection(State):
    def __init__(self, game):
        super().__init__(game)
        pygame.mouse.set_visible(False)

        self.font_title = load_font("assets/fonts/PublicPixel.ttf", 28)
        self.font_button_main = load_font("assets/fonts/PublicPixel.ttf", 16)
        self.font_button_sub = load_font("assets/fonts/PublicPixel.ttf", 12)

        self.title_text = self.font_title.render("SELECCIONAR MODO", True, (255, 255, 255))
        self.title_rect = self.title_text.get_rect(center=(SCREEN_WIDTH // 2, 160))

        # cargar las nuves
        try:
            self.bg_imagec = pygame.image.load("assets/images/clouds_lulo.png").convert_alpha()
            self.bg_imagec = pygame.transform.scale(self.bg_imagec, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.bg_scrollc = 0
            self.bg_widthc = self.bg_imagec.get_width()
        except Exception as e:
            print("Error cargando nuves de fondo:", e)
            self.bg_imagec = None



        # Cargar imagen del fondo de árboles
        try:
            self.bg_image = pygame.image.load("assets/images/forest_short.png").convert_alpha()
            self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.bg_scroll = 0
            self.bg_width = self.bg_image.get_width()
        except Exception as e:
            print("Error cargando fondo de árboles:", e)
            self.bg_image = None

        self.cloud_speed = 30
        self.forest_speed = 50

        
        
        self.selected = 0
        self.options = [
            {"main": "PLAYER VS PLAYER", "sub": "Clásico 1v1", "color": (0, 255, 0)},
            {"main": "PLAYER VS BOT", "sub": "Contra la IA", "color": (0, 240, 255)}
        ]

        self.button_width = 340
        self.button_height = 90
        self.button_spacing = 40

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.state_stack.pop()
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self._select_mode()

    
    def _select_mode(self):
        from core.config import config
        config.machine_mode = (self.selected == 1)  # PvE si el índice seleccionado es 1
        print(f"Modo guardado en config: {'Jugador vs Máquina' if config.machine_mode else 'Jugador vs Jugador'}")

        from states.character_selection import CharacterSelection
        self.game.state_stack.append(CharacterSelection(self.game))


    def update(self, dt):
        # Mover el fondo de árboles
        if self.bg_image:
            self.bg_scroll -= self.forest_speed * dt
            if self.bg_scroll <= -self.bg_width:
                self.bg_scroll = 0

        # Mover el fondo de nubes
        if self.bg_imagec:
            self.bg_scrollc -= self.cloud_speed * dt
            if self.bg_scrollc <= -self.bg_widthc:
                self.bg_scrollc = 0


    def render(self, screen):
        # Dibujar fondo con scroll
        if self.bg_imagec:
            screen.blit(self.bg_imagec, (self.bg_scrollc, 0))
            screen.blit(self.bg_imagec, (self.bg_scrollc + self.bg_widthc, 0))

        if self.bg_image:
            screen.blit(self.bg_image, (self.bg_scroll, 0))
            screen.blit(self.bg_image, (self.bg_scroll + self.bg_width, 0))
        

        # Título
        screen.blit(self.title_text, self.title_rect)

        # Botones en línea
        total_width = (self.button_width * 2) + self.button_spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        y = SCREEN_HEIGHT // 2

        for i, option in enumerate(self.options):
            x = start_x + i * (self.button_width + self.button_spacing)
            rect = pygame.Rect(x, y, self.button_width, self.button_height)
            border_color = option["color"] if i == self.selected else (58, 58, 58)
            border_thickness = 3 if i == self.selected else 2
            pygame.draw.rect(screen, (30, 30, 30), rect, border_radius=8)
            pygame.draw.rect(screen, border_color, rect, border_thickness, border_radius=8)

            if i == self.selected:
                glow = pygame.Surface((self.button_width, self.button_height), pygame.SRCALPHA)
                pygame.draw.rect(glow, (*option["color"], 40), glow.get_rect(), border_radius=8)
                screen.blit(glow, (x, y))

            # Textos
            main_text = self.font_button_main.render(option["main"], True, (255, 255, 255))
            main_rect = main_text.get_rect(center=(x + self.button_width // 2, y + 30))

            sub_text = self.font_button_sub.render(option["sub"], True, (160, 160, 160))
            sub_rect = sub_text.get_rect(center=(x + self.button_width // 2, y + 65))

            screen.blit(main_text, main_rect)
            screen.blit(sub_text, sub_rect)
