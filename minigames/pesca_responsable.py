import pygame
import random
from core.state import State
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK
from core.utils import load_font
from core.effects import TransitionEffect

class PescaResponsableState(State):
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
            self.background_img = pygame.image.load("assets/CosasDeMinijuegos/FondoPesca.jpg").convert()
            self.background_img = pygame.transform.scale(self.background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception as e:
            print(f"Error cargando fondo: {e}")
            self.background_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background_img.fill((0, 100, 200))
        
        # Cargar imágenes de peces
        try:
            self.pez_bueno_img = pygame.image.load("assets/CosasDeMinijuegos/Peces/PezBueno.png").convert_alpha()
            self.pez_bueno_img = pygame.transform.scale(self.pez_bueno_img, (60, 40))
            
            self.pez_malo_img = pygame.image.load("assets/CosasDeMinijuegos/Peces/PezMalo.png").convert_alpha()
            self.pez_malo_img = pygame.transform.scale(self.pez_malo_img, (60, 40))
        except Exception as e:
            print(f"Error cargando peces: {e}")
            # Crear peces simples como fallback
            self.pez_bueno_img = pygame.Surface((60, 40))
            self.pez_bueno_img.fill((0, 255, 0))
            self.pez_malo_img = pygame.Surface((60, 40))
            self.pez_malo_img.fill((255, 0, 0))
        
        # Cargar imagen de anzuelo
        try:
            self.anzuelo_img = pygame.image.load("assets/CosasDeMinijuegos/Anzuelo.png").convert_alpha()
            self.anzuelo_img = pygame.transform.scale(self.anzuelo_img, (30, 30))
        except Exception as e:
            print(f"Error cargando anzuelo: {e}")
            self.anzuelo_img = pygame.Surface((30, 30))
            self.anzuelo_img.fill((150, 150, 150))
        
        # Posiciones de anzuelos
        self.anzuelo1_pos = pygame.Rect(SCREEN_WIDTH // 4 - 15, SCREEN_HEIGHT // 2, 30, 30)
        self.anzuelo2_pos = pygame.Rect(3 * SCREEN_WIDTH // 4 - 15, SCREEN_HEIGHT // 2, 30, 30)
        
        # Peces
        self.peces = []
        
        # Puntajes
        self.puntaje1 = 0
        self.puntaje2 = 0
        
        # Tiempo
        self.tiempo_juego = 30  # segundos
        self.inicio_tiempo = pygame.time.get_ticks()
        
        # Estado del juego
        self.game_state = "PLAYING"  # PLAYING, GAME_OVER
        
        # Configurar temporizador para generar peces
        pygame.time.set_timer(pygame.USEREVENT + 3, 1000)  # Cada segundo
    
    def generar_pez(self):
        """Generar un nuevo pez"""
        tipo = random.choice(["bueno", "malo"])
        x = random.randint(0, SCREEN_WIDTH - 60)
        y = random.randint(100, SCREEN_HEIGHT - 200)
        velocidad_x = random.choice([-2, -1, 1, 2])
        velocidad_y = random.choice([-1, 0, 1])
        
        pez = {
            "rect": pygame.Rect(x, y, 60, 40),
            "tipo": tipo,
            "vel_x": velocidad_x,
            "vel_y": velocidad_y
        }
        
        self.peces.append(pez)
    
    def handle_event(self, event):
        if not self.can_handle_input or self.transitioning or self.transition.active:
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._start_transition(lambda: self.game.state_stack.pop())
            
            elif self.game_state == "GAME_OVER":
                if event.key == pygame.K_RETURN:
                    self._start_transition(lambda: self.game.state_stack.pop())
        
        # Generar peces
        if event.type == pygame.USEREVENT + 3:
            self.generar_pez()
    
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
                pygame.time.set_timer(pygame.USEREVENT + 3, 0)
            
            # Mover anzuelos
            teclas = pygame.key.get_pressed()
            velocidad = 5
            
            # Anzuelo 1 (Jugador 1)
            if teclas[pygame.K_w] and self.anzuelo1_pos.top > 0:
                self.anzuelo1_pos.y -= velocidad
            if teclas[pygame.K_s] and self.anzuelo1_pos.bottom < SCREEN_HEIGHT:
                self.anzuelo1_pos.y += velocidad
            if teclas[pygame.K_a] and self.anzuelo1_pos.left > 0:
                self.anzuelo1_pos.x -= velocidad
            if teclas[pygame.K_d] and self.anzuelo1_pos.right < SCREEN_WIDTH // 2:
                self.anzuelo1_pos.x += velocidad
            
            # Anzuelo 2 (Jugador 2)
            if teclas[pygame.K_UP] and self.anzuelo2_pos.top > 0:
                self.anzuelo2_pos.y -= velocidad
            if teclas[pygame.K_DOWN] and self.anzuelo2_pos.bottom < SCREEN_HEIGHT:
                self.anzuelo2_pos.y += velocidad
            if teclas[pygame.K_LEFT] and self.anzuelo2_pos.left > SCREEN_WIDTH // 2:
                self.anzuelo2_pos.x -= velocidad
            if teclas[pygame.K_RIGHT] and self.anzuelo2_pos.right < SCREEN_WIDTH:
                self.anzuelo2_pos.x += velocidad
            
            # Mover peces y detectar colisiones
            for pez in self.peces[:]:
                pez["rect"].x += pez["vel_x"]
                pez["rect"].y += pez["vel_y"]
                
                # Rebotar en bordes
                if pez["rect"].left <= 0 or pez["rect"].right >= SCREEN_WIDTH:
                    pez["vel_x"] *= -1
                if pez["rect"].top <= 0 or pez["rect"].bottom >= SCREEN_HEIGHT:
                    pez["vel_y"] *= -1
                
                # Colisión con anzuelo 1
                if pez["rect"].colliderect(self.anzuelo1_pos):
                    if pez["tipo"] == "bueno":
                        self.puntaje1 += 1
                    else:
                        self.puntaje1 -= 1
                    self.peces.remove(pez)
                    continue
                
                # Colisión con anzuelo 2
                if pez["rect"].colliderect(self.anzuelo2_pos):
                    if pez["tipo"] == "bueno":
                        self.puntaje2 += 1
                    else:
                        self.puntaje2 -= 1
                    self.peces.remove(pez)
                    continue
                
                # Eliminar peces que salen de pantalla
                if (pez["rect"].right < 0 or pez["rect"].left > SCREEN_WIDTH or
                    pez["rect"].bottom < 0 or pez["rect"].top > SCREEN_HEIGHT):
                    self.peces.remove(pez)
    
    def render(self, screen):
        # Dibujar fondo
        screen.blit(self.background_img, (0, 0))
        
        # Dibujar línea divisoria
        pygame.draw.line(screen, BLACK, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 2)
        
        # Dibujar peces
        for pez in self.peces:
            if pez["tipo"] == "bueno":
                screen.blit(self.pez_bueno_img, pez["rect"])
            else:
                screen.blit(self.pez_malo_img, pez["rect"])
        
        # Dibujar anzuelos
        screen.blit(self.anzuelo_img, self.anzuelo1_pos)
        screen.blit(self.anzuelo_img, self.anzuelo2_pos)
        
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

print("Pesca Responsable - Minijuego integrado como estado")
