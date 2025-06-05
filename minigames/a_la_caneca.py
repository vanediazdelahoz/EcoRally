# minigames/a_la_caneca.py
import pygame
import random
from core.config import config
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

        # Obtener nombres de personajes
        character_names = ["Rosalba", "Tinú", "Sofia", "Luis"]
        self.player1_name = character_names[config.characters[0]]
        self.player2_name = (
            character_names[config.characters[1]]
            if not config.machine_mode
            else f"Bot {character_names[config.characters[1]]}"
        )

        # Cargar fondo
        try:
            self.fondo = pygame.image.load(
                "assets/CosasDeMinijuegos/FondoClasificar.png"
            ).convert()
            self.fondo = pygame.transform.scale(
                self.fondo, (SCREEN_WIDTH, SCREEN_HEIGHT)
            )
        except Exception as e:
            print(f"Error cargando fondo: {e}")
            self.fondo = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.fondo.fill((30, 30, 40))

        # Cargar canecas
        try:
            self.canecaB = pygame.transform.scale(
                pygame.image.load(
                    "assets/CosasDeMinijuegos/Canasta de basura/CanecaB.png"
                ).convert_alpha(),
                (100, 100),
            )
            self.canecaV = pygame.transform.scale(
                pygame.image.load(
                    "assets/CosasDeMinijuegos/Canasta de basura/CanecaV.png"
                ).convert_alpha(),
                (100, 100),
            )
            self.canecaN = pygame.transform.scale(
                pygame.image.load(
                    "assets/CosasDeMinijuegos/Canasta de basura/CanecaN.png"
                ).convert_alpha(),
                (100, 100),
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

        # === CONFIGURACIÓN DE POSICIONES DE CANECAS (AJUSTABLE) ===
        self.canecas_j1_x_offset = 94  # Posición X inicial para canecas J1 (ajustable)
        self.canecas_j1_spacing = 100  # Espaciado entre canecas J1 (ajustable)
        self.canecas_j1_y = 450  # Posición Y de canecas J1 (ajustable)

        self.canecas_j2_x_offset = 600  # Posición X inicial para canecas J2 (ajustable)
        self.canecas_j2_spacing = 100  # Espaciado entre canecas J2 (ajustable)
        self.canecas_j2_y = 450  # Posición Y de canecas J2 (ajustable)

        # Posiciones de canecas calculadas dinámicamente
        self.canecas_j1 = {
            "negra": (self.canecas_j1_x_offset, self.canecas_j1_y),
            "blanca": (
                self.canecas_j1_x_offset + self.canecas_j1_spacing,
                self.canecas_j1_y,
            ),
            "verde": (
                self.canecas_j1_x_offset + self.canecas_j1_spacing * 2,
                self.canecas_j1_y,
            ),
        }
        self.canecas_j2 = {
            "negra": (self.canecas_j2_x_offset, self.canecas_j2_y),
            "blanca": (
                self.canecas_j2_x_offset + self.canecas_j2_spacing,
                self.canecas_j2_y,
            ),
            "verde": (
                self.canecas_j2_x_offset + self.canecas_j2_spacing * 2,
                self.canecas_j2_y,
            ),
        }

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
                img = pygame.image.load(
                    f"assets/CosasDeMinijuegos/Basura/{n}"
                ).convert_alpha()
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
        self.player2_is_bot = config.machine_mode
        self.bot_interval = 1500
        self.bot_last_action_time = pygame.time.get_ticks()
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

    def simular_bot_jugador2(self):
        correcta = self.clasificacion[self.basura_j2]
        opciones = ["blanca", "negra", "verde"]
        eleccion = correcta if random.random() < 0.8 else random.choice(opciones)

        if eleccion == "blanca":
            self.puntaje2 += 1 if correcta == "blanca" else -1
        elif eleccion == "negra":
            self.puntaje2 += 1 if correcta == "negra" else -1
        elif eleccion == "verde":
            self.puntaje2 += 1 if correcta == "verde" else -1

        self.puntaje2 = max(0, self.puntaje2)
        self.nueva_basura(2)

    def handle_event(self, event):
        if not self.can_handle_input or self.transitioning or self.transition.active:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._start_transition(lambda: self.game.state_stack.pop())
            if self.game_state == "PLAYING":
                correcta_j1 = self.clasificacion[self.basura_j1]
                if event.key == pygame.K_w:
                    self.puntaje1 += 1 if correcta_j1 == "blanca" else -1
                    self.puntaje1 = max(0, self.puntaje1)
                    self.nueva_basura(1)
                elif event.key == pygame.K_a:
                    self.puntaje1 += 1 if correcta_j1 == "negra" else -1
                    self.puntaje1 = max(0, self.puntaje1)
                    self.nueva_basura(1)
                elif event.key == pygame.K_d:
                    self.puntaje1 += 1 if correcta_j1 == "verde" else -1
                    self.puntaje1 = max(0, self.puntaje1)
                    self.nueva_basura(1)
                elif not self.player2_is_bot:
                    correcta_j2 = self.clasificacion[self.basura_j2]
                    if event.key == pygame.K_UP:
                        self.puntaje2 += 1 if correcta_j2 == "blanca" else -1
                        self.puntaje2 = max(0, self.puntaje2)
                        self.nueva_basura(2)
                    elif event.key == pygame.K_LEFT:
                        self.puntaje2 += 1 if correcta_j2 == "negra" else -1
                        self.puntaje2 = max(0, self.puntaje2)
                        self.nueva_basura(2)
                    elif event.key == pygame.K_RIGHT:
                        self.puntaje2 += 1 if correcta_j2 == "verde" else -1
                        self.puntaje2 = max(0, self.puntaje2)
                        self.nueva_basura(2)
            elif self.game_state == "GAME_OVER" and event.key == pygame.K_RETURN:
                self._end_minigame()

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
                board_game.continue_after_minigame(self.puntaje1, self.puntaje2)

        # Salir del minijuego
        self._start_transition(lambda: self.game.state_stack.pop())

    def update(self, dt):
        self.transition.update(dt)

        if not self.transition.active and self.transitioning:
            self.transitioning = False
            self.can_handle_input = True

        # Actualizar tiempo
        if self.game_state == "PLAYING":
            tiempo_actual = (pygame.time.get_ticks() - self.inicio) / 1000
            tiempo_restante = max(0, self.tiempo_limite - tiempo_actual)

            # Lógica del bot
            if self.player2_is_bot:
                tiempo = pygame.time.get_ticks()
                if (
                    tiempo - self.bot_last_action_time
                    > self.bot_interval + random.randint(0, 10) * 100
                ):
                    self.simular_bot_jugador2()
                    self.bot_last_action_time = tiempo

            if tiempo_restante <= 0:
                self.game_state = "GAME_OVER"

    def render(self, screen):
        # Dibujar fondo
        screen.blit(self.fondo, (0, 0))

        # Tapar la línea negra con un color oscuro para disimularla
        pygame.draw.rect(
            screen, (30, 30, 40), (SCREEN_WIDTH // 2 - 1, 0, 3, SCREEN_HEIGHT)
        )

        # Dibujar canecas
        for tipo, pos in self.canecas_j1.items():
            if tipo == "negra":
                screen.blit(self.canecaN, pos)
                text_a = self.font_small.render(
                    "A", True, (255, 255, 255)
                )  # Letra blanca
                screen.blit(text_a, (pos[0] + 43, pos[1] + 50))
            elif tipo == "blanca":
                screen.blit(self.canecaB, pos)
                text_a = self.font_small.render("W", True, (0, 0, 0))  # Letra negra
                screen.blit(text_a, (pos[0] + 43, pos[1] + 50))
            elif tipo == "verde":
                screen.blit(self.canecaV, pos)
                text_a = self.font_small.render(
                    "D", True, (255, 255, 255)
                )  # Letra blanca
                screen.blit(text_a, (pos[0] + 43, pos[1] + 50))

        for tipo, pos in self.canecas_j2.items():
            if tipo == "negra":
                screen.blit(self.canecaN, pos)
                text_a = self.font_small.render(
                    "←", True, (255, 255, 255)
                )  # Letra blanca
                screen.blit(text_a, (pos[0] + 43, pos[1] + 50))
            elif tipo == "blanca":
                screen.blit(self.canecaB, pos)
                text_a = self.font_small.render("↑", True, (0, 0, 0))  # Letra negra
                screen.blit(text_a, (pos[0] + 43, pos[1] + 50))
            elif tipo == "verde":
                screen.blit(self.canecaV, pos)
                text_a = self.font_small.render(
                    "→", True, (255, 255, 255)
                )  # Letra blanca
                screen.blit(text_a, (pos[0] + 43, pos[1] + 50))

        # Dibujar basura actual
        screen.blit(self.imagenes[self.basura_j1], (SCREEN_WIDTH // 4 - 40, 200))
        screen.blit(self.imagenes[self.basura_j2], ((3 * SCREEN_WIDTH) // 4 - 40, 200))

        # Calcular tiempo restante
        if self.game_state == "PLAYING":
            tiempo_actual = (pygame.time.get_ticks() - self.inicio) / 1000
            tiempo_restante = max(0, self.tiempo_limite - tiempo_actual)
        else:
            tiempo_restante = 0

        # Dibujar puntajes y tiempo - USANDO NOMBRES DE PERSONAJES
        screen.blit(
            self.font.render(f"{self.player1_name}: {self.puntaje1}", True, WHITE),
            (30, 20),
        )
        # Posición corregida para jugador 2 (no tan a la derecha)
        p2_text = self.font.render(f"{self.player2_name}: {self.puntaje2}", True, WHITE)
        screen.blit(p2_text, (SCREEN_WIDTH - p2_text.get_width() - 30, 20))

        # Cronómetro centrado
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
            mensaje = f"¡Felicidades {self.player1_name}, ganaste!"
        elif self.puntaje2 > self.puntaje1:
            mensaje = f"¡Felicidades {self.player2_name}, ganaste!"
        else:
            mensaje = "¡Empate!"

        # Calcular tamaño dinámico del cuadro
        lines = [
            mensaje,
            f"{self.player1_name}: {self.puntaje1}   {self.player2_name}: {self.puntaje2}",
        ]

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
        marcador = f"{self.player1_name}: {self.puntaje1}   {self.player2_name}: {self.puntaje2}"
        marcador_surf = self.font_small.render(marcador, True, WHITE)
        marcador_rect = marcador_surf.get_rect(center=(cuadro.centerx, cuadro.y + 70))
        screen.blit(marcador_surf, marcador_rect)

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


print("A La Caneca - Posiciones de canecas configurables y nombres de personajes")
