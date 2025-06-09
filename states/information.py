# Muestra texto informativo con scroll

import pygame
from core.state import State
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, MARRON, BLACK
from core.utils import load_font
from core.background_manager import BackgroundManager
from core.effects import TransitionEffect

class Information(State):
    def __init__(self, game):
        super().__init__(game)
        pygame.mouse.set_visible(False)
        
        self.background = BackgroundManager()
        
        self.transition = TransitionEffect(0.15)
        self.transition.start_fade_in()
        
        self.transitioning = False
        self.can_handle_input = True
        
       # Configuración del texto
        self.title = "Información"
        with open("states/info.txt", "r", encoding="utf-8") as f:
            self.content = f.read()

        # Fuentes
        self.title_font = load_font("assets/fonts/PressStart2P-Regular.ttf", 32)
        self.text_font = load_font("assets/fonts/PublicPixel.ttf", 12)
        self.instruction_font = load_font("assets/fonts/PressStart2P-Regular.ttf", 14)
        
        self.text_area_x = 80
        self.text_area_y = 120
        self.text_area_width = SCREEN_WIDTH - 160
        self.text_area_height = SCREEN_HEIGHT - 200
        
        self.scroll_offset = 0
        self.scroll_speed = 8
        self.line_height = 20
        
        self.scroll_timer = 0
        self.scroll_delay = 30
        
        self.lines = self._wrap_text(self.content, self.text_area_width - 150)
        
        total_content_height = len(self.lines) * self.line_height
        self.max_scroll = max(0, total_content_height - self.text_area_height + 80)
        
        self.title_surface = self._render_text_with_shadow(self.title_font, self.title, WHITE)
        self.title_rect = self.title_surface.get_rect(center=(SCREEN_WIDTH // 2, 60))
        
        self.instructions = [
            "↑↓ - Desplazar texto (mantener presionado)",
            "ESC - Regresar"
        ]
    
    def _render_text_with_shadow(self, font, text, text_color, shadow_color=(128, 128, 128), shadow_offset=2):
        shadow_surface = font.render(text, True, shadow_color)
        text_surface = font.render(text, True, text_color)
        
        combined_width = text_surface.get_width() + shadow_offset
        combined_height = text_surface.get_height() + shadow_offset
        combined_surface = pygame.Surface((combined_width, combined_height), pygame.SRCALPHA)
        
        combined_surface.blit(shadow_surface, (shadow_offset, shadow_offset))
        combined_surface.blit(text_surface, (0, 0))
        
        return combined_surface
    
    def _wrap_text(self, text, max_width):
        paragraphs = text.split('\n\n')
        lines = []
        
        for paragraph in paragraphs:
            if paragraph.strip():
                words = paragraph.split()
                current_line = ""
                
                for word in words:
                    test_line = current_line + (" " if current_line else "") + word
                    test_surface = self.text_font.render(test_line, True, WHITE)
                    
                    if test_surface.get_width() <= max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                
                if current_line:
                    lines.append(current_line)
                
                lines.append("")
        
        return lines
    
    def handle_event(self, event):
        if not self.can_handle_input or self.transitioning or self.transition.active:
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._start_transition(lambda: self.game.state_stack.pop())
    
    def _start_transition(self, callback):
        self.transitioning = True
        self.can_handle_input = False
        self.transition.start_fade_out(callback)
    
    def update(self, dt):
        self.background.update(dt)
        self.transition.update(dt)
        
        if not self.transition.active and self.transitioning:
            self.transitioning = False
            self.can_handle_input = True
        
        if self.can_handle_input and not self.transitioning:
            keys = pygame.key.get_pressed()
            current_time = pygame.time.get_ticks()
            
            if current_time - self.scroll_timer > self.scroll_delay:
                if keys[pygame.K_UP]:
                    self.scroll_offset = max(0, self.scroll_offset - self.scroll_speed)
                    self.scroll_timer = current_time
                elif keys[pygame.K_DOWN]:
                    self.scroll_offset = min(self.max_scroll, self.scroll_offset + self.scroll_speed)
                    self.scroll_timer = current_time
    
    def render(self, screen):
        self.background.render(screen)
        
        screen.blit(self.title_surface, self.title_rect)
        
        text_bg = pygame.Surface((self.text_area_width, self.text_area_height), pygame.SRCALPHA)
        text_bg.fill((*BLACK, 200))
        screen.blit(text_bg, (self.text_area_x, self.text_area_y))
        
        pygame.draw.rect(screen, WHITE, 
                        (self.text_area_x, self.text_area_y, self.text_area_width, self.text_area_height), 2)
        
        text_surface_width = self.text_area_width - 120
        text_surface_height = self.text_area_height - 60
        text_surface = pygame.Surface((text_surface_width, text_surface_height))
        text_surface.fill(BLACK)
        
        start_line = max(0, self.scroll_offset // self.line_height)
        end_line = min(len(self.lines), start_line + (self.text_area_height // self.line_height) + 5)
        
        for i in range(start_line, end_line):
            line = self.lines[i]
            y_pos = (i * self.line_height) - self.scroll_offset + 20
            
            if -self.line_height <= y_pos <= text_surface_height:
                if line.strip():
                    line_surface = self.text_font.render(line, True, WHITE)
                    text_surface.blit(line_surface, (20, y_pos))
        
        screen.blit(text_surface, (self.text_area_x + 20, self.text_area_y + 20))

        if self.max_scroll > 0:
            scroll_bar_height = self.text_area_height - 20
            scroll_bar_width = 10
            scroll_bar_x = self.text_area_x + self.text_area_width - 70
            scroll_bar_y = self.text_area_y + 10

            pygame.draw.rect(screen, (100, 100, 100), 
                           (scroll_bar_x, scroll_bar_y, scroll_bar_width, scroll_bar_height))
            
            indicator_height = max(20, int((self.text_area_height / (self.max_scroll + self.text_area_height)) * scroll_bar_height))
            indicator_y = scroll_bar_y + int((self.scroll_offset / self.max_scroll) * (scroll_bar_height - indicator_height))
            
            pygame.draw.rect(screen, WHITE, 
                           (scroll_bar_x, indicator_y, scroll_bar_width, indicator_height))
        
        instruction_y = SCREEN_HEIGHT - 60
        for i, instruction in enumerate(self.instructions):
            instruction_surface = self._render_text_with_shadow(self.instruction_font, instruction, WHITE)
            instruction_rect = instruction_surface.get_rect(center=(SCREEN_WIDTH // 2, instruction_y + i * 25))
            screen.blit(instruction_surface, instruction_rect)
        
        self.transition.render(screen)