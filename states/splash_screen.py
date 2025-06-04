# states/splash_screen.py
import pygame
from core.state import State
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE
from core.utils import load_font
from core.background_manager import BackgroundManager
from core.effects import TransitionEffect

class SplashScreen(State):
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
        self.title_font = load_font("assets/fonts/PressStart2P-Regular.ttf", 48)
        self.subtitle_font = load_font("assets/fonts/MinecraftStandard.otf", 17)
        self.continue_font = load_font("assets/fonts/PressStart2P-Regular.ttf", 23)
        
        # === CONFIGURACIÓN DE POSICIONES (AJUSTABLE) ===
        self.title_y_position = 200  # Posición Y del título (ajustable)
        self.subtitle_spacing = 6  # Espaciado entre título y subtítulo (ajustable)
        self.continue_y_position = SCREEN_HEIGHT - 85  # Posición Y del mensaje (ajustable)
        
        # Textos CON SOMBREADO GRIS
        self.title_surface = self._render_text_with_shadow(self.title_font, "ECORALLY", WHITE)
        self.subtitle_surface = self._render_text_with_shadow(self.subtitle_font, "¡Recicla y Haz la Diferencia!", WHITE)
        self.continue_surface = self._render_text_with_shadow(self.continue_font, "Presiona \"Enter\"", WHITE)
        
        # Calcular posiciones centradas en X
        self.title_rect = self.title_surface.get_rect(center=(SCREEN_WIDTH // 2, self.title_y_position))
        self.subtitle_rect = self.subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, self.title_y_position + self.title_surface.get_height() + self.subtitle_spacing))
        self.continue_rect = self.continue_surface.get_rect(center=(SCREEN_WIDTH // 2, self.continue_y_position))
        
        # Efecto de parpadeo
        self.blink_timer = 0
        self.blink_visible = True
        self.blink_on_duration = 1.5  # tiempo visible (ajustable)
        self.blink_off_duration = 0.5  # tiempo invisible (ajustable)
        self.blink_state = "on"
    
    def _render_text_with_shadow(self, font, text, text_color, shadow_color=(128, 128, 128), shadow_offset=2):
        """Renderiza texto con sombreado gris"""
        # Crear superficie para el texto con sombra
        shadow_surface = font.render(text, True, shadow_color)
        text_surface = font.render(text, True, text_color)
        
        # Crear superficie combinada
        combined_width = text_surface.get_width() + shadow_offset
        combined_height = text_surface.get_height() + shadow_offset
        combined_surface = pygame.Surface((combined_width, combined_height), pygame.SRCALPHA)
        
        # Dibujar sombra primero, luego texto
        combined_surface.blit(shadow_surface, (shadow_offset, shadow_offset))
        combined_surface.blit(text_surface, (0, 0))
        
        return combined_surface
    
    def handle_event(self, event):
        if not self.can_handle_input or self.transitioning or self.transition.active:
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._start_transition(self._go_to_main_menu)
    
    def _start_transition(self, callback):
        self.transitioning = True
        self.can_handle_input = False
        self.transition.start_fade_out(callback)
    
    def _go_to_main_menu(self):
        from states.main_menu import MainMenu
        self.game.state_stack.append(MainMenu(self.game))
    
    def update(self, dt):
        self.background.update(dt)
        self.transition.update(dt)
        
        if not self.transition.active and self.transitioning:
            self.transitioning = False
            self.can_handle_input = True
        
        # Efecto de parpadeo
        self.blink_timer += dt
        if self.blink_state == "on" and self.blink_timer >= self.blink_on_duration:
            self.blink_visible = False
            self.blink_state = "off"
            self.blink_timer = 0
        elif self.blink_state == "off" and self.blink_timer >= self.blink_off_duration:
            self.blink_visible = True
            self.blink_state = "on"
            self.blink_timer = 0
    
    def render(self, screen):
        # Renderizar fondo1.png
        self.background.render(screen)
        
        # Renderizar título y subtítulo (siempre visibles)
        screen.blit(self.title_surface, self.title_rect)
        screen.blit(self.subtitle_surface, self.subtitle_rect)
        
        # Texto parpadeante SIN rectángulo negro de fondo
        if self.blink_visible:
            screen.blit(self.continue_surface, self.continue_rect)
        
        # Renderizar transición
        self.transition.render(screen)

print("SplashScreen rediseñado - fondo1.png, texto blanco sin contorno, posiciones ajustables")
