# states/mode_selection.py
import pygame
from core.config import config
from core.state import State
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, MARRON
from core.utils import load_font
from core.background_manager import BackgroundManager
from core.effects import TransitionEffect

class ModeSelection(State):
    def __init__(self, game):
        super().__init__(game)
        pygame.mouse.set_visible(False)
        
        # Gestor de fondo con fondo1.png
        self.background = BackgroundManager()
        
        # Efecto de transición
        self.transition = TransitionEffect(0.15)
        self.transition.start_fade_in()
        
        # Control de transición - INICIALIZAR PRIMERO
        self.transitioning = False
        self.can_handle_input = True
        
        # Fuentes
        self.font_title = load_font("assets/fonts/PublicPixel.ttf", 32)
        self.font_button_main = load_font("assets/fonts/PublicPixel.ttf", 18)
        self.font_button_sub = load_font("assets/fonts/PublicPixel.ttf", 13)
        
        # === CONFIGURACIÓN DE POSICIONES (AJUSTABLE) ===
        self.title_y_position = 160   # Posición Y del título (ajustable)
        self.carteles_y_position = 250  # Posición Y de los carteles (ajustable)
        self.cartel_width = 400      # Ancho de cada cartel (ajustable)
        self.cartel_height = 400    # Alto de cada cartel (ajustable)
        self.carteles_spacing = 30 # Espaciado entre carteles (ajustable)
        self.text_offset_y = 140     # Offset Y del texto sobre carteles (ajustable)
        
        # Título CON SOMBREADO GRIS
        self.title_surface = self._render_text_with_shadow(self.font_title, "SELECCIONAR MODO", WHITE)
        self.title_rect = self.title_surface.get_rect(center=(SCREEN_WIDTH // 2, self.title_y_position))
        
        # Opciones del menú
        self.selected = 0
        self.options = [
            {"main": "PLAYER VS PLAYER", "sub": "Clásico 1v1"},
            {"main": "PLAYER VS BOT", "sub": "Contra la IA"}
        ]
        
        # Cargar imagen del cartel modo RESPETANDO PROPORCIONES
        try:
            modo_original = pygame.image.load("assets/images/landscape/modo.png").convert_alpha()
            
            # Calcular escala manteniendo proporción
            original_width = modo_original.get_width()
            original_height = modo_original.get_height()
            
            # Calcular escala para que quepa en el tamaño deseado
            scale_x = self.cartel_width / original_width
            scale_y = self.cartel_height / original_height
            scale = min(scale_x, scale_y)  # Usar la menor para mantener proporción
            
            # Calcular nuevas dimensiones manteniendo proporción
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            
            self.modo_image = pygame.transform.scale(modo_original, (new_width, new_height))
            
            # Actualizar dimensiones reales del cartel
            self.cartel_width = new_width
            self.cartel_height = new_height
            
        except Exception as e:
            print(f"Error cargando modo.png: {e}")
            # Crear rectángulo como fallback
            self.modo_image = pygame.Surface((self.cartel_width, self.cartel_height))
            self.modo_image.fill((100, 100, 100))
        
        # Calcular posiciones de los carteles
        total_width = (self.cartel_width * 2) + self.carteles_spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        self.cartel_positions = []
        for i in range(2):
            cartel_x = start_x + i * (self.cartel_width + self.carteles_spacing)
            self.cartel_positions.append((cartel_x, self.carteles_y_position))
    
    def _render_text_with_shadow(self, font, text, text_color, shadow_color=(128, 128, 128), shadow_offset=2):
        """Renderiza texto con sombreado gris"""
        shadow_surface = font.render(text, True, shadow_color)
        text_surface = font.render(text, True, text_color)
        
        combined_width = text_surface.get_width() + shadow_offset
        combined_height = text_surface.get_height() + shadow_offset
        combined_surface = pygame.Surface((combined_width, combined_height), pygame.SRCALPHA)
        
        combined_surface.blit(shadow_surface, (shadow_offset, shadow_offset))
        combined_surface.blit(text_surface, (0, 0))
        
        return combined_surface
    
    def handle_event(self, event):
        if not self.can_handle_input or self.transitioning or self.transition.active:
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._start_transition(lambda: self.game.state_stack.pop())
            elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self._start_transition(self._select_mode)
    
    def _start_transition(self, callback):
        self.transitioning = True
        self.can_handle_input = False
        self.transition.start_fade_out(callback)
    
    def _select_mode(self):
        config.machine_mode = (self.selected == 1)
        print(f"Modo guardado en config: {'Jugador vs Máquina' if config.machine_mode else 'Jugador vs Jugador'}")
        
        from states.character_selection import CharacterSelection
        self.game.state_stack.append(CharacterSelection(self.game))
    
    def update(self, dt):
        self.background.update(dt)
        self.transition.update(dt)
        
        if not self.transition.active and self.transitioning:
            self.transitioning = False
            self.can_handle_input = True
    
    def render(self, screen):
        # Renderizar fondo1.png
        self.background.render(screen)
        
        # Título
        screen.blit(self.title_surface, self.title_rect)
        
        # Carteles y texto
        for i, option in enumerate(self.options):

            is_selected = (i == self.selected)
            cartel_pos = self.cartel_positions[i]

            # Renderizar cartel modo (espejado si es el segundo)
            if i == 1:
                cartel_image = pygame.transform.flip(self.modo_image, True, False)
            else:
                cartel_image = self.modo_image
            
            # Renderizar cartel modo
            cartel_rect = pygame.Rect(cartel_pos[0], cartel_pos[1], self.cartel_width, self.cartel_height)
            screen.blit(cartel_image, cartel_rect)
            
            # Texto encima del cartel
            text_center_x = cartel_rect.centerx
            text_y = cartel_rect.top + self.text_offset_y

            main_color = WHITE if is_selected else MARRON
            sub_color = WHITE if is_selected else MARRON
            main_shadown_color = (100, 100, 100) if is_selected else (128, 128, 128)

            main_text = self._render_text_with_shadow(self.font_button_main, option["main"], main_color, main_shadown_color, 3)
            sub_text = self._render_text_with_shadow(self.font_button_sub, option["sub"], sub_color)


            # Renderizar texto principal
            main_rect = main_text.get_rect(center=(text_center_x, text_y - 15))
            sub_rect = sub_text.get_rect(center=(text_center_x, text_y + 15))

            screen.blit(main_text, main_rect)
            screen.blit(sub_text, sub_rect)
        
        # Renderizar transición
        self.transition.render(screen)

print("ModeSelection rediseñado - carteles modo con proporciones respetadas, fondo1.png, texto blanco")
