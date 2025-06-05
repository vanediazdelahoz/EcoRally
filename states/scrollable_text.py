# states/information.py
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
        
        # Gestor de fondo
        self.background = BackgroundManager()
        
        # Efecto de transición
        self.transition = TransitionEffect(0.15)
        self.transition.start_fade_in()
        
        # Control de transición
        self.transitioning = False
        self.can_handle_input = True
        
       # Configuración del texto
        self.title = "Información"
        self.content = """El cambio climático es uno de los problemas globales más graves y urgentes. Impulsado principalmente por actividades humanas, este fenómeno ha intensificado la emisión de gases de efecto invernadero que se acumulan en la atmósfera, alterando los patrones climáticos del planeta. Como resultado, han surgido efectos devastadores, como el aumento del nivel del mar, fenómenos meteorológicos extremos, escasez de agua y alimentos, pérdida de glaciares y propagación de enfermedades (Ministerio de Ambiente y Desarrollo Sostenible, 2022). Estas consecuencias afectan tanto a las comunidades humanas como a los ecosistemas, aumentando su vulnerabilidad y comprometiendo su resiliencia.

A pesar de la implementación de acuerdos internacionales como el Acuerdo de París, el progreso en la mitigación de esta crisis ha sido limitado. El año 2024 fue registrado como el más caluroso hasta la fecha, y por primera vez se superó el umbral crítico de aumento de temperatura global de 1,5 °C (Stone, 2025). Este escenario pone en evidencia que, aunque se han asumido compromisos globales, aún existe una brecha significativa entre los objetivos propuestos y las acciones efectivamente llevadas a cabo.

Entre los múltiples factores que contribuyen al cambio climático, uno de los menos visibles pero altamente impactantes es la inadecuada gestión de los residuos sólidos. La forma en que se producen, consumen y desechan los materiales tiene efectos ambientales significativos. En particular, los residuos orgánicos y reciclables que terminan en vertederos no tratados emiten grandes cantidades de metano, un gas de efecto invernadero que, a corto plazo, es considerablemente más potente que el dióxido de carbono (Siegel, 2022). De hecho, se estima que el sector de residuos es responsable de cerca del 20%/ de las emisiones antropogénicas de metano, lo que subraya la urgencia de abordar esta fuente como parte de las estrategias climáticas globales.

En este contexto, el reciclaje se presenta como una de las herramientas más efectivas para mitigar el impacto ambiental de los residuos. Además de reducir la cantidad de desechos enviados a los vertederos, el reciclaje disminuye las emisiones de gases de efecto invernadero, reduce el consumo energético, limita la contaminación y conserva los recursos naturales. Según la Agencia de Protección Ambiental de los Estados Unidos (Manchasoft, 2023), reciclar una tonelada de materiales puede reducir las emisiones asociadas en un 60 % y el uso de energía en un 74 %. Sin embargo, estos beneficios dependen directamente del nivel de participación ciudadana, que sigue siendo insuficiente en muchas regiones del mundo.

Las estadísticas globales reflejan esta deficiencia. Solo el 14%/ de los residuos generados se recicla a nivel mundial (Manchasoft, 2023), y en países como Colombia, las cifras son aún más bajas. Según la iniciativa Visión 30/30 de la ANDI, el 62 % de los colombianos no separa sus residuos usando bolsas de colores, y solo el 46%/ identifica correctamente los materiales que deben ir en la bolsa blanca (Castañeda, 2023). Estas cifras revelan no solo una falta de conocimiento práctico, sino también una desconexión entre la gravedad del problema ambiental y las acciones cotidianas de las personas. Como afirma el ecólogo Masashi Soga, enfrentar el cambio climático requiere transformaciones profundas, tanto individuales como colectivas, basadas en el desarrollo de la conciencia ambiental (Stone, 2025).

Ante esta necesidad, es fundamental buscar nuevas formas de sensibilizar y educar a la sociedad. En este sentido, los videojuegos ofrecen una herramienta innovadora con un alto potencial educativo. A través del aprendizaje basado en el juego, los usuarios pueden involucrarse activamente en experiencias significativas que promueven cambios de comportamiento. Los videojuegos refuerzan actitudes sostenibles mediante dinámicas lúdicas, recompensas, desafíos y narrativas inmersivas, facilitando el aprendizaje en un entorno seguro y motivador (Dirección Nacional de Tecnologías para la Educación – DNTE, 2023).

Desde esta perspectiva, el presente proyecto propone el desarrollo de EcoRally, un videojuego de estilo tablero orientado a generar conciencia sobre el cambio climático y la importancia del reciclaje. En EcoRally, dos jugadores compiten por recolectar y reciclar residuos mientras participan en minijuegos temáticos entre rondas. El juego ofrece tanto un modo competitivo entre jugadores humanos como un modo contra un agente de inteligencia artificial basado en el algoritmo Dyna-Q, que toma decisiones estratégicas a partir de experiencias previas. La propuesta busca fomentar actitudes ambientales responsables a través de una experiencia lúdica que destaque el impacto de las decisiones individuales sobre el medio ambiente."""
        
        # Fuentes
        self.title_font = load_font("assets/fonts/PressStart2P-Regular.ttf", 32)
        self.text_font = load_font("assets/fonts/PublicPixel.ttf", 12)
        self.instruction_font = load_font("assets/fonts/PressStart2P-Regular.ttf", 14)
        
        # === CONFIGURACIÓN DEL ÁREA DE TEXTO ===
        self.text_area_x = 80
        self.text_area_y = 120
        self.text_area_width = SCREEN_WIDTH - 160
        self.text_area_height = SCREEN_HEIGHT - 200
        
        # === CONFIGURACIÓN DEL SCROLL ===
        self.scroll_offset = 0
        self.scroll_speed = 8  # AUMENTADO: Velocidad más rápida para scroll
        self.line_height = 20  # Reducido para mejor espaciado
        
        # === CONTROL DE TECLAS MANTENIDAS ===
        self.scroll_timer = 0
        self.scroll_delay = 30  # REDUCIDO: Menos delay para scroll más fluido
        
        # Procesar el contenido en líneas (MUCHO más espacio para la barra de scroll)
        self.lines = self._wrap_text(self.content, self.text_area_width - 150)  # Mucho más espacio
        
        # Calcular límites de scroll
        total_content_height = len(self.lines) * self.line_height
        self.max_scroll = max(0, total_content_height - self.text_area_height + 80)
        
        # Renderizar título con sombra
        self.title_surface = self._render_text_with_shadow(self.title_font, self.title, WHITE)
        self.title_rect = self.title_surface.get_rect(center=(SCREEN_WIDTH // 2, 60))
        
        # Instrucciones
        self.instructions = [
            "↑↓ - Desplazar texto (mantener presionado)",
            "ESC - Regresar"
        ]
    
    def _render_text_with_shadow(self, font, text, text_color, shadow_color=(128, 128, 128), shadow_offset=2):
        """Renderiza texto con sombreado"""
        shadow_surface = font.render(text, True, shadow_color)
        text_surface = font.render(text, True, text_color)
        
        combined_width = text_surface.get_width() + shadow_offset
        combined_height = text_surface.get_height() + shadow_offset
        combined_surface = pygame.Surface((combined_width, combined_height), pygame.SRCALPHA)
        
        combined_surface.blit(shadow_surface, (shadow_offset, shadow_offset))
        combined_surface.blit(text_surface, (0, 0))
        
        return combined_surface
    
    def _wrap_text(self, text, max_width):
        """Divide el texto en líneas que quepan en el ancho especificado"""
        paragraphs = text.split('\n\n')
        lines = []
        
        for paragraph in paragraphs:
            if paragraph.strip():
                words = paragraph.split()
                current_line = ""
                
                for word in words:
                    # Verificar si la palabra cabe en la línea actual
                    test_line = current_line + (" " if current_line else "") + word
                    test_surface = self.text_font.render(test_line, True, WHITE)
                    
                    if test_surface.get_width() <= max_width:
                        current_line = test_line
                    else:
                        # La línea actual está completa, empezar una nueva
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                
                # Agregar la última línea del párrafo
                if current_line:
                    lines.append(current_line)
                
                # Agregar línea vacía entre párrafos
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
        
        # === SCROLL CONTINUO CON TECLAS MANTENIDAS ===
        if self.can_handle_input and not self.transitioning:
            keys = pygame.key.get_pressed()
            current_time = pygame.time.get_ticks()
            
            # Verificar si es tiempo de hacer scroll
            if current_time - self.scroll_timer > self.scroll_delay:
                if keys[pygame.K_UP]:
                    self.scroll_offset = max(0, self.scroll_offset - self.scroll_speed)
                    self.scroll_timer = current_time
                elif keys[pygame.K_DOWN]:
                    self.scroll_offset = min(self.max_scroll, self.scroll_offset + self.scroll_speed)
                    self.scroll_timer = current_time
    
    def render(self, screen):
        # Renderizar fondo
        self.background.render(screen)
        
        # Renderizar título
        screen.blit(self.title_surface, self.title_rect)
        
        # === ÁREA DE TEXTO CON FONDO MARRON ===
        text_bg = pygame.Surface((self.text_area_width, self.text_area_height), pygame.SRCALPHA)
        text_bg.fill((*BLACK, 200))  # Fondo MARRON con transparencia
        screen.blit(text_bg, (self.text_area_x, self.text_area_y))
        
        # Borde del área de texto
        pygame.draw.rect(screen, WHITE, 
                        (self.text_area_x, self.text_area_y, self.text_area_width, self.text_area_height), 2)
        
        # === RENDERIZAR TEXTO CON SCROLL ===
        # CORREGIDO: Crear superficie con fondo MARRON en lugar de transparente
        text_surface_width = self.text_area_width - 120  # AUN MÁS espacio para barra
        text_surface_height = self.text_area_height - 60
        text_surface = pygame.Surface((text_surface_width, text_surface_height))
        text_surface.fill(BLACK)  # CORREGIDO: Fondo MARRON sólido
        
        # Renderizar líneas visibles
        start_line = max(0, self.scroll_offset // self.line_height)
        end_line = min(len(self.lines), start_line + (self.text_area_height // self.line_height) + 5)
        
        for i in range(start_line, end_line):
            line = self.lines[i]
            y_pos = (i * self.line_height) - self.scroll_offset + 20
            
            # Solo renderizar si está dentro del área visible
            if -self.line_height <= y_pos <= text_surface_height:
                if line.strip():  # Solo renderizar líneas no vacías
                    line_surface = self.text_font.render(line, True, WHITE)
                    text_surface.blit(line_surface, (20, y_pos))
        
        # Blit del texto en el área de recorte
        screen.blit(text_surface, (self.text_area_x + 20, self.text_area_y + 20))
        
        # === INDICADOR DE SCROLL (MUY SEPARADO DEL TEXTO) ===
        if self.max_scroll > 0:
            # Barra de scroll muy separada del texto
            scroll_bar_height = self.text_area_height - 20
            scroll_bar_width = 10
            scroll_bar_x = self.text_area_x + self.text_area_width - 20 - scroll_bar_width
            scroll_bar_y = self.text_area_y + 10
            
            # Fondo de la barra
            pygame.draw.rect(screen, (100, 100, 100), 
                           (scroll_bar_x, scroll_bar_y, scroll_bar_width, scroll_bar_height))
            
            # Indicador de posición
            indicator_height = max(20, int((self.text_area_height / (self.max_scroll + self.text_area_height)) * scroll_bar_height))
            indicator_y = scroll_bar_y + int((self.scroll_offset / self.max_scroll) * (scroll_bar_height - indicator_height))
            
            pygame.draw.rect(screen, WHITE, 
                           (scroll_bar_x, indicator_y, scroll_bar_width, indicator_height))
        
        # === INSTRUCCIONES ===
        instruction_y = SCREEN_HEIGHT - 60
        for i, instruction in enumerate(self.instructions):
            instruction_surface = self._render_text_with_shadow(self.instruction_font, instruction, WHITE)
            instruction_rect = instruction_surface.get_rect(center=(SCREEN_WIDTH // 2, instruction_y + i * 25))
            screen.blit(instruction_surface, instruction_rect)
        
        # Renderizar transición
        self.transition.render(screen)