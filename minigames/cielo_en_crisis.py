import pygame
import random
from core.state import State
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK
from core.utils import load_font
from core.effects import TransitionEffect

class CieloEnCrisisState(State):
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
        self.font = load_font("assets/fonts/PublicPixel.ttf", 22)
        self.font_small = load_font("assets/fonts/PublicPixel.ttf", 16)
        
        # Cargar fondo
        try:
            self.fondo = pygame.image.load("assets/CosasDeMinijuegos/FondoLluvia.png").convert()
            self.fondo = pygame.transform.scale(self.fondo, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception as e:
            print(f"Error cargando fondo: {e}")
            self.fondo = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.fondo.fill((30, 30, 100))
        
        # Cargar imágenes de basura
        self.tipos_basura = [
            {"nombre": "Aluminio", "img": "Aluminio.png", "puntos": 1},
            {"nombre": "Banano", "img": "Banano.png", "puntos": 1},
            {"nombre": "Botella", "img": "Botella.png", "puntos": 1},
            {"nombre": "Lata", "img": "Lata.png", "puntos": 1},
            {"nombre": "Manzana", "img": "Manzana.png", "puntos": 1},
            {"nombre": "Papel", "img": "Papel.png", "puntos": 1},
            {"nombre": "Pescado", "img": "Pescado.png", "puntos": 1},
            {"nombre": "Carton", "img": "Carton.png", "puntos": 1},
        ]
        
        try:
            for basura in self.tipos_basura:
                imagen = pygame.image.load(f"assets/CosasDeMinijuegos/Basura/{basura['img']}").convert_alpha()
                imagen = pygame.transform.scale(imagen, (40, 40))
                basura["superficie"] = imagen
        except Exception as e:
            print(f"Error cargando basura: {e}")
            # Crear imágenes simples como fallback
            for basura in self.tipos_basura:
                surf = pygame.Surface((40, 40))
                surf.fill((200, 200, 0))
                basura["superficie"] = surf
        
        # Cargar imagen de caneca
        try:
            self.caneca_img = pygame.image.load("assets/CosasDeMinijuegos/Canasta de basura/CanecaX.png").convert_alpha()
            self.caneca_img = pygame.transform.scale(self.caneca_img, (100, 100))
        except Exception as e:
            print(f"Error cargando caneca: {e}")
            self.caneca_img = pygame.Surface((100, 100))
            self.caneca_img.fill((100, 100, 100))
        
        # Jugadores
        self.jugador1_pos = pygame.Rect(SCREEN_WIDTH // 4 - 50, SCREEN_HEIGHT - 110, 100, 100)
        self.jugador2_pos = pygame.Rect(3 * SCREEN_WIDTH // 4 - 50, SCREEN_HEIGHT - 110, 100, 100)
        
        # Basura
        self.basura_jugador1 = []
        self.basura_jugador2 = []
        
        # Puntajes
        self.puntaje1 = 0
        self.puntaje2 = 0
        
        # Velocidad
        self.velocidad = 5
        self.vel_bajada = 9
        
        # Tiempo
        self.tiempo_juego = 30  # segundos
        self.inicio_tiempo = pygame.time.get_ticks()
        
        # Estado del juego
        self.game_state = "PLAYING"  # PLAYING, GAME_OVER
        
        # Generadores de números aleatorios separados
        self.random_j1 = random.Random()
        self.random_j2 = random.Random()
        
        # Configurar temporizadores para generar basura
        pygame.time.set_timer(pygame.USEREVENT + 1, 600)  # Basura J1
        pygame.time.set_timer(pygame.USEREVENT + 2, 600)  # Basura J2
    
    def handle_event(self, event):
        if not self.can_handle_input or self.transitioning or self.transition.active:
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._start_transition(lambda: self.game.state_stack.pop())
            
            elif self.game_state == "GAME_OVER":
                if event.key == pygame.K_RETURN:
                    self._start_transition(lambda: self.game.state_stack.pop())
        
        # Generar basura
        if event.type == pygame.USEREVENT + 1:
            tipo1 = self.random_j1.choice(self.tipos_basura)
            x1 = self.random_j1.randint(0, SCREEN_WIDTH // 2 - 40)
            self.basura_jugador1.append({"rect": pygame.Rect(x1, -40, 40, 40), "tipo": tipo1})
        
        if event.type == pygame.USEREVENT + 2:
            tipo2 = self.random_j2.choice(self.tipos_basura)
            x2 = self.random_j2.randint(SCREEN_WIDTH // 2, SCREEN_WIDTH - 40)
            self.basura_jugador2.append({"rect": pygame.Rect(x2, -40, 40, 40), "tipo": tipo2})
    
    def _start_transition(self, callback):
        self.transitioning = True
        self.can_handle_input = False
        self.transition.start_fade_out(callback)
    
    def update(self, dt):
        self.transition.update(dt)
        
        if not self.transition.active and self.transitioning:
            self.transitioning = False
            self.can_handle_input = True
        
        if self.game_state == "PLAYING":
            # Actualizar tiempo
            tiempo_actual = (pygame.time.get_ticks() - self.inicio_tiempo) / 1000
            tiempo_restante = max(0, self.tiempo_juego - tiempo_actual)
            
            if tiempo_restante <= 0:
                self.game_state = "GAME_OVER"
                # Detener generación de basura
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)
                pygame.time.set_timer(pygame.USEREVENT + 2, 0)
            
            # Mover jugadores
            teclas = pygame.key.get_pressed()
            velocidad = self.velocidad
            
            # Jugador 1
            if teclas[pygame.K_a] and self.jugador1_pos.left > 0:
                self.jugador1_pos.x -= velocidad
            if teclas[pygame.K_d] and self.jugador1_pos.right < SCREEN_WIDTH // 2:
                self.jugador1_pos.x += velocidad
            
            # Jugador 2
            if teclas[pygame.K_LEFT] and self.jugador2_pos.left > SCREEN_WIDTH // 2:
                self.jugador2_pos.x -= velocidad
            if teclas[pygame.K_RIGHT] and self.jugador2_pos.right < SCREEN_WIDTH:
                self.jugador2_pos.x += velocidad
            
            # Mover basura
            for b in self.basura_jugador1[:]:
                b["rect"].y += self.vel_bajada - (int(tiempo_restante) // 10)
                if b["rect"].colliderect(self.jugador1_pos):
                    self.puntaje1 += b["tipo"]["puntos"]
                    self.basura_jugador1.remove(b)
                elif b["rect"].y > SCREEN_HEIGHT:
                    self.basura_jugador1.remove(b)
            
            for b in self.basura_jugador2[:]:
                b["rect"].y += self.vel_bajada - (int(tiempo_restante) // 10)
                if b["rect"].colliderect(self.jugador2_pos):
                    self.puntaje2 += b["tipo"]["puntos"]
                    self.basura_jugador2.remove(b)
                elif b["rect"].y > SCREEN_HEIGHT:
                    self.basura_jugador2.remove(b)
    
    def render(self, screen):
        # Dibujar fondo
        screen.blit(self.fondo, (0, 0))
        
        # Dibujar línea divisoria
        pygame.draw.line(screen, BLACK, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 2)
        
        # Dibujar basura
        for b in self.basura_jugador1:
            screen.blit(b["tipo"]["superficie"], b["rect"])
        
        for b in self.basura_jugador2:
            screen.blit(b["tipo"]["superficie"], b["rect"])
        
        # Dibujar jugadores (canecas)
        screen.blit(self.caneca_img, self.jugador1_pos)
        screen.blit(self.caneca_img, self.jugador2_pos)
        
        # Dibujar puntajes
        texto1 = self.font.render(f"Jugador 1: {self.puntaje1}", True, WHITE)
        texto2 = self.font.render(f"Jugador 2: {self.puntaje2}", True, WHITE)
        screen.blit(texto1, (20, 10))
        screen.blit(texto2, (SCREEN_WIDTH - 220, 10))
        
        # Dibujar tiempo
        tiempo_actual = (pygame.time.get_ticks() - self.inicio_tiempo) / 1000
        tiempo_restante = max(0, self.tiempo_juego - tiempo_actual)
        
        tiempo_rect = pygame.Rect(SCREEN_WIDTH // 2 - 40, 10, 80, 40)
        pygame.draw.rect(screen, BLACK, tiempo_rect)
        pygame.draw.rect(screen, WHITE, tiempo_rect, 2)
        tiempo_txt = self.font.render(str(int(tiempo_restante)), True, WHITE)
        txt_rect = tiempo_txt.get_rect(center=tiempo_rect.center)
        screen.blit(tiempo_txt, txt_rect)
        
        # Mostrar pantalla de fin de juego
        if self.game_state == "GAME_OVER":
            self.mostrar_overlay_ganador(screen)
        
        # Renderizar transición
        self.transition.render(screen)
    
    def mostrar_overlay_ganador(self, screen):
        """Mostrar overlay con el resultado final"""
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

print("Cielo En Crisis - Minijuego integrado como estado")
