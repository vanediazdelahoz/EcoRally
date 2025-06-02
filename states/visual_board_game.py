import pygame
from core.config import config
from core.state import State
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, ORIGINAL_WIDTH, ORIGINAL_HEIGHT, get_coordinate, GREEN, WHITE, LIGHT_GRAY
from core.utils import load_font, get_character

class BoardGameView(State):
    def __init__(self, game):
        super().__init__(game)
        pygame.mouse.set_visible(False)

        self.font_title = load_font("assets/fonts/PublicPixel.ttf", 28)
        self.font_button = load_font("assets/fonts/mc-ten-lowercase-alt.ttf", 14)
        self.font_ascii = load_font("assets/fonts/mc-ten-lowercase-alt.ttf", 25)
        self.casillas = get_coordinate(SCREEN_WIDTH, SCREEN_HEIGHT)

        try:
            self.bg_image = pygame.image.load("assets/mapa/Mapa.png").convert_alpha()
            self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception as e:
            print("Error cargando el mapa:", e)
            self.bg_image = None

        def resize_image(image, width_ratio, height_ratio):
            new_width = int(image.get_width() * width_ratio)
            new_height = int(image.get_height() * height_ratio)
            return pygame.transform.scale(image, (new_width, new_height))
        
        if config.characters[0] != 2:
            width_ratio = 2.5*SCREEN_WIDTH / ORIGINAL_WIDTH
            height_ratio = 2.6*SCREEN_HEIGHT / ORIGINAL_HEIGHT
        else:
            width_ratio = 2.1*SCREEN_WIDTH / ORIGINAL_WIDTH
            height_ratio = 2.2*SCREEN_HEIGHT / ORIGINAL_HEIGHT

        self.walk_frames_p1 = get_character(config.characters[0])
        self.walk_frames_p1 = [resize_image(img, width_ratio, height_ratio) for img in self.walk_frames_p1]

        if config.characters[1] != 2:
            width_ratio = 2.5*SCREEN_WIDTH / ORIGINAL_WIDTH
            height_ratio = 2.6*SCREEN_HEIGHT / ORIGINAL_HEIGHT
        else:
            width_ratio = 2.1*SCREEN_WIDTH / ORIGINAL_WIDTH
            height_ratio = 2.2*SCREEN_HEIGHT / ORIGINAL_HEIGHT

        self.walk_frames_p2 = get_character(config.characters[1])
        self.walk_frames_p2 = [resize_image(img, width_ratio, height_ratio) for img in self.walk_frames_p2]

        self.numero_ronda = 1

        self.players = []

        # Player 1
        self.players.append({
            "walk_frames": self.walk_frames_p1[1:],
            "idle": self.walk_frames_p1[0],
            "pos_idx": 0,
            "pos_actual": self.casillas[0],
            "anim_frame": 0,
            "moving": False,
            "move_from": None,
            "move_to": None,
            "move_step": 0,
            "move_steps_total": 0
        })

        # Player 2
        self.players.append({
            "walk_frames": self.walk_frames_p2[1:],
            "idle": self.walk_frames_p2[0],
            "pos_idx": 1,
            "pos_actual": self.casillas[1],
            "anim_frame": 0,
            "moving": False,
            "move_from": None,
            "move_to": None,
            "move_step": 0,
            "move_steps_total": 0
        })


    def interpolar(self, a, b, t):
        return int(a[0] + (b[0] - a[0]) * t), int(a[1] + (b[1] - a[1]) * t)

    def start_move(self, player_id, to_idx):
        player = self.players[player_id]
        if player["moving"]:
            return
        player["move_from"] = self.casillas[player["pos_idx"]]
        player["move_to"] = self.casillas[to_idx]
        distancia = ((player["move_to"][0] - player["move_from"][0]) ** 2 + (player["move_to"][1] - player["move_from"][1]) ** 2) ** 0.5
        player["move_steps_total"] = max(int(distancia), 1)
        player["move_step"] = 0
        player["moving"] = True


    def update(self, dt):
        for player in self.players:
            if player["moving"]:
                t = player["move_step"] / player["move_steps_total"]
                player["pos_actual"] = self.interpolar(player["move_from"], player["move_to"], t)
                player["anim_frame"] = (player["anim_frame"] + 1) % (len(player["walk_frames"]) * 8)

                player["move_step"] += 1
                if player["move_step"] > player["move_steps_total"]:
                    player["pos_actual"] = player["move_to"]
                    player["pos_idx"] = self.casillas.index(player["move_to"])
                    player["moving"] = False
                    player["anim_frame"] = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.quit()
            elif event.key == pygame.K_a:
                self.start_move(0, self.players[0]["pos_idx"] + 1)  # jugador 1
            elif event.key == pygame.K_d:
                self.start_move(1, self.players[1]["pos_idx"] + 1)  # jugador 2

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
            screen.blit(text_surface, (x, y + i * 20))  # 20 es el espaciado vertical entre líneas



    def render(self, screen):
        if self.bg_image:
            screen.blit(self.bg_image, (0, 0))

        # Ordena los jugadores por su coordenada Y para dibujar al más arriba primero
        players_sorted = sorted(self.players, key=lambda p: p["pos_actual"][1])

        for player in players_sorted:
            if player["moving"]:
                frame_index = player["anim_frame"] // 8
                frame_actual = player["walk_frames"][frame_index]

                # Detectar si se mueve a la izquierda
                if player["move_from"][0] > player["move_to"][0]:
                    frame_actual = pygame.transform.flip(frame_actual, True, False)

                screen.blit(frame_actual, frame_actual.get_rect(center=player["pos_actual"]))
            else:
                screen.blit(player["idle"], player["idle"].get_rect(center=player["pos_actual"]))
        
        self.draw_ascii_info(screen)




