import pygame
from core.config import config
from core.state import State
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, get_coordinate
from core.utils import load_font, get_character

class BoardGameView(State):
    def __init__(self, game):
        super().__init__(game)
        pygame.mouse.set_visible(False)

        self.font_title = load_font("assets/fonts/PublicPixel.ttf", 28)
        self.font_button = load_font("assets/fonts/mc-ten-lowercase-alt.ttf", 14)
        self.casillas = get_coordinate(SCREEN_WIDTH, SCREEN_HEIGHT)

        try:
            self.bg_image = pygame.image.load("assets/mapa/Mapa.png").convert_alpha()
            self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception as e:
            print("Error cargando el mapa:", e)
            self.bg_image = None

        self.players = []

        # Player 1
        self.players.append({
            "walk_frames": get_character(config.characters[0])[1:],
            "idle": get_character(config.characters[0])[0],
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
            "walk_frames": get_character(config.characters[1])[1:],
            "idle": get_character(config.characters[1])[0],
            "pos_idx": 1,
            "pos_actual": self.casillas[1],
            "anim_frame": 0,
            "moving": False,
            "move_from": None,
            "move_to": None,
            "move_step": 0,
            "move_steps_total": 0
        })

        self.velocidad = 1

    def interpolar(self, a, b, t):
        return int(a[0] + (b[0] - a[0]) * t), int(a[1] + (b[1] - a[1]) * t)

    def start_move(self, player_id, to_idx):
        player = self.players[player_id]
        if player["moving"]:
            return
        player["move_from"] = self.casillas[player["pos_idx"]]
        player["move_to"] = self.casillas[to_idx]
        distancia = ((player["move_to"][0] - player["move_from"][0]) ** 2 + (player["move_to"][1] - player["move_from"][1]) ** 2) ** 0.5
        player["move_steps_total"] = max(int(distancia // self.velocidad), 1)
        player["move_step"] = 0
        player["moving"] = True


    def update(self, dt):
        for player in self.players:
            if player["moving"]:
                t = player["move_step"] / player["move_steps_total"]
                player["pos_actual"] = self.interpolar(player["move_from"], player["move_to"], t)
                player["anim_frame"] = (player["anim_frame"] + 1) % (len(player["walk_frames"]) * 5)

                player["move_step"] += 1
                if player["move_step"] > player["move_steps_total"]:
                    player["pos_actual"] = player["move_to"]
                    player["pos_idx"] = self.casillas.index(player["move_to"])
                    player["moving"] = False
                    player["anim_frame"] = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.state_stack.pop()
            elif event.key == pygame.K_a:
                self.start_move(0, 1)  # jugador 1
            elif event.key == pygame.K_d:
                self.start_move(1, 2)  # jugador 2


    def render(self, screen):
        if self.bg_image:
            screen.blit(self.bg_image, (0, 0))

        for player in self.players:
            if player["moving"]:
                frame_index = player["anim_frame"] // 5
                frame_actual = player["walk_frames"][frame_index]

                # Detectar si se mueve a la izquierda
                if player["move_from"][0] > player["move_to"][0]:
                    frame_actual = pygame.transform.flip(frame_actual, True, False)

                screen.blit(frame_actual, frame_actual.get_rect(center=player["pos_actual"]))
            else:
                screen.blit(player["idle"], player["idle"].get_rect(center=player["pos_actual"]))


