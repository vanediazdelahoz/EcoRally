# states/character_selection.py
import pygame
from core.config import config
from core.state import State
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from core.utils import load_font


class CharacterSelection(State):
    def __init__(self, game):
        super().__init__(game)

        self.font_title = load_font("assets/fonts/PublicPixel.ttf", 28)
        self.font_button = load_font("assets/fonts/mc-ten-lowercase-alt.ttf", 14)

        self.title_text = self.font_title.render("SELECCIONA TU PERSONAJE", True, (255, 255, 255))
        self.title_rect = self.title_text.get_rect(center=(SCREEN_WIDTH // 2, 130))

        try:
            self.bg_imagec = pygame.image.load("assets/images/clouds_twilight.png").convert_alpha()
            self.bg_imagec = pygame.transform.scale(self.bg_imagec, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.bg_scrollc = 0
            self.bg_widthc = self.bg_imagec.get_width()
        except Exception as e:
            print("Error cargando nubes:", e)
            self.bg_imagec = None

        try:
            self.bg_image = pygame.image.load("assets/images/forest.png").convert_alpha()
            self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.bg_scroll = 0
            self.bg_width = self.bg_image.get_width()
        except Exception as e:
            print("Error cargando fondo bosque:", e)
            self.bg_image = None

        try:
            self.overlay_image = pygame.image.load("assets/images/filtro_naranja.png").convert_alpha()
            self.overlay_image = pygame.transform.scale(self.overlay_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception as e:
            print("Error cargando imagen de filtro:", e)
            self.overlay_image = None


        self.cloud_speed = 30
        self.forest_speed = 50

        # Personajes escalados
        character_paths = [
            "assets/personajes/Abuelita/abuelita1.png",
            "assets/personajes/IndigenaMono/IndioConMono1.png",
            "assets/personajes/SillaDeRuedas/SillaDeRuedas1.png",
            "assets/personajes/Luis/Luis1.png"
        ]

        self.characters = []
        i = 0
        for path in character_paths:
            try:
                if i < 2 :
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.scale(img, (99, 180))  # Escalar a tamaño uniforme
                    self.characters.append(img)
                else:
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.scale(img, (107, 153))  # Escalar a tamaño uniforme
                    self.characters.append(img)
                i += 1
            except Exception as e:
                print(f"Error cargando personaje en {path}:", e)


        self.selected_j1 = 0
        self.selected_j2 = 1

        vertical_offset = 40

        # Paneles más pequeños
        self.panel_width = 141
        self.panel_height = 213
        spacing = 160  # más separación entre paneles
        total_width = self.panel_width * 2 + spacing
        start_x = (SCREEN_WIDTH - total_width) // 2

        self.j1_rect = pygame.Rect(start_x, 160 + vertical_offset, self.panel_width, self.panel_height)
        self.j2_rect = pygame.Rect(start_x + self.panel_width + spacing, 160 + vertical_offset, self.panel_width, self.panel_height)

        button_w, button_h = 130, 40
        self.button_j1 = pygame.Rect(self.j1_rect.centerx - button_w // 2, self.j1_rect.bottom + 15, button_w, button_h)
        self.button_j2 = pygame.Rect(self.j2_rect.centerx - button_w // 2, self.j2_rect.bottom + 15, button_w, button_h)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.state_stack.pop()
            elif event.key == pygame.K_a:
                self.selected_j1 = (self.selected_j1 - 1) % len(self.characters)
            elif event.key == pygame.K_d:
                self.selected_j1 = (self.selected_j1 + 1) % len(self.characters)
            elif event.key == pygame.K_LEFT:
                self.selected_j2 = (self.selected_j2 - 1) % len(self.characters)
            elif event.key == pygame.K_RIGHT:
                self.selected_j2 = (self.selected_j2 + 1) % len(self.characters)

            elif event.key == pygame.K_f:
                if self.selected_j1 != self.selected_j2:  # Opcional: evitar que seleccionen el mismo
                    config.characters = [self.selected_j1, None]
                    print(f"Jugador 1 seleccionó personaje {self.selected_j1} con F")

            elif event.key == pygame.K_RETURN:
                if self.selected_j1 != self.selected_j2:  # Opcional
                    if config.characters == [] or config.characters[0] is not None:
                        config.characters = [config.characters[0], self.selected_j2]
                    else:
                        config.characters = [None, self.selected_j2]
                    print(f"Jugador 2 seleccionó personaje {self.selected_j2} con Enter")

                if None not in config.characters:
                    print("Ambos jugadores seleccionaron. Continuar...")

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.button_j1.collidepoint(event.pos):
                print(f"Jugador 1 seleccionó personaje {self.selected_j1} con click")
            elif self.button_j2.collidepoint(event.pos):
                print(f"Jugador 2 seleccionó personaje {self.selected_j2} con click")

    def update(self, dt):
        if self.bg_image:
            self.bg_scroll -= self.forest_speed * dt
            if self.bg_scroll <= -self.bg_width:
                self.bg_scroll = 0

        if self.bg_imagec:
            self.bg_scrollc -= self.cloud_speed * dt
            if self.bg_scrollc <= -self.bg_widthc:
                self.bg_scrollc = 0

    def _draw_arrow(self, surface, x, y, direction="left", color=(101, 67, 33)):  # marrón oscuro
        size = 20
        if direction == "left":
            points = [(x, y), (x + size, y - size), (x + size, y + size)]
        else:
            points = [(x, y), (x - size, y - size), (x - size, y + size)]
        pygame.draw.polygon(surface, color, points)

    def render(self, screen):
        if self.bg_imagec:
            screen.blit(self.bg_imagec, (self.bg_scrollc, 0))
            screen.blit(self.bg_imagec, (self.bg_scrollc + self.bg_widthc, 0))

        if self.overlay_image:
            self.overlay_image.set_alpha(240)
            screen.blit(self.overlay_image, (0, 0))
        
        if self.bg_image:
            screen.blit(self.bg_image, (self.bg_scroll, 0))
            screen.blit(self.bg_image, (self.bg_scroll + self.bg_width, 0))

        if self.overlay_image:
            self.overlay_image.set_alpha(60)
            screen.blit(self.overlay_image, (0, 0))


        screen.blit(self.title_text, self.title_rect)

        pygame.draw.rect(screen, (50, 50, 50), self.j1_rect, border_radius=10)
        pygame.draw.rect(screen, (50, 50, 50), self.j2_rect, border_radius=10)

        char_j1 = self.characters[self.selected_j1]
        char_rect_j1 = char_j1.get_rect(center=self.j1_rect.center)
        screen.blit(char_j1, char_rect_j1)

        char_j2 = self.characters[self.selected_j2]
        char_j2_flipped = pygame.transform.flip(char_j2, True, False)
        char_rect_j2 = char_j2_flipped.get_rect(center=self.j2_rect.center)
        screen.blit(char_j2_flipped, char_rect_j2)


        # Flechas marrón oscuro
        self._draw_arrow(screen, self.j1_rect.left - 35, self.j1_rect.centery, "left")
        self._draw_arrow(screen, self.j1_rect.right + 35, self.j1_rect.centery, "right")
        self._draw_arrow(screen, self.j2_rect.left - 35, self.j2_rect.centery, "left")
        self._draw_arrow(screen, self.j2_rect.right + 35, self.j2_rect.centery, "right")

        pygame.draw.rect(screen, (50, 50, 50), self.button_j1, border_radius=6)
        btn_text_j1 = self.font_button.render("SELECCIONAR", True, (255, 255, 255))
        btn_rect_j1 = btn_text_j1.get_rect(center=self.button_j1.center)
        screen.blit(btn_text_j1, btn_rect_j1)

        pygame.draw.rect(screen, (50, 50, 50), self.button_j2, border_radius=6)
        btn_text_j2 = self.font_button.render("SELECCIONAR", True, (255, 255, 255))
        btn_rect_j2 = btn_text_j2.get_rect(center=self.button_j2.center)
        screen.blit(btn_text_j2, btn_rect_j2)



