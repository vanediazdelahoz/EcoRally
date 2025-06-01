# Pantalla de entrada: fondo y "presiona Enter"

import pygame
from core.state import State
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, GREEN, GREY
from core.utils import load_font

# Constantes
TITLE_TEXT = "EcoRally"
SUBTITLE_TEXT = "Recicla y Haz la Diferencia"
MENU_BUTTON_WIDTH = 200
MENU_BUTTON_HEIGHT = 40
MENU_SPACING = 15

LIGHT_OUTLINE_OFFSETS = [(dx, dy) for dx in range(-3, 1) for dy in range(-3, 1) if (dx, dy) != (0, 0)]
HEAVY_SHADOW_OFFSETS = [(dx, dy) for dx in range(1, 8) for dy in range(1, 8)]


def render_text_with_outline(font, text, text_color, outline_color):
    base = font.render(text, True, text_color)
    size = base.get_size()
    margin = 10
    outline_surface = pygame.Surface((size[0] + 2 * margin, size[1] + 2 * margin), pygame.SRCALPHA)

    for offsets in (LIGHT_OUTLINE_OFFSETS, HEAVY_SHADOW_OFFSETS):
        for dx, dy in offsets:
            outline_surface.blit(font.render(text, True, outline_color), (margin + dx, margin + dy))

    outline_surface.blit(base, (margin, margin))
    return outline_surface


class SplashScreen(State):
    def __init__(self, game):
        super().__init__(game)
        pygame.mouse.set_visible(False)
        
        self.phase = "menu"
        self.options = ["Jugar", "Opciones", "Salir"]
        self.selected_option = 0

        # Fuentes
        self.title_font = load_font("assets/fonts/PressStart2P-Regular.ttf", 55)
        self.subtitle_font = load_font("assets/fonts/PublicPixel.ttf", 20)
        self.menu_font = load_font("assets/fonts/mc-ten-lowercase-alt.ttf", 25)

        # Fondos
        self.bg_base = pygame.image.load("assets/images/sky_nuevo.png").convert()
        self._init_trees()
        self._init_clouds()

        # Títulos (los rects se actualizarán dinámicamente para centrar todo)
        self.title = render_text_with_outline(self.title_font, TITLE_TEXT, GREEN, BLACK)
        self.title_rect = self.title.get_rect()
        self.subtitle = render_text_with_outline(self.subtitle_font, SUBTITLE_TEXT, WHITE, BLACK)
        self.subtitle_rect = self.subtitle.get_rect()

    def _init_trees(self):
        original = pygame.image.load("assets/images/forest_short.png").convert_alpha()
        scale_factor = (650 / original.get_width()) * 1.2
        size = (int(original.get_width() * scale_factor), int(original.get_height() * scale_factor))
        self.bg_trees = pygame.transform.smoothscale(original, size)
        self.bg_scroll_x = 0
        self.bg_scroll_speed = 0.5
        self.bg_trees_y = SCREEN_HEIGHT - size[1]

    def _init_clouds(self):
        original = pygame.image.load("assets/images/sky_clouds.png").convert_alpha()
        # Aquí escalamos a un ancho fijo menor que el ancho pantalla para respetar proporciones y no deformar
        desired_width = SCREEN_WIDTH
        scale_factor = desired_width / original.get_width()
        desired_height = int(original.get_height() * scale_factor)
        self.clouds = pygame.transform.smoothscale(original, (int(desired_width), desired_height))
        self.clouds.set_alpha(50)
        self.clouds_scroll_x = 0
        self.clouds_scroll_speed = 8

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.phase == "menu":
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self._handle_menu_selection()

    def _handle_menu_selection(self):
        selected = self.options[self.selected_option]
        if selected == "Jugar":
            from states.mode_selection import ModeSelection
            self.game.state_stack.append(ModeSelection(self.game))
        elif selected == "Opciones":
            from states.options import Options
            self.game.state_stack.append(Options(self.game))
        elif selected == "Salir":
            self.game.quit()

    def update(self, dt):
        # Scroll horizontal árboles (scroll continuo)
        self.bg_scroll_x -= self.bg_scroll_speed
        if self.bg_scroll_x <= -self.bg_trees.get_width():
            self.bg_scroll_x += self.bg_trees.get_width()

        # Scroll horizontal nubes (scroll continuo)
        self.clouds_scroll_x -= self.clouds_scroll_speed * dt
        if self.clouds_scroll_x <= -self.clouds.get_width():
            self.clouds_scroll_x += self.clouds.get_width()

    def _draw_scrolling_background(self, screen, image, scroll_x, y_pos):
        width = image.get_width()
        x = int(scroll_x)
        while x < SCREEN_WIDTH:
            screen.blit(image, (x, y_pos))
            x += width
        # Extra para cubrir huecos cuando scroll_x es negativo
        if scroll_x < 0:
            screen.blit(image, (x, y_pos))

    def render(self, screen):
        screen.blit(self.bg_base, (0, 0))
        self._draw_scrolling_background(screen, self.clouds, self.clouds_scroll_x, SCREEN_HEIGHT - self.clouds.get_height())
        self._draw_scrolling_background(screen, self.bg_trees, self.bg_scroll_x, self.bg_trees_y)

        # Calcular altura total del bloque (título + subtítulo + espacio + menú)
        title_h = self.title.get_height()
        subtitle_h = self.subtitle.get_height()
        buttons_h = len(self.options) * MENU_BUTTON_HEIGHT + (len(self.options) - 1) * MENU_SPACING

        spacing_title_subtitle = 0  # espacio vertical entre título y subtítulo
        spacing_subtitle_menu = 40   # espacio vertical entre subtítulo y menú

        total_height = title_h + spacing_title_subtitle + subtitle_h + spacing_subtitle_menu + buttons_h

        start_y = (SCREEN_HEIGHT - total_height) // 2

        # Actualizar rects para centrar títulos
        self.title_rect.center = (SCREEN_WIDTH // 2, start_y + title_h // 2)
        self.subtitle_rect.center = (SCREEN_WIDTH // 2, start_y + title_h + spacing_title_subtitle + subtitle_h // 2)

        # Dibujar títulos
        screen.blit(self.title, self.title_rect)
        screen.blit(self.subtitle, self.subtitle_rect)

        # Dibujar menú centrado verticalmente debajo del subtítulo
        self._render_menu(screen, start_y + title_h + spacing_title_subtitle + subtitle_h + spacing_subtitle_menu)

    def _render_menu(self, screen, start_y):
        for i, option in enumerate(self.options):
            is_selected = (i == self.selected_option)
            rect_x = (SCREEN_WIDTH - MENU_BUTTON_WIDTH) // 2
            rect_y = start_y + i * (MENU_BUTTON_HEIGHT + MENU_SPACING)
            button_rect = pygame.Rect(rect_x, rect_y, MENU_BUTTON_WIDTH, MENU_BUTTON_HEIGHT)

            if is_selected:
                # Contorno tipo sombra en esquina inferior derecha (como en los títulos)
                for dx, dy in HEAVY_SHADOW_OFFSETS:
                    shadow_rect = button_rect.move(dx, dy)
                    pygame.draw.rect(screen, BLACK, shadow_rect, border_radius=8)

            # Fondo del botón
            color = GREEN if is_selected else GREY
            pygame.draw.rect(screen, color, button_rect, border_radius=8)

            # Texto centrado verticalmente (real, sin ajuste bruto)
            text_surface = self.menu_font.render(option, True, WHITE)
            text_rect = text_surface.get_rect(center=button_rect.center)
            screen.blit(text_surface, text_rect)
