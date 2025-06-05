# minigames/pesca_responsable.py
import pygame
import random
from core.config import config
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

        # Obtener nombres de personajes
        character_names = ["Rosalba", "Tinú", "Sofia", "Luis"]
        self.player1_name = character_names[config.characters[0]]
        self.player2_name = (
            character_names[config.characters[1]]
            if not config.machine_mode
            else f"Bot {character_names[config.characters[1]]}"
        )

        # Configuración del juego
        self.FPS = 60
        self.ROUND_TIME = 30  # segundos
        self.PLAYER_SIZE = 150
        self.TRASH_SIZE = 40
        self.TOP_MARGIN = 250
        self.TRASH_LIMIT_BOTTOM = SCREEN_HEIGHT - 50

        # Configurar posiciones de barcos ANTES de cargar imágenes
        self.BARCO1_POS = (80, self.TOP_MARGIN - 160)
        self.BARCO2_POS = (SCREEN_WIDTH - 280, self.TOP_MARGIN - 160)

        # Configurar jugadores (cebos) ANTES de cargar imágenes
        self.players = [
            {
                "rect": pygame.Rect(
                    self.BARCO1_POS[0] + 100,  # Centrado respecto al barco
                    self.BARCO1_POS[1] + 120,  # Justo debajo del barco
                    self.PLAYER_SIZE // 2,
                    self.PLAYER_SIZE // 2,
                ),
                "score": 0,
                "image": None,  # Se asignará en load_images
                "keys": {
                    "up": pygame.K_w,
                    "down": pygame.K_s,
                    "left": pygame.K_a,
                    "right": pygame.K_d,
                },
            },
            {
                "rect": pygame.Rect(
                    self.BARCO2_POS[0] - 50,
                    self.BARCO2_POS[1] + 120,
                    self.PLAYER_SIZE // 2,
                    self.PLAYER_SIZE // 2,
                ),
                "score": 0,
                "image": None,  # Se asignará en load_images
                "keys": {
                    "up": pygame.K_UP,
                    "down": pygame.K_DOWN,
                    "left": pygame.K_LEFT,
                    "right": pygame.K_RIGHT,
                },
            },
        ]

        # AHORA cargar imágenes (después de crear self.players)
        self.load_images()

        # Lista de basura
        self.trash_list = []

        # Tiempo
        self.start_ticks = pygame.time.get_ticks()

        # Estado del juego
        self.game_state = "PLAYING"  # PLAYING, GAME_OVER

        # Contador para generar basura (como en la versión antigua)
        self.trash_spawn_counter = 0
        self.trash_spawn_frequency = (
            1  # Generar basura cada frame (como en la versión antigua)
        )

    def load_images(self):
        """Cargar todas las imágenes necesarias"""
        try:
            # Cargar imagen de fondo
            self.background_img = pygame.image.load(
                "assets/CosasDeMinijuegos/FondoPesca.jpg"
            ).convert()
            self.background_img = pygame.transform.scale(
                self.background_img, (SCREEN_WIDTH, SCREEN_HEIGHT)
            )
        except Exception as e:
            print(f"Error cargando fondo: {e}")
            self.background_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background_img.fill((0, 100, 200))

        try:
            # Cargar barcos
            self.BARCO1_IMAGE = pygame.image.load(
                "assets/CosasDeMinijuegos/Barco/Barco Izquierda.png"
            ).convert_alpha()
            self.BARCO2_IMAGE = pygame.image.load(
                "assets/CosasDeMinijuegos/Barco/Barco Derecha.png"
            ).convert_alpha()
            self.BARCO1_IMAGE = pygame.transform.scale(self.BARCO1_IMAGE, (200, 200))
            self.BARCO2_IMAGE = pygame.transform.scale(self.BARCO2_IMAGE, (200, 200))
        except Exception as e:
            print(f"Error cargando barcos: {e}")
            self.BARCO1_IMAGE = pygame.Surface((200, 200))
            self.BARCO1_IMAGE.fill((139, 69, 19))
            self.BARCO2_IMAGE = pygame.Surface((200, 200))
            self.BARCO2_IMAGE.fill((139, 69, 19))

        try:
            # Cargar cebos/anzuelos
            player1_img = pygame.image.load(
                "assets/CosasDeMinijuegos/Barco/Cebo Izquierda.png"
            ).convert_alpha()
            player2_img = pygame.image.load(
                "assets/CosasDeMinijuegos/Barco/Cebo Derecha.png"
            ).convert_alpha()
            self.players[0]["image"] = pygame.transform.scale(
                player1_img, (self.PLAYER_SIZE, self.PLAYER_SIZE)
            )
            self.players[1]["image"] = pygame.transform.scale(
                player2_img, (self.PLAYER_SIZE, self.PLAYER_SIZE)
            )
        except Exception as e:
            print(f"Error cargando cebos: {e}")
            self.players[0]["image"] = pygame.Surface(
                (self.PLAYER_SIZE, self.PLAYER_SIZE)
            )
            self.players[0]["image"].fill((255, 255, 0))
            self.players[1]["image"] = pygame.Surface(
                (self.PLAYER_SIZE, self.PLAYER_SIZE)
            )
            self.players[1]["image"].fill((255, 255, 0))

        try:
            # Cargar imágenes de basura
            aluminio_img = pygame.image.load(
                "assets/CosasDeMinijuegos/Basura/Aluminio.png"
            ).convert_alpha()
            botella_img = pygame.image.load(
                "assets/CosasDeMinijuegos/Basura/Botella.png"
            ).convert_alpha()
            lata_img = pygame.image.load(
                "assets/CosasDeMinijuegos/Basura/Lata.png"
            ).convert_alpha()

            self.ALL_TRASH_IMAGES = [
                pygame.transform.scale(
                    aluminio_img, (self.TRASH_SIZE, self.TRASH_SIZE)
                ),
                pygame.transform.scale(botella_img, (self.TRASH_SIZE, self.TRASH_SIZE)),
                pygame.transform.scale(lata_img, (self.TRASH_SIZE, self.TRASH_SIZE)),
            ]
        except Exception as e:
            print(f"Error cargando basura: {e}")
            # Crear basura simple como fallback
            self.ALL_TRASH_IMAGES = []
            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
            for color in colors:
                trash_surf = pygame.Surface((self.TRASH_SIZE, self.TRASH_SIZE))
                trash_surf.fill(color)
                self.ALL_TRASH_IMAGES.append(trash_surf)

    def spawn_trash(self):
        """Generar nueva basura desde los lados (COMO EN LA VERSIÓN ANTIGUA)"""
        direction = random.choice(["left", "right"])
        y = random.randint(self.TOP_MARGIN, self.TRASH_LIMIT_BOTTOM - self.TRASH_SIZE)
        image = random.choice(self.ALL_TRASH_IMAGES)

        if direction == "right":
            x = SCREEN_WIDTH + random.randint(0, 100)
            speed = -3
        else:
            x = -self.TRASH_SIZE - random.randint(0, 100)
            speed = 3

        rect = pygame.Rect(x, y, self.TRASH_SIZE, self.TRASH_SIZE)
        self.trash_list.append({"rect": rect, "image": image, "speed": speed})

    def move_trash(self):
        """Mover toda la basura"""
        for trash in self.trash_list:
            trash["rect"].x += trash["speed"]

    def handle_player_input(self, player, keys_pressed):
        """Manejar input de jugadores"""
        speed = 4
        if keys_pressed[player["keys"]["up"]]:
            player["rect"].y -= speed
        if keys_pressed[player["keys"]["down"]]:
            player["rect"].y += speed
        if keys_pressed[player["keys"]["left"]]:
            player["rect"].x -= speed
        if keys_pressed[player["keys"]["right"]]:
            player["rect"].x += speed

        # Limitar al área acuática
        player["rect"].clamp_ip(
            pygame.Rect(
                0,
                self.TOP_MARGIN - player["rect"].height // 2,
                SCREEN_WIDTH,
                self.TRASH_LIMIT_BOTTOM - (self.TOP_MARGIN - player["rect"].height),
            )
        )

    def check_collisions(self):
        """Detectar colisiones entre jugadores y basura"""
        for player in self.players:
            for trash in self.trash_list[:]:
                if player["rect"].colliderect(trash["rect"]):
                    player["score"] += 1
                    self.trash_list.remove(trash)

    def handle_event(self, event):
        if not self.can_handle_input or self.transitioning or self.transition.active:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._start_transition(lambda: self.game.state_stack.pop())

            elif self.game_state == "GAME_OVER":
                if event.key == pygame.K_RETURN:
                    # Retornar al juego principal con los puntajes
                    self._end_minigame()

    def bot_move(self, player):
        """Movimiento automático del bot hacia la basura más cercana"""
        if not self.trash_list:
            return  # No hay basura

        target = min(
            self.trash_list,
            key=lambda t: abs(t["rect"].x - player["rect"].x)
            + abs(t["rect"].y - player["rect"].y),
        )
        speed = 3

        if player["rect"].x < target["rect"].x:
            player["rect"].x += speed
        elif player["rect"].x > target["rect"].x:
            player["rect"].x -= speed

        if player["rect"].y < target["rect"].y:
            player["rect"].y += speed
        elif player["rect"].y > target["rect"].y:
            player["rect"].y -= speed

        # Limitar al área acuática
        player["rect"].clamp_ip(
            pygame.Rect(
                0,
                self.TOP_MARGIN - player["rect"].height // 2,
                SCREEN_WIDTH,
                self.TRASH_LIMIT_BOTTOM - (self.TOP_MARGIN - player["rect"].height),
            )
        )

    def _start_transition(self, callback):
        self.transitioning = True
        self.can_handle_input = False
        self.transition.start_fade_out(callback)

    def _end_minigame(self):
        """Terminar minijuego y retornar puntajes al juego principal"""
        # Obtener referencia al BoardGameView
        if len(self.game.state_stack) >= 2:
            board_game = self.game.state_stack[-2]  # El estado anterior
            if hasattr(board_game, "continue_after_minigame"):
                board_game.continue_after_minigame(
                    self.players[0]["score"], self.players[1]["score"]
                )

        # Salir del minijuego
        self._start_transition(lambda: self.game.state_stack.pop())

    def update(self, dt):
        self.transition.update(dt)

        if not self.transition.active and self.transitioning:
            self.transitioning = False
            self.can_handle_input = True

        if self.game_state == "PLAYING":
            # Actualizar tiempo
            elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000
            time_left = self.ROUND_TIME - elapsed_time

            if time_left <= 0:
                self.game_state = "GAME_OVER"
                return

            # Manejar input de jugadores
            # Manejar input o bot
            keys_pressed = pygame.key.get_pressed()

            self.handle_player_input(
                self.players[0], keys_pressed
            )  # Jugador 1 siempre manual

            if config.machine_mode:
                self.bot_move(self.players[1])  # Jugador 2 como bot
            else:
                self.handle_player_input(
                    self.players[1], keys_pressed
                )  # Jugador 2 manual

            # GENERAR BASURA EN CADA FRAME (como en la versión antigua)
            self.trash_spawn_counter += 1
            if self.trash_spawn_counter >= self.trash_spawn_frequency:
                self.spawn_trash()
                self.trash_spawn_counter = 0

            # Mover basura
            self.move_trash()

            # Eliminar basura que sale de pantalla
            self.trash_list[:] = [
                t
                for t in self.trash_list
                if -self.TRASH_SIZE <= t["rect"].x <= SCREEN_WIDTH
            ]

            # Detectar colisiones
            self.check_collisions()

    def render(self, screen):
        # Dibujar fondo
        screen.blit(self.background_img, (0, 0))

        # Dibujar barcos antes que los jugadores y la basura
        screen.blit(self.BARCO1_IMAGE, self.BARCO1_POS)
        screen.blit(self.BARCO2_IMAGE, self.BARCO2_POS)

        # Dibujar jugadores (cebos)
        for player in self.players:
            screen.blit(player["image"], player["rect"])

        # Dibujar basura
        for trash in self.trash_list:
            screen.blit(trash["image"], trash["rect"])

        # Dibujar puntajes - USANDO NOMBRES DE PERSONAJES
        texto1 = self.font.render(
            f"{self.player1_name}: {self.players[0]['score']}", True, WHITE
        )
        screen.blit(texto1, (20, 10))

        # Puntaje jugador 2 (esquina derecha) - CORREGIDO
        texto2 = self.font.render(
            f"{self.player2_name}: {self.players[1]['score']}", True, WHITE
        )
        texto2_rect = texto2.get_rect(topright=(SCREEN_WIDTH - 20, 10))
        screen.blit(texto2, texto2_rect)

        # Cronómetro (centro superior, con fondo negro y borde blanco)
        elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000
        time_left = max(0, self.ROUND_TIME - elapsed_time)

        tiempo_rect = pygame.Rect(SCREEN_WIDTH // 2 - 40, 10, 80, 40)
        pygame.draw.rect(screen, BLACK, tiempo_rect)
        pygame.draw.rect(screen, WHITE, tiempo_rect, 2)
        tiempo_txt = self.font.render(str(int(time_left)), True, WHITE)
        txt_rect = tiempo_txt.get_rect(center=tiempo_rect.center)
        screen.blit(tiempo_txt, txt_rect)

        # Mostrar pantalla de fin de juego
        if self.game_state == "GAME_OVER":
            self.draw_end_game_overlay(screen)

        # Renderizar transición
        self.transition.render(screen)

    def draw_end_game_overlay(self, screen):
        """Dibujar overlay de fin de juego"""
        # Mensaje de ganador
        s1 = self.players[0]["score"]
        s2 = self.players[1]["score"]
        if s1 > s2:
            mensaje = f"¡Felicidades {self.player1_name}, ganaste!"
        elif s2 > s1:
            mensaje = f"¡Felicidades {self.player2_name}, ganaste!"
        else:
            mensaje = "¡Empate!"

        # Calcular tamaño dinámico del cuadro
        lines = [mensaje, f"{self.player1_name}: {s1}   {self.player2_name}: {s2}"]

        max_width = 0
        for line in lines:
            text_surf = self.font.render(line, True, WHITE)
            max_width = max(max_width, text_surf.get_width())

        # Cuadro dinámico
        box_width = max_width + 60
        box_height = 120
        cuadro = pygame.Rect(
            SCREEN_WIDTH // 2 - box_width // 2,
            SCREEN_HEIGHT // 2 - box_height // 2,
            box_width,
            box_height,
        )

        pygame.draw.rect(screen, BLACK, cuadro)
        pygame.draw.rect(screen, WHITE, cuadro, 4)

        # Mensaje principal
        mensaje_surf = self.font.render(mensaje, True, WHITE)
        mensaje_rect = mensaje_surf.get_rect(center=(cuadro.centerx, cuadro.y + 30))
        screen.blit(mensaje_surf, mensaje_rect)

        # Resumen de puntajes
        resumen = f"{self.player1_name}: {s1}   {self.player2_name}: {s2}"
        resumen_surf = self.font.render(resumen, True, WHITE)
        resumen_rect = resumen_surf.get_rect(center=(cuadro.centerx, cuadro.y + 70))
        screen.blit(resumen_surf, resumen_rect)

        # Mensaje de continuar en la parte inferior (independiente)
        continuar = "Presiona ENTER para continuar"
        continuar_surf = self.font_small.render(continuar, True, WHITE)
        continuar_rect = continuar_surf.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)
        )

        # Fondo para el mensaje inferior
        bg_rect = pygame.Rect(
            continuar_rect.x - 10,
            continuar_rect.y - 5,
            continuar_rect.width + 20,
            continuar_rect.height + 10,
        )
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))
        screen.blit(bg_surface, bg_rect)
        screen.blit(continuar_surf, continuar_rect)


print("Pesca Responsable - Nombres de personajes implementados")
