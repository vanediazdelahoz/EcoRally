import pygame
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT

class BackgroundManager:
    _initialized = False
    _backgrounds = {}  # Dictionary to store multiple backgrounds
    _current_bg = "fondo1.png"  # Default background
    
    def __init__(self, background_name="fondo1.png"):
        """
        Gestor de fondo simplificado que puede cargar diferentes fondos
        """
        self.background_name = background_name
        
        if not BackgroundManager._initialized:
            self._load_background(background_name)
            BackgroundManager._initialized = True
        elif background_name not in BackgroundManager._backgrounds:
            self._load_background(background_name)
        
        # Set current background
        BackgroundManager._current_bg = background_name
        self.current_bg = background_name
    
    def _load_background(self, bg_name):
        """Carga una imagen de fondo RESPETANDO PROPORCIONES"""
        try:
            # Verificar si es Mapa.png para usar la ruta correcta
            if bg_name == "Mapa.png":
                fondo_path = f"assets/mapa/{bg_name}"
            else:
                fondo_path = f"assets/images/landscape/{bg_name}"
                
            # Cargar imagen original
            fondo_original = pygame.image.load(fondo_path).convert()
            
            # Obtener dimensiones originales
            original_width = fondo_original.get_width()
            original_height = fondo_original.get_height()
            
            # Calcular escalas para ancho y alto
            scale_x = SCREEN_WIDTH / original_width
            scale_y = SCREEN_HEIGHT / original_height
            
            # USAR LA ESCALA MENOR para mantener proporciones (no distorsionar)
            scale = min(scale_x, scale_y)
            
            # Calcular nuevas dimensiones manteniendo proporción
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            
            # Escalar imagen manteniendo proporción
            scaled_bg = pygame.transform.scale(fondo_original, (new_width, new_height))
            
            # Calcular posición para centrar la imagen
            bg_x = (SCREEN_WIDTH - new_width) // 2
            bg_y = (SCREEN_HEIGHT - new_height) // 2
            
            # Si la imagen no cubre toda la pantalla, llenar con color de fondo
            if new_width < SCREEN_WIDTH or new_height < SCREEN_HEIGHT:
                # Crear superficie del tamaño de la pantalla
                full_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                full_surface.fill((50, 50, 50))  # Color de relleno gris oscuro
                full_surface.blit(scaled_bg, (bg_x, bg_y))
                
                # Guardar en el diccionario
                BackgroundManager._backgrounds[bg_name] = {
                    'surface': full_surface,
                    'x': 0,
                    'y': 0
                }
            else:
                # Guardar en el diccionario
                BackgroundManager._backgrounds[bg_name] = {
                    'surface': scaled_bg,
                    'x': bg_x,
                    'y': bg_y
                }
            
            print(f"BackgroundManager - {bg_name} cargado con proporciones respetadas")
            
        except Exception as e:
            print(f"Error cargando {bg_name}: {e}")
            # Crear superficie negra como fallback
            fallback = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fallback.fill((0, 0, 0))
            BackgroundManager._backgrounds[bg_name] = {
                'surface': fallback,
                'x': 0,
                'y': 0
            }
    
    def change_background(self, new_background_name):
        """Cambiar a un nuevo fondo"""
        if new_background_name not in BackgroundManager._backgrounds:
            self._load_background(new_background_name)
        
        BackgroundManager._current_bg = new_background_name
        self.current_bg = new_background_name
        print(f"BackgroundManager - Cambiado a {new_background_name}")
    
    def update(self, dt):
        """Ya no hay animaciones de fondo"""
        pass
    
    def render(self, screen):
        """Renderiza el fondo actual centrado"""
        bg_data = BackgroundManager._backgrounds[self.current_bg]
        screen.blit(bg_data['surface'], (bg_data['x'], bg_data['y']))

print("BackgroundManager mejorado - soporte para múltiples fondos con proporciones respetadas")
