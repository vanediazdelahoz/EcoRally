# Minijuego "Cielo en Crisis"

import pygame
import random
from core.config import config
from core.state import State
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK
from core.utils import load_font
from core.effects import TransitionEffect


class CieloEnCrisisState(State):
    def __init__(self, game):
        super().__init__(game)
        pygame.mouse.set_visible(False)

        self.transition = TransitionEffect(0.15)
        self.transition.start_fade_in()

        self.transitioning = False
        self.can_handle_input = True

        self.font = load_font("assets/fonts/PublicPixel.ttf", 22)
        self.font_small = load_font("assets/fonts/PublicPixel.ttf", 16)

        character_names = ["Rosalba", "Tinú", "Sofia", "Luis"]
        self.player1_name = character_names[config.characters[0]]
        self.player2_name = (
            character_names[config.characters[1]]
            if not config.machine_mode
            else f"Bot {character_names[config.characters[1]]}")

        try:
            self.fondo = pygame.image.load(
                "assets/images/minigames/sky_crisis/background_sky_crisis.png").convert()
            self.fondo = pygame.transform.scale(
                self.fondo, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception as e:
            self.fondo = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.fondo.fill((30, 30, 100))

        self.tipos_basura = [
            {"nombre": "Aluminio", "img": "aluminum.png", "puntos": 1},
            {"nombre": "Banano", "img": "banana.png", "puntos": 1},
            {"nombre": "Botella", "img": "bottle.png", "puntos": 1},
            {"nombre": "Lata", "img": "can.png", "puntos": 1},
            {"nombre": "Manzana", "img": "apple.png", "puntos": 1},
            {"nombre": "Papel", "img": "paper.png", "puntos": 1},
            {"nombre": "Pescado", "img": "fish.png", "puntos": 1},
            {"nombre": "Carton", "img": "cardboard.png", "puntos": 1},]

        try:
            for basura in self.tipos_basura:
                imagen = pygame.image.load(
                    f"assets/images/minigames/trash/{basura['img']}"
                ).convert_alpha()
                imagen = pygame.transform.scale(imagen, (40, 40))
                basura["superficie"] = imagen
        except Exception as e:
            for basura in self.tipos_basura:
                surf = pygame.Surface((40, 40))
                surf.fill((200, 200, 0))
                basura["superficie"] = surf

        try:
            self.caneca_img = pygame.image.load(
                "assets/images/minigames/sky_crisis/bin_sky.png").convert_alpha()
            self.caneca_img = pygame.transform.scale(self.caneca_img, (100, 100))
        except Exception as e:
            self.caneca_img = pygame.Surface((100, 100))
            self.caneca_img.fill((100, 100, 100))

        self.jugador1_pos = pygame.Rect(
            SCREEN_WIDTH // 4 - 50, SCREEN_HEIGHT - 110, 100, 100)
        self.jugador2_pos = pygame.Rect(
            3 * SCREEN_WIDTH // 4 - 50, SCREEN_HEIGHT - 110, 100, 100)

        self.player2_is_bot = config.machine_mode
        self.bot_interval = 20
        self.bot_last_move_time = pygame.time.get_ticks()

        self.basura_jugador1 = []
        self.basura_jugador2 = []

        self.puntaje1 = 0
        self.puntaje2 = 0

        self.velocidad = 5
        self.vel_bajada = 9

        self.tiempo_juego = 30
        self.inicio_tiempo = pygame.time.get_ticks()

        self.game_state = "PLAYING"

        self.random_j1 = random.Random()
        self.random_j2 = random.Random()

        pygame.time.set_timer(pygame.USEREVENT + 1, 600)
        pygame.time.set_timer(pygame.USEREVENT + 2, 600)

    def handle_event(self, event):
        if not self.can_handle_input or self.transitioning or self.transition.active:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._start_transition(lambda: self.game.state_stack.pop())

            elif self.game_state == "GAME_OVER":
                if event.key == pygame.K_RETURN:
                    self._end_minigame()

        if event.type == pygame.USEREVENT + 1:
            tipo1 = self.random_j1.choice(self.tipos_basura)
            x1 = self.random_j1.randint(0, SCREEN_WIDTH // 2 - 40)
            self.basura_jugador1.append(
                {"rect": pygame.Rect(x1, -40, 40, 40), "tipo": tipo1})

        if event.type == pygame.USEREVENT + 2:
            tipo2 = self.random_j2.choice(self.tipos_basura)
            x2 = self.random_j2.randint(SCREEN_WIDTH // 2, SCREEN_WIDTH - 40)
            self.basura_jugador2.append(
                {"rect": pygame.Rect(x2, -40, 40, 40), "tipo": tipo2})

    def _start_transition(self, callback):
        self.transitioning = True
        self.can_handle_input = False
        self.transition.start_fade_out(callback)

    def _end_minigame(self):
        pygame.time.set_timer(pygame.USEREVENT + 1, 0)
        pygame.time.set_timer(pygame.USEREVENT + 2, 0)

        if len(self.game.state_stack) >= 2:
            board_game = self.game.state_stack[-2]
            if hasattr(board_game, "continue_after_minigame"):
                board_game.continue_after_minigame(self.puntaje1, self.puntaje2)

        self._start_transition(lambda: self.game.state_stack.pop())

    def update(self, dt):
        self.transition.update(dt)

        if not self.transition.active and self.transitioning:
            self.transitioning = False
            self.can_handle_input = True

        if self.game_state == "PLAYING":
            tiempo_actual = (pygame.time.get_ticks() - self.inicio_tiempo) / 1000
            tiempo_restante = max(0, self.tiempo_juego - tiempo_actual)

            if tiempo_restante <= 0:
                self.game_state = "GAME_OVER"
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)
                pygame.time.set_timer(pygame.USEREVENT + 2, 0)
                return

            teclas = pygame.key.get_pressed()
            velocidad = self.velocidad

            if teclas[pygame.K_a] and self.jugador1_pos.left > 0:
                self.jugador1_pos.x -= velocidad
            if teclas[pygame.K_d] and self.jugador1_pos.right < SCREEN_WIDTH // 2:
                self.jugador1_pos.x += velocidad

            if not self.player2_is_bot:
                if teclas[pygame.K_LEFT] and self.jugador2_pos.left > SCREEN_WIDTH // 2:
                    self.jugador2_pos.x -= velocidad
                if teclas[pygame.K_RIGHT] and self.jugador2_pos.right < SCREEN_WIDTH:
                    self.jugador2_pos.x += velocidad
            else:
                ahora = pygame.time.get_ticks()
                if (
                    ahora - self.bot_last_move_time > self.bot_interval
                    and self.basura_jugador2):
                    basura_mas_cercana = max(
                        self.basura_jugador2, key=lambda b: b["rect"].y)

                    centro_bot = self.jugador2_pos.centerx
                    centro_basura = basura_mas_cercana["rect"].centerx

                    if (
                        centro_bot < centro_basura - 5
                        and self.jugador2_pos.right < SCREEN_WIDTH):
                        self.jugador2_pos.x += velocidad
                    elif (
                        centro_bot > centro_basura + 5
                        and self.jugador2_pos.left > SCREEN_WIDTH // 2):
                        self.jugador2_pos.x -= velocidad

                    self.bot_last_move_time = ahora

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
        screen.blit(self.fondo, (0, 0))

        pygame.draw.line(
            screen, BLACK, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 2)

        for b in self.basura_jugador1:
            screen.blit(b["tipo"]["superficie"], b["rect"])

        for b in self.basura_jugador2:
            screen.blit(b["tipo"]["superficie"], b["rect"])

        screen.blit(self.caneca_img, self.jugador1_pos)
        screen.blit(self.caneca_img, self.jugador2_pos)

        texto1 = self.font.render(f"{self.player1_name}: {self.puntaje1}", True, WHITE)
        screen.blit(texto1, (20, 10))

        texto2 = self.font.render(f"{self.player2_name}: {self.puntaje2}", True, WHITE)
        screen.blit(texto2, (SCREEN_WIDTH - texto2.get_width() - 20, 10))

        tiempo_actual = (pygame.time.get_ticks() - self.inicio_tiempo) / 1000
        tiempo_restante = max(0, self.tiempo_juego - tiempo_actual)

        tiempo_rect = pygame.Rect(SCREEN_WIDTH // 2 - 40, 10, 80, 40)
        pygame.draw.rect(screen, BLACK, tiempo_rect)
        pygame.draw.rect(screen, WHITE, tiempo_rect, 2)
        tiempo_txt = self.font.render(str(int(tiempo_restante)), True, WHITE)
        txt_rect = tiempo_txt.get_rect(center=tiempo_rect.center)
        screen.blit(tiempo_txt, txt_rect)

        if self.game_state == "GAME_OVER":
            self.mostrar_overlay_ganador(screen)

        self.transition.render(screen)

    def mostrar_overlay_ganador(self, screen):
        if self.puntaje1 > self.puntaje2:
            mensaje = f"¡Felicidades {self.player1_name}, ganaste!"
        elif self.puntaje2 > self.puntaje1:
            mensaje = f"¡Felicidades {self.player2_name}, ganaste!"
        else:
            mensaje = "¡Empate!"

        lines = [
            mensaje,
            f"{self.player1_name}: {self.puntaje1}   {self.player2_name}: {self.puntaje2}",]

        max_width = 0
        for line in lines:
            text_surf = self.font.render(line, True, WHITE)
            max_width = max(max_width, text_surf.get_width())

        box_width = max_width + 60
        box_height = 120
        cuadro = pygame.Rect(
            SCREEN_WIDTH // 2 - box_width // 2,
            SCREEN_HEIGHT // 2 - box_height // 2,
            box_width,
            box_height,)

        pygame.draw.rect(screen, BLACK, cuadro)
        pygame.draw.rect(screen, WHITE, cuadro, 4)

        mensaje_surf = self.font.render(mensaje, True, WHITE)
        mensaje_rect = mensaje_surf.get_rect(center=(cuadro.centerx, cuadro.y + 30))
        screen.blit(mensaje_surf, mensaje_rect)

        marcador = f"{self.player1_name}: {self.puntaje1}   {self.player2_name}: {self.puntaje2}"
        marcador_surf = self.font.render(marcador, True, WHITE)
        marcador_rect = marcador_surf.get_rect(center=(cuadro.centerx, cuadro.y + 70))
        screen.blit(marcador_surf, marcador_rect)

        continuar = "Presiona ENTER para continuar"
        continuar_surf = self.font_small.render(continuar, True, WHITE)
        continuar_rect = continuar_surf.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))

        bg_rect = pygame.Rect(
            continuar_rect.x - 10,
            continuar_rect.y - 5,
            continuar_rect.width + 20,
            continuar_rect.height + 10,)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))
        screen.blit(bg_surface, bg_rect)
        screen.blit(continuar_surf, continuar_rect)
