# states/character_selection.py
import pygame
import random
from core.config import config
from core.state import State
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE
from core.utils import load_font, get_character
from core.background_manager import BackgroundManager
from core.effects import TransitionEffect

class CharacterSelection(State):
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
        
        # Fuentes - DEFINIR ANTES DE USAR
        self.font_title = load_font("assets/fonts/PublicPixel.ttf", 28)
        self.font_button = load_font("assets/fonts/PublicPixel.ttf", 18)
        self.font_controls = load_font("assets/fonts/mc-ten-lowercase-alt.ttf", 11)
        self.label_font = load_font("assets/fonts/PublicPixel.ttf", 14)
        
        # === CONFIGURACIÓN DE POSICIONES (AJUSTABLE) ===
        self.title_y_position = 80  # Posición Y del título (ajustable)
        self.panels_y_position = 180  # Posición Y de los paneles (ajustable)
        self.panel_width = 160       # Ancho de paneles (ajustable)
        self.panel_height = 220      # Alto de paneles (ajustable)
        self.panels_spacing = 200    # Espaciado entre paneles (ajustable)
        self.arrow_distance = 90     # Distancia de flechas a paneles (ajustable)
        self.arrow_size = 150         # Tamaño de las flechas (ajustable)
        
        # === CONFIGURACIÓN DE TEXTOS DE CONTROLES (AJUSTABLE) ===
        self.controls_offset_y = 80     # Distancia vertical desde el panel hacia ABAJO (ajustable)
        self.controls_line_spacing = 15  # Espaciado entre líneas de texto (ajustable)
        self.controls_font_size = 12     # Tamaño de fuente de controles (ajustable)
        
        # Actualizar fuente de controles con el tamaño configurable
        self.font_controls = load_font("assets/fonts/mc-ten-lowercase-alt.ttf", self.controls_font_size)
        
        # Título CON SOMBREADO GRIS
        self.title_surface = self._render_text_with_shadow(self.font_title, "SELECCIONA TU PERSONAJE", WHITE)
        self.title_rect = self.title_surface.get_rect(center=(SCREEN_WIDTH // 2, self.title_y_position))
        
        # Cargar personajes
        character_paths = get_character(4)
        self.character_names = ["Rosalba", "Icm", "Sofia", "Luis"]
        self.characters = []
        
        for i, path in enumerate(character_paths):
            try:
                img = pygame.image.load(path).convert_alpha()
                if i < 2:
                    img = pygame.transform.scale(img, (99, 180))
                else:
                    img = pygame.transform.scale(img, (107, 153))
                self.characters.append(img)
            except Exception as e:
                print(f"Error cargando personaje en {path}:", e)
        
        # Variables de selección
        self.selected_p1 = 0
        self.selected_p2 = 1
        self.confirmed_p1 = False
        self.confirmed_p2 = False
        self.final_p1 = None
        self.final_p2 = None
        
        # Limpiar configuración anterior
        config.characters.clear()
        config.characters.extend([None, None])
        
        # Configuración de paneles
        total_width = self.panel_width * 2 + self.panels_spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        self.p1_rect = pygame.Rect(start_x, self.panels_y_position, self.panel_width, self.panel_height)
        self.p2_rect = pygame.Rect(start_x + self.panel_width + self.panels_spacing, self.panels_y_position, self.panel_width, self.panel_height)
        
        # Labels CON SOMBREADO
        self.p1_label = self._render_text_with_shadow(self.label_font, "JUGADOR 1", WHITE)
        self.p2_label = self._render_text_with_shadow(self.label_font, "JUGADOR 2" if not config.machine_mode else "BOT", WHITE)
        
        # Cargar imagen de flecha CORRIGIENDO ORIENTACIÓN COMPLETAMENTE
        try:
            flecha_original = pygame.image.load("assets/images/landscape/flecha.png").convert_alpha()
            
            # Calcular escala manteniendo proporción
            original_width = flecha_original.get_width()
            original_height = flecha_original.get_height()
            
            # Calcular escala para que el lado más grande sea arrow_size
            scale = self.arrow_size / max(original_width, original_height)
            
            # Calcular nuevas dimensiones manteniendo proporción
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            
            # Escalar manteniendo proporción
            flecha_base = pygame.transform.scale(flecha_original, (new_width, new_height))
            
            # INTERCAMBIAR: La imagen original debe apuntar hacia la izquierda
            # Para flecha izquierda: usar la original
            self.flecha_left = flecha_base
            # Para flecha derecha: rotar 180 grados
            self.flecha_right = pygame.transform.rotate(flecha_base, 180)
            
        except Exception as e:
            print(f"Error cargando flecha.png: {e}")
            # Crear flechas simples como fallback
            self.flecha_right = pygame.Surface((self.arrow_size, self.arrow_size))
            self.flecha_right.fill(WHITE)
            self.flecha_left = self.flecha_right.copy()
        
        # Instrucciones de controles
        self.controls_p1 = [
            "A/D - Cambiar",
            "F - Confirmar"
        ]
        self.controls_p2 = [
            "←/→ - Cambiar", 
            "Enter - Confirmar"
        ] if not config.machine_mode else ["Automático"]
        
        # Flag para evitar ESC después de confirmación completa
        self.both_confirmed = False
    
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
    
    def check_both_confirmed(self):
        """Verificar si ambos jugadores han confirmado y proceder al juego"""
        if self.confirmed_p1 and self.confirmed_p2 and not self.both_confirmed:
            self.both_confirmed = True
            pygame.time.set_timer(pygame.USEREVENT + 10, 500)
    
    def handle_event(self, event):
        if not self.can_handle_input or self.transitioning or self.transition.active:
            return
            
        if event.type == pygame.KEYDOWN:
            # ESC solo funciona si NO ambos han confirmado
            if event.key == pygame.K_ESCAPE and not self.both_confirmed:
                self._start_transition(lambda: self.game.state_stack.pop())
            
            # Controles Player 1
            elif event.key == pygame.K_a and not self.confirmed_p1:
                self.selected_p1 = (self.selected_p1 - 1) % len(self.characters)
            elif event.key == pygame.K_d and not self.confirmed_p1:
                self.selected_p1 = (self.selected_p1 + 1) % len(self.characters)
            elif event.key == pygame.K_f:
                if not self.confirmed_p1:
                    # Confirmar selección P1
                    if not self.confirmed_p2 or self.selected_p1 != self.final_p2:
                        self.confirmed_p1 = True
                        self.final_p1 = self.selected_p1
                        config.characters[0] = self.final_p1
                        print(f"Jugador 1 confirmó personaje {self.final_p1}: {self.character_names[self.final_p1]}")
                        
                        if config.machine_mode:
                            # Bot selecciona automáticamente
                            available_chars = [i for i in range(len(self.characters)) if i != self.final_p1]
                            self.final_p2 = random.choice(available_chars)
                            self.selected_p2 = self.final_p2
                            self.confirmed_p2 = True
                            config.characters[1] = self.final_p2
                            print(f"Bot seleccionó automáticamente personaje {self.final_p2}: {self.character_names[self.final_p2]}")
                        
                        # Verificar si ambos han confirmado
                        self.check_both_confirmed()
                    else:
                        print("Ese personaje ya fue seleccionado por el otro jugador.")
                else:
                    # Retractarse P1
                    if not self.both_confirmed:
                        self.confirmed_p1 = False
                        self.final_p1 = None
                        config.characters[0] = None
                        print("Jugador 1 se retractó de su selección")
                        
                        # Si era modo bot, también resetear bot
                        if config.machine_mode:
                            self.confirmed_p2 = False
                            self.final_p2 = None
                            config.characters[1] = None
                            self.both_confirmed = False
            
            # Controles Player 2 (solo si no es bot)
            elif not config.machine_mode:
                if event.key == pygame.K_LEFT and not self.confirmed_p2:
                    self.selected_p2 = (self.selected_p2 - 1) % len(self.characters)
                elif event.key == pygame.K_RIGHT and not self.confirmed_p2:
                    self.selected_p2 = (self.selected_p2 + 1) % len(self.characters)
                elif event.key == pygame.K_RETURN:
                    if not self.confirmed_p2:
                        # Confirmar selección P2
                        if not self.confirmed_p1 or self.selected_p2 != self.final_p1:
                            self.confirmed_p2 = True
                            self.final_p2 = self.selected_p2
                            config.characters[1] = self.final_p2
                            print(f"Jugador 2 confirmó personaje {self.final_p2}: {self.character_names[self.final_p2]}")
                            
                            # Verificar si ambos han confirmado
                            self.check_both_confirmed()
                        else:
                            print("Ese personaje ya fue seleccionado por el otro jugador.")
                    else:
                        # Retractarse P2
                        if not self.both_confirmed:
                            self.confirmed_p2 = False
                            self.final_p2 = None
                            config.characters[1] = None
                            print("Jugador 2 se retractó de su selección")
        
        if event.type == pygame.USEREVENT + 10:
            pygame.time.set_timer(pygame.USEREVENT + 10, 0)
            if None not in config.characters:
                def go_to_game():
                    from states.visual_board_game import BoardGameView
                    self.game.state_stack.append(BoardGameView(self.game))
                self._start_transition(go_to_game)
    
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
    
    def render(self, screen):
        # Renderizar fondo1.png
        self.background.render(screen)
        
        # Título
        screen.blit(self.title_surface, self.title_rect)
        
        # Labels de jugadores
        p1_label_rect = self.p1_label.get_rect(center=(self.p1_rect.centerx, self.p1_rect.top - 20))
        p2_label_rect = self.p2_label.get_rect(center=(self.p2_rect.centerx, self.p2_rect.top - 20))
        screen.blit(self.p1_label, p1_label_rect)
        screen.blit(self.p2_label, p2_label_rect)
        
        # Paneles de personajes
        self._draw_character_panel(screen, self.p1_rect, self.selected_p1, self.confirmed_p1, "p1")
        self._draw_character_panel(screen, self.p2_rect, self.selected_p2, self.confirmed_p2, "p2")
        
        # Botones de nombres (ANTES de los controles para calcular posición)
        self._draw_character_button(screen, self.p1_rect, self.confirmed_p1, self.selected_p1, "p1")
        self._draw_character_button(screen, self.p2_rect, self.confirmed_p2, self.selected_p2, "p2")
        
        # Instrucciones de controles (DESPUÉS de los nombres)
        self._draw_controls(screen)
        
        # Flechas con orientación corregida
        if not self.confirmed_p1:
            # Flecha izquierda (apunta hacia la izquierda)
            left_arrow_pos = (self.p1_rect.left - self.arrow_distance, self.p1_rect.centery - self.flecha_left.get_height() // 2)
            screen.blit(self.flecha_left, left_arrow_pos)
            
            # Flecha derecha (apunta hacia la derecha)
            right_arrow_pos = (self.p1_rect.right + self.arrow_distance - self.flecha_right.get_width(), self.p1_rect.centery - self.flecha_right.get_height() // 2)
            screen.blit(self.flecha_right, right_arrow_pos)
        
        if not config.machine_mode and not self.confirmed_p2:
            # Flecha izquierda (apunta hacia la izquierda)
            left_arrow_pos = (self.p2_rect.left - self.arrow_distance, self.p2_rect.centery - self.flecha_left.get_height() // 2)
            screen.blit(self.flecha_left, left_arrow_pos)
            
            # Flecha derecha (apunta hacia la derecha)
            right_arrow_pos = (self.p2_rect.right + self.arrow_distance - self.flecha_right.get_width(), self.p2_rect.centery - self.flecha_right.get_height() // 2)
            screen.blit(self.flecha_right, right_arrow_pos)
        
        # Renderizar transición
        self.transition.render(screen)
    
    def _draw_controls(self, screen):
        """Dibuja las instrucciones de controles DEBAJO de los nombres - POSICIÓN CONFIGURABLE"""
        # Controles P1 - Ahora debajo del nombre
        y_start = self.p1_rect.bottom + self.controls_offset_y
        for i, control in enumerate(self.controls_p1):
            text = self._render_text_with_shadow(self.font_controls, control, WHITE, (100, 100, 100), 1)
            text_rect = text.get_rect(center=(self.p1_rect.centerx, y_start + i * self.controls_line_spacing))
            screen.blit(text, text_rect)
        
        # Controles P2 - Ahora debajo del nombre
        y_start = self.p2_rect.bottom + self.controls_offset_y
        for i, control in enumerate(self.controls_p2):
            text = self._render_text_with_shadow(self.font_controls, control, WHITE, (100, 100, 100), 1)
            text_rect = text.get_rect(center=(self.p2_rect.centerx, y_start + i * self.controls_line_spacing))
            screen.blit(text, text_rect)
    
    def _draw_character_panel(self, screen, rect, selected_idx, is_confirmed, player):
        # Color del panel (opcional, puede ser transparente)
        if is_confirmed:
            panel_color = (40, 80, 40, 100)  # Verde semi-transparente
        else:
            panel_color = (60, 60, 60, 100)  # Gris semi-transparente
        
        # Crear superficie con transparencia
        panel_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        panel_surface.fill(panel_color)
        screen.blit(panel_surface, rect)
        
        # Borde blanco
        pygame.draw.rect(screen, WHITE, rect, 2)
        
        # Personaje
        char = self.characters[selected_idx]
        
        # Voltear personaje de player 2
        if player == "p2":
            char = pygame.transform.flip(char, True, False)
        
        char_rect = char.get_rect(center=rect.center)
        screen.blit(char, char_rect)
    
    def _draw_character_button(self, screen, panel_rect, is_confirmed, selected_idx, player):
        # Texto del botón
        name = self.character_names[selected_idx]
        
        if player == "p2" and config.machine_mode:
            name = f"Bot: {name}"
        
        if is_confirmed:
            name += " ✓"
        
        # Crear superficie de texto CON SOMBREADO
        if is_confirmed:
            # Texto más grande cuando está confirmado
            button_font = load_font("assets/fonts/PublicPixel.ttf", 20)
            text_surface = self._render_text_with_shadow(button_font, name, WHITE, (100, 100, 100), 2)
        else:
            text_surface = self._render_text_with_shadow(self.font_button, name, WHITE, (100, 100, 100), 1)
        
        # Crear rectángulo de fondo para el nombre
        text_rect = text_surface.get_rect(center=(panel_rect.centerx, panel_rect.bottom + 30))
        
        # Crear rectángulo de fondo con padding
        padding = 8
        bg_rect = pygame.Rect(
            text_rect.left - padding,
            text_rect.top - padding//2,
            text_rect.width + padding * 2,
            text_rect.height + padding
        )
        
        # Color del rectángulo de fondo
        if is_confirmed:
            bg_color = (40, 80, 40, 180)  # Verde semi-transparente
        else:
            bg_color = (40, 40, 40, 180)  # Gris oscuro semi-transparente
        
        # Crear superficie con transparencia para el fondo
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill(bg_color)
        screen.blit(bg_surface, bg_rect)
        
        # Borde del rectángulo
        pygame.draw.rect(screen, WHITE, bg_rect, 1)
        
        # Renderizar el texto encima del rectángulo
        screen.blit(text_surface, text_rect)

print("CharacterSelection - Lógica de confirmación corregida")
