import pygame
import random
from core.state import State
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK
from core.utils import load_font
from core.effects import TransitionEffect

class ALaCanecaState(State):
    def __init__(self, game):
        super().__init__(game)
        pygame.mouse.set_visible(False)
        
        # Efecto de transición
        self.transition = TransitionEffect(0.15)
        self.transition.start_fade_in()
        
        # Control de transición
        self.transitioning = False
        self.can_handle_input = True
        
        # Fuentes
        self.font = load_font("assets/fonts/PublicPixel.ttf", 24)
        self.font_small = load_font("assets/fonts/PublicPixel.ttf", 16)
        self.font_final = load_font("assets/fonts/PublicPixel.ttf", 32)
        
        # Cargar fondo
        try:
            self.fondo = pygame.image.load("assets/CosasDeMinijuegos/FondoClasificar.png").convert()
            self.fondo = pygame.transform.scale(self.fondo, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception as e:
            print(f"Error cargando fondo: {e}")
            self.fondo = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.fondo.fill((30, 30, 40))
        
        # Cargar canecas
        try:
            self.canecaB = pygame.transform.scale(
                pygame.image.load("assets/CosasDeMinijuegos/Canasta de basura/CanecaB.png").convert_alpha(),
                (100, 100)
            )
            self.canecaV = pygame.transform.scale(
                pygame.image.load("assets/CosasDeMinijuegos/Canasta de basura/CanecaV.png").convert_alpha(),
                (100, 100)
            )
            self.canecaN = pygame.transform.scale(
                pygame.image.load("assets/CosasDeMinijuegos/Canasta de basura/CanecaN.png").convert_alpha(),
                (100, 100)
            )
        except Exception as e:
            print(f"Error cargando canecas: {e}")
            # Crear canecas simples como fallback
            self.canecaB = pygame.Surface((100, 100))
            self.canecaB.fill((255, 255, 255))
            self.canecaV = pygame.Surface((100, 100))
            self.canecaV.fill((0, 255, 0))
            self.canecaN = pygame.Surface((100, 100))
            self.canecaN.fill((100, 100, 100))
        
        # Posiciones de canecas
        self.canecas_j1 = {"negra": (100, 450), "blanca": (250, 450), "verde": (400, 450)}
        self.canecas_j2 = {"negra": (700, 450), "blanca": (850, 450), "verde": (1000, 450)}
        
        # Clasificación de basura
        self.clasificacion = {
            "Botella.png": "blanca",
            "Lata.png": "blanca",
            "Papel.png": "blanca",
            "Carton.png": "blanca",
            "Aluminio.png": "negra",
            "Banano.png": "verde",
            "Manzana.png": "verde",
            "Pescado.png": "verde",
        }
        
        # Cargar imágenes de basura
        self.nombres = list(self.clasificacion.keys())
        self.imagenes = {}
        
        try:
            for n in self.nombres:
                img = pygame.image.load(f"assets/CosasDeMinijuegos/Basura/{n}").convert_alpha()
                self.imagenes[n] = pygame.transform.scale(img, (80, 80))
        except Exception as e:
            print(f"Error cargando basura: {e}")
            # Crear imágenes simples como fallback
            for n in self.nombres:
                surf = pygame.Surface((80, 80))
                surf.fill((200, 200, 0))
                self.imagenes[n] = surf
        
        # Variables del juego
        self.puntaje1 = 0
        self.puntaje2 = 0
        self.tiempo_limite = 30  # segundos
        self.inicio = pygame.time.get_ticks()
        
        # Basura actual para cada jugador
        self.basura_j1 = random.choice(self.nombres)
        self.basura_j2 = random.choice(self.nombres)
        
        # Estado del juego
        self.game_state = "PLAYING"  # PLAYING, GAME_OVER
    
    def nueva_basura(self, jugador):
        """Generar nueva basura para un jugador"""
        if jugador == 1:
            self.basura_j1 = random.choice(self.nombres)
        else:
            self.basura_j2 = random.choice(self.nombres)
    
    def handle_event(self, event):
        if not self.can_handle_input or self.transitioning or self.transition.active:
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._start_transition(lambda: self.game.state_stack.pop())
            
            if self.game_state == "PLAYING":
                correcta_j1 = self.clasificacion[self.basura_j1]
                correcta_j2 = self.clasificacion[self.basura_j2]
                
                # Controles Jugador 1
                if event.key == pygame.K_w:
                    self.puntaje1 += 1 if correcta_j1 == "blanca" else -1
                    self.nueva_basura(1)
                elif event.key == pygame.K_a:
                    self.puntaje1 += 1 if correcta_j1 == "negra" else -1
                    self.nueva_basura(1)
                elif event.key == pygame.K_d:
                    self.puntaje1 += 1 if correcta_j1 == "verde" else -1
                    self.nueva_basura(1)
                
                # Controles Jugador 2
                elif event.key == pygame.K_UP:
                    self.puntaje2 += 1 if correcta_j2 == "blanca" else -1
                    self.nueva_basura(2)
                elif event.key == pygame.K_LEFT:
                    self.puntaje2 += 1 if correcta_j2 == "negra" else -1
                    self.nueva_basura(2)
                elif event.key == pygame.K_RIGHT:
                    self.puntaje2 += 1 if correcta_j2 == "verde" else -1
                    self.nueva_basura(2)
            
            elif self.game_state == "GAME_OVER":
                if event.key == pygame.K_RETURN:
                    self._start_transition(lambda: self.game.state_stack.pop())
    
    def _start_transition(self, callback):
        self.transitioning = True
        self.can_handle_input = False
        self.transition.start_fade_out(callback)
    
    def update(self, dt):
        self.transition.update(dt)
        
        if not self.transition.active and self.transitioning:
            self.transitioning = False
            self.can_handle_input = True
        
        # Actualizar tiempo
        if self.game_state == "PLAYING":
            tiempo_actual = (pygame.time.get_ticks() - self.inicio) / 1000
            tiempo_restante = max(0, self.tiempo_limite - tiempo_actual)
            
            if tiempo_restante <= 0:
                self.game_state = "GAME_OVER"
    
    def render(self, screen):
        # Dibujar fondo
        screen.blit(self.fondo, (0, 0))
        
        # Tapar la línea negra con un color oscuro para disimularla
        pygame.draw.rect(screen, (30, 30, 40), (SCREEN_WIDTH // 2 - 1, 0, 3, SCREEN_HEIGHT))
        
        # Dibujar canecas
        for tipo, pos in self.canecas_j1.items():
            if tipo == "negra":
                screen.blit(self.canecaN, pos)
            elif tipo == "blanca":
                screen.blit(self.canecaB, pos)
            elif tipo == "verde":
                screen.blit(self.canecaV, pos)
        
        for tipo, pos in self.canecas_j2.items():
            if tipo == "negra":
                screen.blit(self.canecaN, pos)
            elif tipo == "blanca":
                screen.blit(self.canecaB, pos)
            elif tipo == "verde":
                screen.blit(self.canecaV, pos)
        
        # Dibujar basura actual
        screen.blit(self.imagenes[self.basura_j1], (SCREEN_WIDTH // 4 - 40, 200))
        screen.blit(self.imagenes[self.basura_j2], ((3 * SCREEN_WIDTH) // 4 - 40, 200))
        
        # Calcular tiempo restante
        if self.game_state == "PLAYING":
            tiempo_actual = (pygame.time.get_ticks() - self.inicio) / 1000
            tiempo_restante = max(0, self.tiempo_limite - tiempo_actual)
        else:
            tiempo_restante = 0
        
        # Dibujar puntajes y tiempo
        screen.blit(self.font.render(f"P1: {self.puntaje1}", True, WHITE), (30, 20))
        screen.blit(self.font.render(f"P2: {self.puntaje2}", True, WHITE), (SCREEN_WIDTH - 200, 20))
        
        pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH // 2 - 40, 15, 80, 35))
        tiempo_txt = self.font.render(f"{int(tiempo_restante)}", True, WHITE)
        screen.blit(tiempo_txt, (SCREEN_WIDTH // 2 - tiempo_txt.get_width() // 2, 20))
        
        # Mostrar pantalla de fin de juego
        if self.game_state == "GAME_OVER":
            self.mostrar_overlay_ganador(screen)
        
        # Renderizar transición
        self.transition.render(screen)
    
    def mostrar_overlay_ganador(self, screen):
        """Mostrar overlay con el resultado final"""
        mensaje = ""
        if self.puntaje1 > self.puntaje2:
            mensaje = "¡Felicidades Jugador 1, ganaste!"
        elif self.puntaje2 > self.puntaje1:
            mensaje = "¡Felicidades Jugador 2, ganaste!"
        else:
            mensaje = "¡Empate!"
        
        cuadro = pygame.Rect(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 100, 500, 200)
        pygame.draw.rect(screen, BLACK, cuadro)
        pygame.draw.rect(screen, WHITE, cuadro, 4)
        
        mensaje_surf = self.font.render(mensaje, True, WHITE)
        mensaje_rect = mensaje_surf.get_rect(center=(cuadro.centerx, cuadro.y + 50))
        screen.blit(mensaje_surf, mensaje_rect)
        
        marcador = f"Jugador 1: {self.puntaje1}   Jugador 2: {self.puntaje2}"
        marcador_surf = self.font.render(marcador, True, WHITE)
        marcador_rect = marcador_surf.get_rect(center=(cuadro.centerx, cuadro.y + 100))
        screen.blit(marcador_surf, marcador_rect)
        
        continuar = "Presiona ENTER para continuar"
        continuar_surf = self.font_small.render(continuar, True, WHITE)
        continuar_rect = continuar_surf.get_rect(center=(cuadro.centerx, cuadro.y + 150))
        screen.blit(continuar_surf, continuar_rect)

print("A La Caneca - Minijuego integrado como estado")
