# Estado de menú principal

import pygame
from core.state import State
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, MARRON
from core.utils import load_font
from core.background_manager import BackgroundManager
from core.effects import TransitionEffect

class MainMenu(State):
    def __init__(self, game):
        super().__init__(game)
        pygame.mouse.set_visible(False)
        
        self.background = BackgroundManager()
        
        self.transition = TransitionEffect(0.15)
        self.transition.start_fade_in()
        
        self.transitioning = False
        self.can_handle_input = True
        
        # Opciones del menú
        self.options = ["Jugar", "Información", "Salir"]
        self.selected_option = 0
        
        # Fuentes
        self.title_font = load_font("assets/fonts/PressStart2P-Regular.ttf", 45)
        self.subtitle_font = load_font("assets/fonts/MinecraftStandard.otf", 16)
        self.menu_font = load_font("assets/fonts/PressStart2P-Regular.ttf", 20)
        
        self.title_x_position = 170
        self.title_y_position = 100
        self.subtitle_spacing = 8
        
        self.cartel_x_position = SCREEN_WIDTH - 700
        self.cartel_y_position = 120
        self.cartel_width = 850
        self.cartel_height = 750
        
        self.menu_text_offset_y = -20
        
        self.title_surface = self._render_text_with_shadow(self.title_font, "ECORALLY", WHITE)
        self.subtitle_surface = self._render_text_with_shadow(self.subtitle_font, "¡Recicla y Haz la Diferencia!", WHITE)
        
        self.title_rect = pygame.Rect(self.title_x_position, self.title_y_position, 
                                     self.title_surface.get_width(), self.title_surface.get_height())
        self.subtitle_rect = pygame.Rect(self.title_x_position, 
                                        self.title_y_position + self.title_surface.get_height() + self.subtitle_spacing,
                                        self.subtitle_surface.get_width(), self.subtitle_surface.get_height())
        
        try:
            cartel_original = pygame.image.load("assets/images/selection/multi_wooden_signpost.png").convert_alpha()
            
            original_width = cartel_original.get_width()
            original_height = cartel_original.get_height()
            
            scale_x = self.cartel_width / original_width
            scale_y = self.cartel_height / original_height
            scale = min(scale_x, scale_y)
            
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            
            self.cartel_image = pygame.transform.scale(cartel_original, (new_width, new_height))
            
            self.cartel_width = new_width
            self.cartel_height = new_height
            
        except Exception as e:
            self.cartel_image = pygame.Surface((self.cartel_width, self.cartel_height))
            self.cartel_image.fill((100, 100, 100))
        
        self.cartel_rect = pygame.Rect(self.cartel_x_position, self.cartel_y_position, 
                                      self.cartel_width, self.cartel_height)
        
        section_height = self.cartel_height // 5
        self.menu_positions = []
        for i in range(3):
            section_center_y = self.cartel_y_position + (i * section_height) + (section_height // 2) + self.menu_text_offset_y + 110
            self.menu_positions.append((self.cartel_rect.centerx, section_center_y))
    
    def _render_text_with_shadow(self, font, text, text_color, shadow_color=(128, 128, 128), shadow_offset=2):
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
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self._start_transition(self._handle_menu_selection)
            elif event.key == pygame.K_ESCAPE:
                self._start_transition(lambda: self.game.state_stack.pop())
    
    def _start_transition(self, callback):
        self.transitioning = True
        self.can_handle_input = False
        self.transition.start_fade_out(callback)
    
    def _handle_menu_selection(self):
        selected = self.options[self.selected_option]
        if selected == "Jugar":
            from states.mode_selection import ModeSelection
            self.game.state_stack.append(ModeSelection(self.game))
        elif selected == "Información":
            from states.information import Information
            self.game.state_stack.append(Information(self.game))
        elif selected == "Salir":
            self.game.quit()
    
    def update(self, dt):
        self.background.update(dt)
        self.transition.update(dt)
        
        if not self.transition.active and self.transitioning:
            self.transitioning = False
            self.can_handle_input = True
    
    def render(self, screen):
        self.background.render(screen)
        
        screen.blit(self.title_surface, self.title_rect)
        screen.blit(self.subtitle_surface, self.subtitle_rect)
        
        screen.blit(self.cartel_image, self.cartel_rect)
        
        for i, option in enumerate(self.options):
            is_selected = (i == self.selected_option)
            
            if is_selected:
                text_surface = self._render_text_with_shadow(self.menu_font, option, WHITE, (120, 120, 120))
            else:
                text_surface = self._render_text_with_shadow(self.menu_font, option, MARRON)
            
            text_rect = text_surface.get_rect(center=self.menu_positions[i])
            screen.blit(text_surface, text_rect)
        
        self.transition.render(screen)