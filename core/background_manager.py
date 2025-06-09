# Gestor de fondos del juego

import pygame
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT

class BackgroundManager:
    _initialized = False
    _backgrounds = {}
    _current_bg = "background.png"
    
    def __init__(self, background_name="background.png"):

        self.background_name = background_name
        
        if not BackgroundManager._initialized:
            self._load_background(background_name)
            BackgroundManager._initialized = True
        elif background_name not in BackgroundManager._backgrounds:
            self._load_background(background_name)
        
        BackgroundManager._current_bg = background_name
        self.current_bg = background_name
    
    def _load_background(self, bg_name):
        try:
            if bg_name == "map.png":
                fondo_path = f"assets/images/map/{bg_name}"
            else:
                fondo_path = f"assets/images/selection/{bg_name}"
                
            fondo_original = pygame.image.load(fondo_path).convert()
            
            original_width = fondo_original.get_width()
            original_height = fondo_original.get_height()
            
            scale_x = SCREEN_WIDTH / original_width
            scale_y = SCREEN_HEIGHT / original_height
            
            scale = min(scale_x, scale_y)
            
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            
            scaled_bg = pygame.transform.scale(fondo_original, (new_width, new_height))
            
            bg_x = (SCREEN_WIDTH - new_width) // 2
            bg_y = (SCREEN_HEIGHT - new_height) // 2
            
            if new_width < SCREEN_WIDTH or new_height < SCREEN_HEIGHT:

                full_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                full_surface.fill((0, 0, 0))
                full_surface.blit(scaled_bg, (bg_x, bg_y))
                
                BackgroundManager._backgrounds[bg_name] = {
                    'surface': full_surface,
                    'x': 0,
                    'y': 0
                }
            else:

                BackgroundManager._backgrounds[bg_name] = {
                    'surface': scaled_bg,
                    'x': bg_x,
                    'y': bg_y
                }
            
        except Exception as e:
            fallback = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fallback.fill((0, 0, 0))
            BackgroundManager._backgrounds[bg_name] = {
                'surface': fallback,
                'x': 0,
                'y': 0
            }
    
    def change_background(self, new_background_name):
        if new_background_name not in BackgroundManager._backgrounds:
            self._load_background(new_background_name)
        
        BackgroundManager._current_bg = new_background_name
        self.current_bg = new_background_name
    
    def update(self, dt):
        pass
    
    def render(self, screen):
        bg_data = BackgroundManager._backgrounds[self.current_bg]
        screen.blit(bg_data['surface'], (bg_data['x'], bg_data['y']))
