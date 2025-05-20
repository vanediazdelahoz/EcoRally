# Pantalla de entrada: fondo y "presiona Enter"

import pygame
from core.state import State
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, GREEN, YELLOW, GREY
from core.utils import load_font


def render_text_with_outline(font, text, text_color, outline_color):
    base = font.render(text, True, text_color)
    size = base.get_size()

    margin = 10
    outline_surface = pygame.Surface((size[0] + 2 * margin, size[1] + 2 * margin), pygame.SRCALPHA)

    # Contorno más grueso arriba e izquierda
    light_outline_offsets = [
        (dx, dy)
        for dx in range(-3, 1)
        for dy in range(-3, 1)
        if not (dx == 0 and dy == 0)
    ]

    # Sombra más gruesa abajo y derecha
    heavy_shadow_offsets = [
        (dx, dy)
        for dx in range(1, 8)
        for dy in range(1, 8)
    ]

    # Pintar contorno superior/izquierdo
    for dx, dy in light_outline_offsets:
        outline_surface.blit(font.render(text, True, outline_color), (margin + dx, margin + dy))

    # Pintar sombra inferior/derecha
    for dx, dy in heavy_shadow_offsets:
        outline_surface.blit(font.render(text, True, outline_color), (margin + dx, margin + dy))

    # Pintar texto encima
    outline_surface.blit(base, (margin, margin))

    return outline_surface



class SplashScreen(State):
    def __init__(self, game):
        super().__init__(game)

        # Fuentes
        self.title_font = load_font("assets/fonts/PressStart2P-Regular.ttf", 55)
        self.subtitle_font = load_font("assets/fonts/PublicPixel.ttf", 20)
        self.instruction_font = load_font("assets/fonts/mc-ten-lowercase-alt.ttf", 25)

        # Fondo del cielo
        self.bg_base = pygame.image.load("assets/images/sky.png").convert()
        self.sky_height = self.bg_base.get_height()

        # Capa de árboles con transparencia y escalado proporcional
        self.bg_trees_original = pygame.image.load("assets/images/forest_long.png").convert_alpha()

        desired_width = 650  # ancho deseado
        original_width = self.bg_trees_original.get_width()
        original_height = self.bg_trees_original.get_height()
        scale_factor = desired_width / original_width
        desired_height = int(original_height * scale_factor)

        self.bg_trees = pygame.transform.smoothscale(self.bg_trees_original, (desired_width, desired_height))
        self.trees_height = desired_height
        self.bg_trees_y = self.sky_height - self.trees_height

        self.bg_scroll_x = 0
        self.bg_scroll_speed = 0.5  # Velocidad de desplazamiento

        # Rectángulo negro debajo de los árboles
        self.grey_rect = pygame.Rect(
            0,
            self.bg_trees_y + self.trees_height,
            SCREEN_WIDTH,
            SCREEN_HEIGHT - (self.bg_trees_y + self.trees_height)
        )

        # Título y subtítulo
        self.title = render_text_with_outline(self.title_font, "EcoRally", GREEN, BLACK)
        self.title_rect = self.title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4.5))

        self.subtitle = render_text_with_outline(self.subtitle_font, "Recicla y Haz la Diferencia", YELLOW, BLACK)
        self.subtitle_rect = self.subtitle.get_rect(center=(SCREEN_WIDTH // 2, (SCREEN_HEIGHT // 4) + 32))

        # Barra verde de instrucción (encima del rectángulo negro)
        self.bar_height = 40
        self.bar_rect = pygame.Rect(0, SCREEN_HEIGHT - 40 - self.bar_height, SCREEN_WIDTH, self.bar_height)
        self.bar_color = GREEN

        # Texto de instrucción dentro de la barra verde
        self.press_enter = self.instruction_font.render("Presiona ENTER para continuar", True, WHITE)
        self.press_enter_rect = self.press_enter.get_rect(
            midleft=(20, SCREEN_HEIGHT - 45 - (self.bar_height // 2)))
        
        # Animación del perro desde sprite sheet
        sprite_sheet = pygame.image.load("assets/images/dog_walk.png").convert_alpha()
        self.dog_frames = []
        frame_width = 48
        frame_height = 48
        for i in range(6):
            frame = sprite_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            self.dog_frames.append(frame)

        self.current_dog_frame = 0
        self.dog_animation_timer = 0
        self.dog_animation_speed = 0.07  # segundos por frame

        # Cargar imagen de nubes y escalar para cubrir el alto del cielo
        self.clouds_original = pygame.image.load("assets/images/clouds.png").convert_alpha()

        original_width = self.clouds_original.get_width()
        original_height = self.clouds_original.get_height()

        clouds_scale_factor = self.sky_height / original_height
        scaled_width = int(original_width * clouds_scale_factor)
        scaled_height = self.sky_height

        self.clouds = pygame.transform.smoothscale(self.clouds_original, (scaled_width, scaled_height))
        self.clouds.set_alpha(50)  # Valor entre 0 (transparente) y 255 (opaco)

        # Scroll horizontal de las nubes (más lento que los árboles)
        self.clouds_scroll_x = 0
        self.clouds_scroll_speed = 8



    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            from states.main_menu import MainMenu
            new_state = MainMenu(self.game)
            self.game.state_stack.append(new_state)

    def update(self, dt):
        self.bg_scroll_x -= self.bg_scroll_speed
        width = self.bg_trees.get_width()
        # Usar módulo para mantener el scroll_x siempre entre -width y 0
        if self.bg_scroll_x <= -width:
            self.bg_scroll_x += width

        # Actualizar animación del perro
        self.dog_animation_timer += dt
        if self.dog_animation_timer >= self.dog_animation_speed:
            self.dog_animation_timer = 0
            self.current_dog_frame = (self.current_dog_frame + 1) % len(self.dog_frames)

        self.clouds_scroll_x -= self.clouds_scroll_speed * dt
        clouds_width = self.clouds.get_width()
        if self.clouds_scroll_x <= -clouds_width:
            self.clouds_scroll_x += clouds_width

    def render(self, screen):
        screen.blit(self.bg_base, (0, 0))
        width = self.bg_trees.get_width()

        # Dibujar nubes con repetición horizontal
        clouds_width = self.clouds.get_width()
        x = self.clouds_scroll_x
        while x < SCREEN_WIDTH:
            screen.blit(self.clouds, (x, 0))
            x += clouds_width


        # Dibujar tantas veces como sea necesario para cubrir toda la pantalla
        x = self.bg_scroll_x
        while x < SCREEN_WIDTH:
            screen.blit(self.bg_trees, (x, self.bg_trees_y))
            x += width

        pygame.draw.rect(screen, GREY, self.grey_rect)
        screen.blit(self.title, self.title_rect)
        screen.blit(self.subtitle, self.subtitle_rect)
        pygame.draw.rect(screen, self.bar_color, self.bar_rect)
        screen.blit(self.press_enter, self.press_enter_rect)

        dog_image = self.dog_frames[self.current_dog_frame]

        # Escalar el perro
        scale_factor = 1.35
        new_width = int(dog_image.get_width() * scale_factor)
        new_height = int(dog_image.get_height() * scale_factor)
        scaled_dog = pygame.transform.smoothscale(dog_image, (new_width, new_height))

        dog_rect = scaled_dog.get_rect()
        dog_x = (SCREEN_WIDTH // 2) - (dog_rect.width // 2)
        dog_y = self.bg_trees_y + self.trees_height - dog_rect.height
        screen.blit(scaled_dog, (dog_x, dog_y))
