import pygame
import random
from core.config import config
from core.state import State
from core.settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    ORIGINAL_WIDTH,
    ORIGINAL_HEIGHT,
    get_coordinate,
    GREEN,
    WHITE,
    LIGHT_GRAY,
)
from core.utils import load_font, get_character, load_image


class BoardGameView(State):
    def __init__(self, game):
        super().__init__(game)
        pygame.mouse.set_visible(False)

        self.font_title = load_font("assets/fonts/PublicPixel.ttf", 28)
        self.font_button = load_font("assets/fonts/mc-ten-lowercase-alt.ttf", 18)
        self.font_ascii = load_font("assets/fonts/mc-ten-lowercase-alt.ttf", 25)
        self.casillas = get_coordinate(SCREEN_WIDTH, SCREEN_HEIGHT)

        try:
            self.OpenR_image = load_image("assets/CosasDelMapa/ReciclajeAbierto/reciclajeAbierto.png", scale=0.4)
        except Exception as e:
            print("Error cargando el punto de reciclaje abierto:", e)
            self.OpenR_image = None
        
        try:
            self.CloseR_image = load_image("assets/CosasDelMapa/ReciclajeCerrado/ReciclajeCerrado.png", scale=0.6)
        except Exception as e:
            print("Error cargando el punto de reciclaje cerrado:", e)
            self.CloseR_image = None
        
        try:
            self.bg_image = pygame.image.load("assets/mapa/Mapa.png").convert_alpha()
            self.bg_image = pygame.transform.scale(
                self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT)
            )
        except Exception as e:
            print("Error cargando el mapa:", e)
            self.bg_image = None

        def resize_image(image, width_ratio, height_ratio):
            new_width = int(image.get_width() * width_ratio)
            new_height = int(image.get_height() * height_ratio)
            return pygame.transform.scale(image, (new_width, new_height))

        if config.characters[0] != 2:
            width_ratio = 2.5 * SCREEN_WIDTH / ORIGINAL_WIDTH
            height_ratio = 2.6 * SCREEN_HEIGHT / ORIGINAL_HEIGHT
        else:
            width_ratio = 2.1 * SCREEN_WIDTH / ORIGINAL_WIDTH
            height_ratio = 2.2 * SCREEN_HEIGHT / ORIGINAL_HEIGHT

        self.walk_frames_p1 = get_character(config.characters[0])
        self.walk_frames_p1 = [
            resize_image(img, width_ratio, height_ratio) for img in self.walk_frames_p1
        ]

        if config.characters[1] != 2:
            width_ratio = 2.5 * SCREEN_WIDTH / ORIGINAL_WIDTH
            height_ratio = 2.6 * SCREEN_HEIGHT / ORIGINAL_HEIGHT
        else:
            width_ratio = 2.1 * SCREEN_WIDTH / ORIGINAL_WIDTH
            height_ratio = 2.2 * SCREEN_HEIGHT / ORIGINAL_HEIGHT

        self.walk_frames_p2 = get_character(config.characters[1])
        self.walk_frames_p2 = [
            resize_image(img, width_ratio, height_ratio) for img in self.walk_frames_p2
        ]

        self.numero_ronda = 1
        self.fork_tiles = [16, 23, 32, 48]
        self.waiting_for_choice = [False, False]  # Uno por jugador
        self.direction_choice = [
            None,
            None,
        ]  # Almacena la dirección elegida temporalmente

        self.players = []

        # Player 1
        self.players.append(
            {
                "walk_frames": self.walk_frames_p1[1:],
                "idle": self.walk_frames_p1[0],
                "pos_idx": 0,
                "pos_actual": self.casillas[0],
                "anim_frame": 0,
                "moving": False,
                "move_from": None,
                "move_to": None,
                "move_step": 0,
                "move_steps_total": 0,
                "cantidad_de_basura": 0,
                "cantidad_de_medallas": 0,
            }
        )

        # Player 2
        self.players.append(
            {
                "walk_frames": self.walk_frames_p2[1:],
                "idle": self.walk_frames_p2[0],
                "pos_idx": 1,
                "pos_actual": self.casillas[1],
                "anim_frame": 0,
                "moving": False,
                "move_from": None,
                "move_to": None,
                "move_step": 0,
                "move_steps_total": 0,
                "cantidad_de_basura": 0,
                "cantidad_de_medallas": 0,
            }
        )

        self.dice_images = [
            pygame.transform.scale(
                pygame.image.load(f"assets/Dado/Dado{i}.png"), (100, 100)
            )
            for i in range(1, 7)
        ]

        # Variables para animar el dado
        self.turno = [0, 1, 2]  # Jugadores que están en turno
        self.dice_rolling = False
        self.dice_start_time = 0
        self.dice_duration = 1500  # ms, duración total de la animación
        self.dice_roll_interval = 100  # ms, tiempo entre frames del dado
        self.dice_last_update = 0
        self.current_dice_frame = 0
        self.final_dice_value = None
        self.dice_result_display_time = 1000  # ms
        self.dice_result_time = 0

        self.puntodereciclaje = {}

        #EJEMPLO DE PUNTOS DE RECICLAJE
        self.set_puntos_de_reciclaje([(2, True), (4, False), (13, True)])


    def set_puntos_de_reciclaje(self, lista_de_casas):
            self.puntodereciclaje = {idx: estado for idx, estado in lista_de_casas}

    def toggle_luces_en_casilla(self, idx):
        if idx in self.puntodereciclaje:
            self.puntodereciclaje[idx] = not self.puntodereciclaje[idx]

    def start_dice_roll(self):
        if not self.dice_rolling:
            self.dice_rolling = True
            self.dice_start_time = pygame.time.get_ticks()
            self.dice_last_update = self.dice_start_time
            self.final_dice_value = None
            self.current_dice_frame = 0

    def interpolar(self, a, b, t):
        return int(a[0] + (b[0] - a[0]) * t), int(a[1] + (b[1] - a[1]) * t)

    def start_move(self, player_id, to_idx):
        player = self.players[player_id]
        if player["moving"]:
            return

        if player["pos_idx"] in self.fork_tiles:
            self.waiting_for_choice[player_id] = True
            return

        player["move_from"] = self.casillas[player["pos_idx"]]
        player["move_to"] = self.casillas[to_idx]
        distancia = (
            (player["move_to"][0] - player["move_from"][0]) ** 2
            + (player["move_to"][1] - player["move_from"][1]) ** 2
        ) ** 0.5
        player["move_steps_total"] = max(int(distancia), 1)
        player["move_step"] = 0
        player["moving"] = True

    def update(self, dt):
        for player in self.players:
            if player["moving"]:
                t = player["move_step"] / player["move_steps_total"]
                player["pos_actual"] = self.interpolar(
                    player["move_from"], player["move_to"], t
                )
                player["anim_frame"] = (player["anim_frame"] + 1) % (
                    len(player["walk_frames"]) * 8
                )

                player["move_step"] += 1
                if player["move_step"] > player["move_steps_total"]:
                    player["pos_actual"] = player["move_to"]
                    player["pos_idx"] = self.casillas.index(player["move_to"])
                    player["moving"] = False
                    player["anim_frame"] = 0

        if self.dice_rolling:
            now = pygame.time.get_ticks()
            if now - self.dice_last_update > self.dice_roll_interval:
                self.current_dice_frame = (self.current_dice_frame + 1) % 6
                self.dice_last_update = now

            if now - self.dice_start_time > self.dice_duration:
                self.dice_rolling = False
                self.final_dice_value = random.randint(0, 5)
                self.dice_result_time = pygame.time.get_ticks()
                print(f"Resultado dado: {self.final_dice_value + 1}")

        if self.final_dice_value is not None:
            if (
                pygame.time.get_ticks() - self.dice_result_time
                > self.dice_result_display_time
            ):
                self.final_dice_value = None

    def handle_event(self, event):
        if self.waiting_for_choice[0]:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_a, pygame.K_d):
                direction = -1 if event.key == pygame.K_a else 1
                self.waiting_for_choice[0] = False
                self.start_move(0, self.players[0]["pos_idx"] + direction)
                return
        if self.waiting_for_choice[1]:
            if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_LEFT,
                pygame.K_RIGHT,
            ):
                direction = -1 if event.key == pygame.K_LEFT else 1
                self.waiting_for_choice[1] = False
                self.start_move(1, self.players[1]["pos_idx"] + direction)
                return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.quit()
            elif event.key == pygame.K_a:
                self.start_move(0, self.players[0]["pos_idx"] + 1)  # jugador 1
            elif event.key == pygame.K_d:
                self.start_move(1, self.players[1]["pos_idx"] + 1)  # jugador 2
            elif event.key == pygame.K_SPACE:
                if not self.dice_rolling:
                    self.start_dice_roll()

    def draw_ascii_info(self, screen):
        info_lines = []

        # Cabecera de ronda
        info_lines.append("---------")
        info_lines.append(f"  RONDA {self.numero_ronda}  ")
        info_lines.append("---------")

        # Dibujar líneas
        x, y = SCREEN_WIDTH - 160, 10  # esquina superior izquierda
        for i, line in enumerate(info_lines):
            text_surface = self.font_ascii.render(line, True, (255, 255, 255))
            screen.blit(
                text_surface, (x, y + i * 20)
            )  # 20 es el espaciado vertical entre líneas

    def render(self, screen):
        self.screen = screen
        if self.bg_image:
            screen.blit(self.bg_image, (0, 0))
        
        for idx, luces_encendidas in self.puntodereciclaje.items():
            pos = self.casillas[idx]  # Obtener coordenadas reales
            casa_img = self.OpenR_image if luces_encendidas else self.CloseR_image
            if casa_img:
                # Aplicar desplazamiento +10 en x y -10 en y
                offset_pos = (pos[0] + SCREEN_WIDTH/30, pos[1] - SCREEN_HEIGHT/12)
                screen.blit(casa_img, offset_pos)

        # Ordena los jugadores por su coordenada Y para dibujar al más arriba primero
        players_sorted = sorted(self.players, key=lambda p: p["pos_actual"][1])

        for player in players_sorted:
            if player["moving"]:
                frame_index = player["anim_frame"] // 8
                frame_actual = player["walk_frames"][frame_index]

                # Detectar si se mueve a la izquierda
                if player["move_from"][0] > player["move_to"][0]:
                    frame_actual = pygame.transform.flip(frame_actual, True, False)

                screen.blit(
                    frame_actual, frame_actual.get_rect(center=player["pos_actual"])
                )
            else:
                screen.blit(
                    player["idle"], player["idle"].get_rect(center=player["pos_actual"])
                )

        if self.dice_rolling:
            dice_img = self.dice_images[self.current_dice_frame]
            screen.blit(dice_img, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 50))
        elif self.final_dice_value is not None:
            dice_img = self.dice_images[self.final_dice_value]
            screen.blit(dice_img, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 50))

        if self.waiting_for_choice[0] or self.waiting_for_choice[1]:
            if self.waiting_for_choice[0]:
                message = "Presiona A (izquierda) o D (derecha)"
            else:
                message = "Flecha izq (izquierda) o Flecha der (derecha)"

            text_surface = self.font_button.render(message, True, WHITE)
            text_rect = text_surface.get_rect()
            text_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40)

            padding_x, padding_y = 12, 8
            bg_rect = pygame.Rect(
                text_rect.left - padding_x,
                text_rect.top - padding_y,
                text_rect.width + 2 * padding_x,
                text_rect.height + 2 * padding_y,
            )

            pygame.draw.rect(screen, LIGHT_GRAY, bg_rect, border_radius=10)
            pygame.draw.rect(
                screen, WHITE, bg_rect, 2, border_radius=10
            )  # borde blanco

            screen.blit(text_surface, text_rect)

        self.draw_ascii_info(screen)
