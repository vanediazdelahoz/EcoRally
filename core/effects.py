# Conjunto de efectos visuales reutilizables

import pygame
import math

class TransitionEffect:
    def __init__(self, duration=0.15):
        self.duration = duration
        self.timer = 0
        self.active = False
        self.fade_in = True
        self.callback = None
        self.callback_executed = False
    
    def start_fade_in(self, callback=None):
        self.active = True
        self.fade_in = True
        self.timer = 0
        self.callback = callback
        self.callback_executed = False
    
    def start_fade_out(self, callback=None):
        self.active = True
        self.fade_in = False
        self.timer = 0
        self.callback = callback
        self.callback_executed = False
    
    def update(self, dt):
        if self.active:
            self.timer += dt
            if self.timer >= self.duration:
                self.active = False
                self.timer = self.duration
                if self.callback and not self.callback_executed:
                    self.callback_executed = True
                    self.callback()
                    self.callback = None
    
    def get_alpha(self):
        if not self.active and self.timer == 0:
            return 0
        
        progress = min(self.timer / self.duration, 1.0)
        if self.fade_in:
            return int(255 * (1 - progress))
        else:
            return int(255 * progress)
    
    def is_complete(self):
        return not self.active and self.timer >= self.duration
    
    def render(self, screen):
        if self.active:
            alpha = self.get_alpha()
            if alpha > 0:
                fade_surface = pygame.Surface(screen.get_size())
                fade_surface.fill((0, 0, 0))
                fade_surface.set_alpha(alpha)
                screen.blit(fade_surface, (0, 0))

class ButtonEffect:
    def __init__(self):
        self.hover_scale = 1.0
        self.target_scale = 1.0
        self.pulse_timer = 0
        
    def set_hover(self, is_hover):
        self.target_scale = 1.01 if is_hover else 1.0
    
    def set_selected(self, is_selected):
        if is_selected:
            self.target_scale = 1.01
        
    def update(self, dt):
        scale_diff = self.target_scale - self.hover_scale
        self.hover_scale += scale_diff * dt * 8
        
        # Pulse effect
        self.pulse_timer += dt * 2
    
    def get_scale(self):
        return self.hover_scale
    
    def get_pulse_alpha(self):
        return int(10 + 8 * math.sin(self.pulse_timer))

def render_text_with_outline(font, text, text_color, outline_color, outline_width=2):
    base = font.render(text, True, text_color)
    size = base.get_size()
    margin = outline_width * 2
    outline_surface = pygame.Surface((size[0] + 2 * margin, size[1] + 2 * margin), pygame.SRCALPHA)
    
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                outline_surface.blit(font.render(text, True, outline_color), (margin + dx, margin + dy))
    
    outline_surface.blit(base, (margin, margin))
    return outline_surface

def calculate_uniform_button_width(texts, font, padding_x=16):
    # Calcula el ancho uniforme para todos los botones basado en el texto más largo
    max_width = 0
    for text in texts:
        text_surface = font.render(text, True, (255, 255, 255))
        text_width = text_surface.get_width()
        max_width = max(max_width, text_width)
    
    return max_width + (padding_x * 2)

def draw_pixel_button(surface, rect, is_selected=False, scale=1.0, pulse_alpha=0, text="", font=None, uniform_width=None):

    if uniform_width and text and font:
        text_surface = font.render(text, True, (255, 255, 255))
        text_height = text_surface.get_height()
        
        padding_y = 12
        
        new_width = uniform_width
        new_height = text_height + (padding_y * 2)
        
        center = rect.center
        rect = pygame.Rect(0, 0, new_width, new_height)
        rect.center = center
    
    if scale != 1.0:
        center = rect.center
        scaled_width = int(rect.width * scale)
        scaled_height = int(rect.height * scale)
        rect = pygame.Rect(0, 0, scaled_width, scaled_height)
        rect.center = center
    
    if is_selected:
        bg_color = (40, 40, 40)
        border_color = (0, 255, 0)
        text_color = (255, 255, 255)
        border_thickness = 3
        
        if pulse_alpha > 0:
            glow_rect = pygame.Rect(rect.x - 4, rect.y - 4, rect.width + 8, rect.height + 8)
            glow_surface = pygame.Surface((rect.width + 8, rect.height + 8), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (0, 255, 0, pulse_alpha), (0, 0, rect.width + 8, rect.height + 8))
            surface.blit(glow_surface, (rect.x - 4, rect.y - 4))
    else:
        bg_color = (25, 25, 25)
        border_color = (80, 80, 80)
        text_color = (255, 255, 255)
        border_thickness = 2
    
    pygame.draw.rect(surface, bg_color, rect)
    
    pygame.draw.rect(surface, border_color, rect, border_thickness)

    if text and font:
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        surface.blit(text_surface, text_rect)
    
    return rect

def draw_pixel_arrow(surface, x, y, direction="left", color=(255, 255, 255), size=16):

    if direction == "left":
        points = [
            (x, y),
            (x + size, y - size//2),
            (x + size//2, y - size//2),
            (x + size//2, y + size//2),
            (x + size, y + size//2)
        ]
    else:
        points = [
            (x, y),
            (x - size, y - size//2),
            (x - size//2, y - size//2),
            (x - size//2, y + size//2),
            (x - size, y + size//2)
        ]
    
    pygame.draw.polygon(surface, color, points)

def draw_pixel_rect(surface, rect, color, border_color=None, border_width=2):

    pygame.draw.rect(surface, color, rect)
    
    if border_color:
        pygame.draw.rect(surface, border_color, rect, border_width)