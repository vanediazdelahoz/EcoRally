# Vista principal del juego de tablero

import pygame
import random
import os

from core.config import config
from core.state import State
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, get_coordinate
from core.utils import load_font, get_character, load_image
from core.effects import TransitionEffect

# Importar lógica del juego
from states.board_game import create_board, setup_recycling_points
from states.player import Player

# Importar el agente DynaQ
from agent.dynaq_agent import DynaQAgent


class BoardGameView(State):
    def __init__(self, game):
        super().__init__(game)
        pygame.mouse.set_visible(False)
        self.bg_image = pygame.image.load("assets/images/map/map.png").convert_alpha()
        self.bg_image = pygame.transform.scale(
            self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.OpenR_image = load_image(
            "assets/images/map/recycling_point/open_recycling_point.png", scale=0.4)
        self.CloseR_image = load_image(
            "assets/images/map/recycling_point/closed_recycling_point.png", scale=0.6)

        self.transition = TransitionEffect(0.15)
        self.transition.start_fade_in()

        self.transitioning = False
        self.can_handle_input = True

        self.font_title = load_font("assets/fonts/PublicPixel.ttf", 24)
        self.font_message = load_font("assets/fonts/PublicPixel.ttf", 16)
        self.font_small = load_font("assets/fonts/PublicPixel.ttf", 12)
        self.font_turn = load_font("assets/fonts/PublicPixel.ttf", 18)

        self.rounds = 10
        self.current_round = 1
        self.total_recycling_points = 3
        self.recycle_timeout = 2
        self.initial_trash = 10

        self.turns_played_this_round = (0)
        self.round_starting_player = None
        self.first_player_of_game = None

        self.casillas = get_coordinate(SCREEN_WIDTH, SCREEN_HEIGHT)

        self.squares = create_board()
        self.recycling_points = setup_recycling_points(
            self.squares, self.total_recycling_points, silent_mode=True)

        character_names = ["Rosalba", "Tinú", "Sofia", "Luis"]
        self.player1_name = character_names[config.characters[0]]
        self.player2_name = (
            character_names[config.characters[1]]
            if not config.machine_mode
            else f"Bot {character_names[config.characters[1]]}")

        self.player1 = Player(self.player1_name)
        self.player2 = Player(self.player2_name)
        self.player1.trash = self.initial_trash
        self.player2.trash = self.initial_trash

        self.player1.move_to(self.squares[0])
        self.player2.move_to(self.squares[0])

        self.round_start_stats = {
            "player1": {"trash": self.initial_trash, "badges": 0},
            "player2": {"trash": self.initial_trash, "badges": 0},
        }

        self.load_character_images()

        self.load_dice_images()

        self.game_state = "INITIAL_ROLL"
        self.current_player = None
        self.dice_result = None
        self.moves_remaining = 0

        self.center_message = "¡Bienvenidos a EcoRally!"
        self.bottom_message = ""
        self.turn_message = ""
        self.dice_total_message = ""
        self.message_timer = 0
        self.waiting_for_enter = True

        self.choice_options = []

        self.dice_rolling = False
        self.dice_start_time = 0
        self.dice_roll_interval = 100
        self.dice_last_update = 0

        self.dice1_rolling = False
        self.dice2_rolling = False
        self.dice1_value = None
        self.dice2_value = None
        self.current_dice1_frame = 0
        self.current_dice2_frame = 0
        self.dice_result_display_time = 2000
        self.dice_result_time = 0

        self.purple_dice_rolling = False
        self.purple_dice_value = None
        self.current_purple_dice_frame = 0

        self.initial_dice_rolling = False
        self.initial_dice_phase = 1
        self.initial_dice1_rolling = False
        self.initial_dice2_rolling = False
        self.initial_dice1_value = None
        self.initial_dice2_value = None
        self.current_initial_dice1_frame = 0
        self.current_initial_dice2_frame = 0
        self.initial_dice_attempts = 0

        self.player1_data = {
            "pos_idx": 0,
            "pos_actual": list(self.casillas[0]),
            "anim_frame": 0,
            "moving": False,
            "move_from": None,
            "move_to": None,
            "move_step": 0,
            "move_steps_total": 0,
            "target_idx": 0,}

        self.player2_data = {
            "pos_idx": 0,
            "pos_actual": list(self.casillas[0]),
            "anim_frame": 0,
            "moving": False,
            "move_from": None,
            "move_to": None,
            "move_step": 0,
            "move_steps_total": 0,
            "target_idx": 0,}

        self.available_minigames = [
            "to_the_bin",
            "sky_crisis",
            "responsible_fishing",]
        self.selected_minigame = None
        self.last_minigame = None

        self.is_bot_mode = config.machine_mode
        self.agent = None

        if self.is_bot_mode:
            self.load_agent()

        self.bot_timer = 0
        self.bot_action_delay = 0
        self.bot_thinking = False
        self.bot_next_action = None

        self.bot_second_dice_timer = 0
        self.bot_second_dice_delay = 0
        
        self.minigame_rules_shown = False
        self.minigame_countdown = 0
        self.minigame_countdown_timer = 0
        
        self.start_initial_dice_roll()

    def load_agent(self):
        model_path = "agent/agent_policy.pkl"
        self.agent = DynaQAgent(train_mode=False)

        os.path.exists(model_path)
        self.agent.load_policy(model_path)

    def load_character_images(self):
        try:
            character_paths = get_character(4)

            char1_path = character_paths[config.characters[0]]
            self.player1_frames = get_character(config.characters[0])

            scale_factor = 0.8
            self.player1_frames = [
                pygame.transform.scale(
                    frame,
                    (
                        int(frame.get_width() * scale_factor),
                        int(frame.get_height() * scale_factor),),)
                for frame in self.player1_frames]

            char2_path = character_paths[config.characters[1]]
            self.player2_frames = get_character(config.characters[1])

            self.player2_frames = [
                pygame.transform.scale(
                    frame,
                    (
                        int(frame.get_width() * scale_factor),
                        int(frame.get_height() * scale_factor),),)
                for frame in self.player2_frames]

        except Exception as e:
            self.player1_frames = [pygame.Surface((40, 60)) for _ in range(4)]
            for frame in self.player1_frames:
                frame.fill((0, 255, 0))

            self.player2_frames = [pygame.Surface((40, 60)) for _ in range(4)]
            for frame in self.player2_frames:
                frame.fill((255, 0, 0))

    def load_dice_images(self):
        try:
            self.dice_images = []
            for i in range(1, 7):
                img = pygame.image.load(f"assets/images/map/dice/dice{i}.png").convert_alpha()
                img = pygame.transform.scale(img, (80, 80))
                self.dice_images.append(img)
        except Exception as e:
            self.dice_images = []
            for i in range(6):
                surf = pygame.Surface((80, 80))
                surf.fill(WHITE)
                pygame.draw.rect(surf, (0, 0, 0), surf.get_rect(), 2)
                font = load_font("assets/fonts/PublicPixel.ttf", 32)
                text = font.render(str(i + 1), True, (0, 0, 0))
                text_rect = text.get_rect(center=surf.get_rect().center)
                surf.blit(text, text_rect)
                self.dice_images.append(surf)

    def start_initial_dice_roll(self):
        self.player1.move_to(self.squares[0])
        self.player2.move_to(self.squares[0])
        self.player1_data["pos_idx"] = 0
        self.player1_data["pos_actual"] = list(self.casillas[0])
        self.player2_data["pos_idx"] = 0
        self.player2_data["pos_actual"] = list(self.casillas[0])

        self.initial_dice_rolling = True
        self.initial_dice_phase = 1
        self.initial_dice1_rolling = True
        self.initial_dice2_rolling = False
        self.initial_dice1_value = None
        self.initial_dice2_value = None
        self.current_initial_dice1_frame = 0
        self.current_initial_dice2_frame = 0
        self.dice_start_time = pygame.time.get_ticks()
        self.dice_last_update = self.dice_start_time
        self.game_state = "INITIAL_ROLL"

        self.center_message = f"Tiro inicial para determinar quién empieza"
        self.bottom_message = f"{self.player1_name}, presiona ENTER para tirar tu dado"
        self.waiting_for_enter = False
        self.message_timer = pygame.time.get_ticks()

    def stop_initial_dice(self, player):
        if self.initial_dice_phase == 1 and player == 1 and self.initial_dice1_rolling:
            self.initial_dice1_rolling = False
            self.initial_dice1_value = random.randint(1, 6)
            self.initial_dice_phase = 2

            self.initial_dice2_rolling = True
            self.center_message = f"Tiro inicial para determinar quién empieza"

            if self.is_bot_mode:
                self.bottom_message = f"{self.player2_name} está tirando su dado..."
                self.schedule_bot_action("stop_initial_dice", random.randint(800, 1500))
            else:
                self.bottom_message = (
                    f"{self.player2_name}, presiona ENTER para tirar tu dado")

        elif (
            self.initial_dice_phase == 2 and player == 2 and self.initial_dice2_rolling):
            self.initial_dice2_rolling = False
            self.initial_dice2_value = random.randint(1, 6)
            self.initial_dice_phase = 3
            self.initial_dice_rolling = False
            self.initial_dice_attempts += 1

        if self.initial_dice_phase == 3:
            self.center_message = f"Tiro inicial #{self.initial_dice_attempts}\n{self.player1_name}: {self.initial_dice1_value} | {self.player2_name}: {self.initial_dice2_value}\n\n"

            if self.initial_dice1_value > self.initial_dice2_value:
                self.current_player = 1
                self.first_player_of_game = 1
                self.round_starting_player = 1
                self.center_message += f"{self.player1_name} comienza"
                self.turn_message = f"Turno: {self.player1_name}"
                self.waiting_for_enter = True
                self.bottom_message = "Presiona ENTER para continuar"
            elif self.initial_dice2_value > self.initial_dice1_value:
                self.current_player = 2
                self.first_player_of_game = 2
                self.round_starting_player = 2
                self.center_message += f"{self.player2_name} comienza"
                self.turn_message = f"Turno: {self.player2_name}"
                self.waiting_for_enter = True
                self.bottom_message = "Presiona ENTER para continuar"
                if self.is_bot_mode:
                    self.schedule_bot_action(
                        "continue_after_message", random.randint(1000, 2000))
            else:
                self.center_message += "Empate. Volviendo a tirar..."
                self.waiting_for_enter = True
                self.bottom_message = "Presiona ENTER para continuar"

            self.message_timer = pygame.time.get_ticks()

    def start_new_round_tracking(self):
        self.round_start_stats = {
            "player1": {"trash": self.player1.trash, "badges": self.player1.badges},
            "player2": {"trash": self.player2.trash, "badges": self.player2.badges},}
        self.turns_played_this_round = 0

    def start_turn(self):
        current_player_obj = self.player1 if self.current_player == 1 else self.player2
        self.center_message = f"Turno de {current_player_obj.character}"
        self.turn_message = f"Turno: {current_player_obj.character}"
        self.waiting_for_enter = True
        self.bottom_message = "Presiona ENTER para continuar"
        self.game_state = "TURN_START"
        self.message_timer = pygame.time.get_ticks()

        self.turns_played_this_round += 1

        if self.is_bot_mode and self.current_player == 2:
            self.schedule_bot_action(
                "continue_after_message", random.randint(800, 1500))

    def start_dice_roll(self):
        if not self.dice_rolling:
            self.dice_rolling = True
            self.dice1_rolling = True
            self.dice2_rolling = False
            self.dice1_value = None
            self.dice2_value = None
            self.dice_start_time = pygame.time.get_ticks()
            self.dice_last_update = self.dice_start_time
            self.current_dice1_frame = 0
            self.current_dice2_frame = 0
            self.game_state = "DICE_ROLL"

            current_player_obj = (
                self.player1 if self.current_player == 1 else self.player2)
            self.turn_message = f"Turno: {current_player_obj.character}"

            if self.is_bot_mode and self.current_player == 2:
                self.bottom_message = f"{self.player2_name} está tirando los dados..."
                self.schedule_bot_action("stop_first_dice", random.randint(800, 1500))
            else:
                self.bottom_message = "Presiona ENTER para detener el primer dado"

            self.center_message = ""
            self.waiting_for_enter = False
            self.message_timer = pygame.time.get_ticks()

    def start_purple_dice_roll(self):
        self.purple_dice_rolling = True
        self.purple_dice_value = None
        self.current_purple_dice_frame = 0
        self.dice_start_time = pygame.time.get_ticks()
        self.dice_last_update = self.dice_start_time
        self.game_state = "PURPLE_DICE"

        current_player_obj = self.player1 if self.current_player == 1 else self.player2
        self.center_message = f"¡Casilla morada!\n{current_player_obj.character} puede tirar un dado para doble basura"

        if self.is_bot_mode and self.current_player == 2:
            self.bottom_message = f"{self.player2_name} está tirando el dado..."
            self.schedule_bot_action("stop_purple_dice", random.randint(800, 1500))
        else:
            self.bottom_message = "Presiona ENTER para tirar"

        self.waiting_for_enter = False
        self.message_timer = pygame.time.get_ticks()

    def stop_purple_dice(self):
        if self.purple_dice_rolling:
            self.purple_dice_rolling = False
            self.purple_dice_value = random.randint(1, 6)
            bonus_trash = self.purple_dice_value * 2

            current_player_obj = (
                self.player1 if self.current_player == 1 else self.player2)
            current_player_obj.collect_trash(bonus_trash)

            self.center_message = f"¡Casilla morada!\n{current_player_obj.character} ganó {bonus_trash} de basura\n(Dado: {self.purple_dice_value}) x 2"
            self.waiting_for_enter = True
            self.bottom_message = "Presiona ENTER para continuar"
            self.game_state = "PURPLE_DICE_RESULT"
            self.message_timer = pygame.time.get_ticks()

            if self.is_bot_mode and self.current_player == 2:
                self.schedule_bot_action(
                    "continue_after_message", random.randint(1000, 2000))

    def stop_first_dice(self):
        if self.dice1_rolling:
            self.dice1_rolling = False
            self.dice1_value = random.randint(1, 6)
            self.dice2_rolling = True

            current_player_obj = (
                self.player1 if self.current_player == 1 else self.player2)
            self.turn_message = f"Turno: {current_player_obj.character}"

            if self.is_bot_mode and self.current_player == 2:
                self.bottom_message = (
                    f"{self.player2_name} está tirando el segundo dado...")
                self.bot_second_dice_timer = pygame.time.get_ticks()
                self.bot_second_dice_delay = random.randint(500, 1000)
            else:
                self.bottom_message = "Presiona ENTER para detener el segundo dado"

            self.message_timer = pygame.time.get_ticks()

    def stop_second_dice(self):
        if self.dice2_rolling:
            self.dice2_rolling = False
            self.dice_rolling = False
            self.dice2_value = random.randint(1, 6)
            self.dice_result = self.dice1_value + self.dice2_value
            self.dice_result_time = pygame.time.get_ticks()

            current_player_obj = (
                self.player1 if self.current_player == 1 else self.player2)
            self.turn_message = f"Turno: {current_player_obj.character}"
            self.dice_total_message = (
                f"{self.dice1_value} + {self.dice2_value} = {self.dice_result}")
            self.bottom_message = "Presiona ENTER para empezar movimiento"
            self.waiting_for_enter = True
            self.message_timer = pygame.time.get_ticks()

            self.moves_remaining = self.dice_result
            self.game_state = "DICE_SHOWING_RESULT"

            self.bot_second_dice_timer = 0

            if self.is_bot_mode and self.current_player == 2:
                self.schedule_bot_action(
                    "continue_after_message", random.randint(1000, 2000))

    def update_dice_animation(self, dt):
        now = pygame.time.get_ticks()

        if now - self.dice_last_update > self.dice_roll_interval:
            if self.dice1_rolling:
                self.current_dice1_frame = (self.current_dice1_frame + 1) % 6
            if self.dice2_rolling:
                self.current_dice2_frame = (self.current_dice2_frame + 1) % 6

            if self.initial_dice1_rolling:
                self.current_initial_dice1_frame = (
                    self.current_initial_dice1_frame + 1) % 6
            if self.initial_dice2_rolling:
                self.current_initial_dice2_frame = (
                    self.current_initial_dice2_frame + 1) % 6

            if self.purple_dice_rolling:
                self.current_purple_dice_frame = (
                    self.current_purple_dice_frame + 1) % 6

            self.dice_last_update = now

    def interpolar(self, a, b, t):
        return int(a[0] + (b[0] - a[0]) * t), int(a[1] + (b[1] - a[1]) * t)

    def start_move_to_next_casilla(self, player_id):
        player_data = self.player1_data if player_id == 1 else self.player2_data
        current_player_obj = self.player1 if player_id == 1 else self.player2

        if player_data["moving"]:
            return False

        if not current_player_obj.position.next_squares:
            return False

        next_square = current_player_obj.position.next_squares[0]
        next_idx = next_square.id

        player_data["move_from"] = list(player_data["pos_actual"])
        player_data["move_to"] = list(self.casillas[next_idx])
        player_data["target_idx"] = next_idx

        distancia = (
            (player_data["move_to"][0] - player_data["move_from"][0]) ** 2
            + (player_data["move_to"][1] - player_data["move_from"][1]) ** 2) ** 0.5
        player_data["move_steps_total"] = max(int(distancia / 1), 20)
        player_data["move_step"] = 0
        player_data["moving"] = True

        return True

    def update_player_movement(self, dt):
        for player_id, player_data in enumerate(
            [self.player1_data, self.player2_data], 1):
            if player_data["moving"]:
                t = player_data["move_step"] / player_data["move_steps_total"]

                player_data["pos_actual"] = list(
                    self.interpolar(player_data["move_from"], player_data["move_to"], t))

                player_data["anim_frame"] = (player_data["anim_frame"] + 1) % (
                    len(self.player1_frames if player_id == 1 else self.player2_frames)* 8)

                player_data["move_step"] += 1

                if player_data["move_step"] > player_data["move_steps_total"]:
                    player_data["pos_actual"] = list(player_data["move_to"])
                    player_data["pos_idx"] = player_data["target_idx"]
                    player_data["moving"] = False

                    current_player_obj = (
                        self.player1 if player_id == 1 else self.player2)
                    current_player_obj.move_to(self.squares[player_data["pos_idx"]])
                    
                    self.moves_remaining -= 1
                    current_square = current_player_obj.position

                    if current_square.recycle:
                        self.process_recycling_point_on_pass(
                            current_player_obj, current_square)
                        return

                    if self.moves_remaining > 0:
                        if len(current_player_obj.position.next_squares) > 1:
                            self.choice_options = []
                            for i, square in enumerate(
                                current_player_obj.position.next_squares):
                                self.choice_options.append((i, square.id))

                            self.center_message = f"Selecciona el camino:\nPasos restantes: {self.moves_remaining}"

                            current_pos = current_player_obj.position.id
                            if current_pos == 23:
                                self.bottom_message = "← Camino izquierdo | Camino derecho →"
                            elif current_pos == 32:
                                self.bottom_message = "← Camino izquierdo | Camino derecho →"
                            elif current_pos == 48:
                                self.bottom_message = "← Camino izquierdo | Camino derecho →"
                            else:
                                self.bottom_message = "← Camino izquierdo | Camino derecho →"

                            if self.is_bot_mode and player_id == 2:
                                self.bottom_message = (
                                    f"{self.player2_name} está decidiendo...")
                                self.schedule_bot_action(
                                    "bot_make_choice", random.randint(800, 1500))

                            self.waiting_for_enter = False
                            self.game_state = "CHOICE"
                            self.message_timer = pygame.time.get_ticks()
                        else:
                            if self.is_bot_mode and player_id == 2:
                                self.schedule_bot_action(
                                    "move_current_player", random.randint(300, 600))
                            else:
                                pygame.time.set_timer(
                                    pygame.USEREVENT + 1, 400)
                    else:
                        self.apply_square_effect(current_player_obj)
                        player_data["anim_frame"] = 0

    def process_recycling_point_on_pass(self, player, square):
        old_badges = player.badges
        old_trash = player.trash
        player.try_recycle(self.recycle_timeout, silent_mode=True)
        new_badges = player.badges

        if new_badges > old_badges:
            self.center_message = f"{player.character} obtuvo una nueva insignia!\nInsignias: {old_badges} -> {new_badges}"
        elif square.timeout > 0:
            self.center_message = f"Punto de reciclaje ocupado!\nSe libera en {square.timeout} rondas"
        elif player.trash < 20:
            self.center_message = f"{player.character} no tiene suficiente basura!\nNecesita 20 de basura para reciclar\nBasura actual: {player.trash}"
        else:
            self.center_message = f"{player.character} puede reciclar aqui!\nTiene {player.trash} de basura"

        self.waiting_for_enter = True
        self.bottom_message = "Presiona ENTER para continuar"
        self.game_state = "RECYCLING_POINT_PASS"
        self.message_timer = pygame.time.get_ticks()

    def move_current_player(self):
        if self.moves_remaining <= 0:
            return

        current_player_obj = self.player1 if self.current_player == 1 else self.player2

        if len(current_player_obj.position.next_squares) > 1:
            self.choice_options = []
            for i, square in enumerate(current_player_obj.position.next_squares):
                self.choice_options.append((i, square.id))

            self.center_message = (
                f"Selecciona el camino:\nPasos restantes: {self.moves_remaining}")

            current_pos = current_player_obj.position.id
            if current_pos == 23:
                self.bottom_message = "← Camino izquierdo | Camino derecho →"
            elif current_pos == 32:
                self.bottom_message = "← Camino izquierdo | Camino derecho →"
            elif current_pos == 48:
                self.bottom_message = "← Camino izquierdo | Camino derecho →"
            else:
                self.bottom_message = "← Camino izquierdo | Camino derecho →"

            if self.is_bot_mode and self.current_player == 2:
                self.bottom_message = f"{self.player2_name} está decidiendo..."
                self.schedule_bot_action("bot_make_choice", random.randint(800, 1500))

            self.waiting_for_enter = False
            self.game_state = "CHOICE"
            self.message_timer = pygame.time.get_ticks()
            return

        if self.start_move_to_next_casilla(self.current_player):
            self.center_message = ""
            self.dice_total_message = ""
            self.game_state = "MOVING"
            if self.moves_remaining > 0:
                self.bottom_message = (
                    f"Moviendo... Pasos restantes: {self.moves_remaining}")

    def make_choice(self, choice_index):
        if choice_index < len(self.choice_options):
            current_player_obj = (
                self.player1 if self.current_player == 1 else self.player2)
        
        current_pos = current_player_obj.position.id
        if current_pos == 23:
            if choice_index == 0:
                chosen_square = self.squares[27]
            else:
                chosen_square = self.squares[24]
        elif current_pos == 32:
            if choice_index == 0:
                chosen_square = self.squares[34]
            else:
                chosen_square = self.squares[33]
        elif current_pos == 48:
            if choice_index == 0:
                chosen_square = self.squares[53]
            else:
                chosen_square = self.squares[49]
        else:
            chosen_square = current_player_obj.position.next_squares[choice_index]

        current_player_obj.move_to(chosen_square)

        player_data = (
            self.player1_data if self.current_player == 1 else self.player2_data)
        player_data["pos_idx"] = chosen_square.id
        player_data["pos_actual"] = list(self.casillas[chosen_square.id])

        if chosen_square.recycle:
            self.process_recycling_point_on_pass(current_player_obj, chosen_square)
            return

        self.moves_remaining -= 1
        self.game_state = "MOVING"

        self.center_message = ""

        if self.moves_remaining <= 0:
            self.apply_square_effect(current_player_obj)
        else:
            if self.is_bot_mode and self.current_player == 2:
                self.schedule_bot_action("move_current_player", random.randint(300, 600))
            else:
                pygame.time.set_timer(pygame.USEREVENT + 1, 400)

    def bot_make_choice(self):
        if self.game_state != "CHOICE" or self.current_player != 2:
            return

        current_player_obj = self.player2

        if self.agent:
            state = self.agent.encode_state(
                current_player_obj.position,
                self.rounds - self.current_round + 1,
                current_player_obj.trash,
                self.recycling_points,
                current_player_obj.badges,
                self.player1.badges,)

            possible_actions = list(
                range(len(current_player_obj.position.next_squares)))

            action = self.agent.get_action(state, possible_actions)

            current_pos = current_player_obj.position.id
            if current_pos == 23:
                next_square_id = 27 if action == 0 else 24
            elif current_pos == 32:
                next_square_id = 34 if action == 0 else 33
            elif current_pos == 48:
                next_square_id = 53 if action == 0 else 49
            else:
                next_square_id = current_player_obj.position.next_squares[action].id
                
            self.bottom_message = (
                f"{self.player2_name} elige el camino hacia la casilla {next_square_id}")
            self.make_choice(action)
        else:
            action = random.choice(range(len(current_player_obj.position.next_squares)))
            self.make_choice(action)

    def apply_square_effect(self, player):
        square = player.position

        if square.recycle:
            self.process_recycling_point_on_pass(player, square)
            return

        old_trash = player.trash
        square.effect(player, silent_mode=True)
        new_trash = player.trash

        if square.type == "blue":
            self.center_message = f"¡{player.character} cayó en una casilla azul!\n\nCasilla neutral, no pasa nada especial."
        elif square.type == "green":
            trash_gained = new_trash - old_trash
            self.center_message = f"¡{player.character} cayó en una casilla verde!\n\nGana {trash_gained} de basura"
        elif square.type == "red":
            trash_lost = old_trash - new_trash
            self.center_message = f"¡Oh no! {player.character} cayó en una casilla roja!\n\nPierde {trash_lost} de basura"
        elif square.type == "purple":
            self.start_purple_dice_roll()
            return

        self.waiting_for_enter = True
        self.bottom_message = "Presiona ENTER para continuar"
        self.game_state = "SQUARE_EFFECT"
        self.message_timer = pygame.time.get_ticks()

        if self.is_bot_mode and self.current_player == 2:
            self.schedule_bot_action(
                "continue_after_message", random.randint(1000, 2000))

    def end_turn(self):
        if self.turns_played_this_round >= 2:
            if self.current_round < self.rounds:
                self.start_minigame()
            else:
                points_to_reactivate = []
                for point in self.recycling_points:
                    if point.timeout > 0:
                        point.timeout -= 1
                        if point.timeout == 0:
                            points_to_reactivate.append(point.id)

                self.points_to_reactivate = points_to_reactivate
                self.current_round += 1
                self.end_game()
        else:
            self.current_player = 2 if self.current_player == 1 else 1
            self.start_turn()

    def start_minigame(self):
        available_games = [
            game for game in self.available_minigames if game != self.last_minigame]

        self.selected_minigame = random.choice(available_games)
        self.last_minigame = self.selected_minigame

        minigame_names = {
            "to_the_bin": "A La Caneca",
            "sky_crisis": "Cielo En Crisis",
            "responsible_fishing": "Pesca Responsable",}

        self.center_message = f"¡Minijuego: {minigame_names[self.selected_minigame]}!"
        self.bottom_message = "Presiona ENTER para continuar"
        self.waiting_for_enter = True
        self.message_timer = pygame.time.get_ticks()
        self.game_state = "MINIGAME"

    def launch_minigame(self):
        if self.selected_minigame == "to_the_bin":
            from minigames.to_the_bin import ALaCanecaState
            self.game.state_stack.append(ALaCanecaState(self.game))
        elif self.selected_minigame == "sky_crisis":
            from minigames.sky_crisis import CieloEnCrisisState
            self.game.state_stack.append(CieloEnCrisisState(self.game))
        elif self.selected_minigame == "responsible_fishing":
            from minigames.responsible_fishing import PescaResponsableState
            self.game.state_stack.append(PescaResponsableState(self.game))

        self.center_message = ""
        self.bottom_message = ""
        self.dice_total_message = ""

    def continue_after_minigame(self, player1_score, player2_score):
        if player1_score > player2_score:
            self.player1.collect_trash(10)
            self.player2.collect_trash(3)
        elif player2_score > player1_score:
            self.player1.collect_trash(3)
            self.player2.collect_trash(10)
        else:
            self.player1.collect_trash(10)
            self.player2.collect_trash(10)

        p1_trash_change = (self.player1.trash - self.round_start_stats["player1"]["trash"])
        p1_badges_change = (self.player1.badges - self.round_start_stats["player1"]["badges"])
        p2_trash_change = (self.player2.trash - self.round_start_stats["player2"]["trash"])
        p2_badges_change = (self.player2.badges - self.round_start_stats["player2"]["badges"])

        if self.player1.badges > self.player2.badges:
            first_place = f"{self.player1_name} (1°)"
            second_place = f"{self.player2_name} (2°)"
        elif self.player2.badges > self.player1.badges:
            first_place = f"{self.player2_name} (1°)"
            second_place = f"{self.player1_name} (2°)"
        else:
            if self.player1.trash > self.player2.trash:
                first_place = f"{self.player1_name} (1°)"
                second_place = f"{self.player2_name} (2°)"
            elif self.player2.trash > self.player1.trash:
                first_place = f"{self.player2_name} (1°)"
                second_place = f"{self.player1_name} (2°)"
            else:
                first_place = f"{self.player1_name} (Empate)"
                second_place = f"{self.player2_name} (Empate)"

        summary_lines = [f"¡Fin de la ronda {self.current_round}!", ""]

        p1_changes = []
        if p1_badges_change != 0:
            p1_changes.append(f"Insignias: {'+' if p1_badges_change > 0 else ''}{p1_badges_change}")
        if p1_trash_change != 0:
            p1_changes.append(f"Basura: {'+' if p1_trash_change > 0 else ''}{p1_trash_change}")

        if p1_changes:
            summary_lines.append(f"{self.player1_name}: {' | '.join(p1_changes)}")
        else:
            summary_lines.append(f"{self.player1_name}: Sin cambios")

        p2_changes = []
        if p2_badges_change != 0:
            p2_changes.append(
                f"Insignias: {'+' if p2_badges_change > 0 else ''}{p2_badges_change}")
        if p2_trash_change != 0:
            p2_changes.append(
                f"Basura: {'+' if p2_trash_change > 0 else ''}{p2_trash_change}")

        if p2_changes:
            summary_lines.append(f"{self.player2_name}: {' | '.join(p2_changes)}")
        else:
            summary_lines.append(f"{self.player2_name}: Sin cambios")

        summary_lines.extend(["", "Ranking actual:", first_place, second_place])

        self.center_message = "\n".join(summary_lines)
        self.bottom_message = "Presiona ENTER para continuar"
        self.waiting_for_enter = True
        self.game_state = "ROUND_SUMMARY"
        self.message_timer = pygame.time.get_ticks()

    def start_new_round_after_summary(self):
        points_to_reactivate = []
        for point in self.recycling_points:
            if point.timeout > 0:
                point.timeout -= 1
                if point.timeout == 0:
                    points_to_reactivate.append(point.id)

        self.points_to_reactivate = points_to_reactivate
        self.current_round += 1

        if self.current_round > self.rounds:
            self.end_game()
            return

        self.center_message = f"Ronda {self.current_round}"
        self.bottom_message = "Presiona ENTER para continuar"
        self.waiting_for_enter = True
        self.dice_total_message = ""
        self.game_state = "NEW_ROUND"
        self.message_timer = pygame.time.get_ticks()

    def show_recycling_status(self):
        active_points = [point for point in self.recycling_points if point.timeout == 0]
        inactive_points = [point for point in self.recycling_points if point.timeout > 0]

        if hasattr(self, "points_to_reactivate") and self.points_to_reactivate:
            points_count = len(self.points_to_reactivate)
            self.center_message = f"{points_count} punto{'s' if points_count > 1 else ''} de reciclaje reactivado{'s' if points_count > 1 else ''}"
            self.points_to_reactivate = []
        elif active_points:
            active_count = len(active_points)
            message = f"{active_count} punto{'s' if active_count > 1 else ''} de reciclaje activo{'s' if active_count > 1 else ''}"
            if inactive_points:
                inactive_count = len(inactive_points)
                message += f"\n {inactive_count} punto{'s' if inactive_count > 1 else ''} desactivado{'s' if inactive_count > 1 else ''}"
            self.center_message = message
        else:
            self.center_message = "Todos los puntos de reciclaje están desactivados"

        self.bottom_message = "Presiona ENTER para continuar"
        self.waiting_for_enter = True
        self.dice_total_message = ""
        self.game_state = "RECYCLING_STATUS"
        self.message_timer = pygame.time.get_ticks()

    def start_new_round(self):
        self.start_new_round_tracking()
        self.current_player = self.round_starting_player
        self.start_turn()

    def end_game(self):
        self.game_state = "GAME_OVER"

        if self.player1.badges > self.player2.badges:
            winner = f"{self.player1_name} gana la partida con más insignias que su oponente."
        elif self.player2.badges > self.player1.badges:
            winner = f"{self.player2_name} gana la partida con más insignias que su oponente."
        else:
            if self.player1.trash > self.player2.trash:
                winner = f"¡Qué duelo tan parejo!\nAmbos jugadores tienen la misma cantidad de insignias,\npero {self.player1_name} gana la partida gracias a su mayor esfuerzo recolectando basura."
            elif self.player2.trash > self.player1.trash:
                winner = f"¡Qué duelo tan parejo!\nAmbos jugadores tienen la misma cantidad de insignias,\npero {self.player2_name} gana la partida gracias a su mayor esfuerzo recolectando basura."
            else:
                winner = "¡Es un empate total! Ambos jugadores tienen las mismas insignias y basura."

        self.center_message = f"¡Fin del juego!\n\nResultados finales:\n{self.player1_name} - Insignias: {self.player1.badges} | Basura: {self.player1.trash}\n{self.player2_name} - Insignias: {self.player2.badges} | Basura: {self.player2.trash}\n\n{winner}"
        self.bottom_message = "Presiona ESC para salir"
        self.turn_message = ""
        self.dice_total_message = ""
        self.waiting_for_enter = False
        self.message_timer = pygame.time.get_ticks()

    def schedule_bot_action(self, action_type, delay_ms):
        self.bot_thinking = True
        self.bot_timer = pygame.time.get_ticks()
        self.bot_action_delay = delay_ms
        self.bot_next_action = action_type

    def execute_bot_action(self):
        self.bot_thinking = False

        if self.bot_next_action == "stop_initial_dice":
            self.stop_initial_dice(2)
        elif self.bot_next_action == "continue_after_message":
            if self.waiting_for_enter:
                self.handle_event(
                    pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN}))
        elif self.bot_next_action == "stop_first_dice":
            self.stop_first_dice()
        elif self.bot_next_action == "move_current_player":
            self.move_current_player()
        elif self.bot_next_action == "bot_make_choice":
            self.bot_make_choice()
        elif self.bot_next_action == "stop_purple_dice":
            self.stop_purple_dice()

        self.bot_next_action = None

    def handle_event(self, event):
        if not self.can_handle_input or self.transitioning or self.transition.active:
            return

        if event.type == pygame.USEREVENT + 1:
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)
            if self.game_state == "MOVING" and self.moves_remaining > 0:
                self.move_current_player()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.game_state == "GAME_OVER":
                    self.game.state_stack.pop(-2)
                    self.game.state_stack.pop(-2)
                    self.game.state_stack.pop(-1)
                else:
                    self.game.state_stack.pop(-2)
                    self.game.state_stack.pop(-2)
                    self.game.state_stack.pop(-1)

            elif event.key == pygame.K_RETURN:
                if self.game_state == "INITIAL_ROLL":
                    if self.initial_dice_phase == 1 and self.initial_dice1_rolling:
                        self.stop_initial_dice(1)
                    elif (
                        self.initial_dice_phase == 2
                        and self.initial_dice2_rolling
                        and not self.is_bot_mode):
                        self.stop_initial_dice(2)
                    elif self.initial_dice_phase == 3 and self.waiting_for_enter:
                        if self.current_player is not None:
                            self.game_state = "NEW_ROUND"
                            self.center_message = f"Ronda {self.current_round}"
                            self.bottom_message = "Presiona ENTER para continuar"
                            self.waiting_for_enter = True
                            self.message_timer = pygame.time.get_ticks()
                        else:
                            self.start_initial_dice_roll()

                elif self.waiting_for_enter:
                    if self.game_state == "TURN_START":
                        self.game_state = "PLAYER_TURN"
                        self.center_message = ""
                        self.waiting_for_enter = False
                    elif self.game_state == "DICE_SHOWING_RESULT":
                        self.dice_total_message = ""
                        self.dice_result = None
                        self.game_state = "MOVING"
                        self.waiting_for_enter = False
                        self.bottom_message = f"Pasos restantes: {self.moves_remaining} - ENTER para continuar"
                    elif self.game_state == "SQUARE_EFFECT":
                        self.end_turn()
                    elif self.game_state == "PURPLE_DICE_RESULT":
                        self.purple_dice_value = None
                        self.end_turn()
                    elif self.game_state == "RECYCLING_POINT_PASS":
                        self.center_message = ""
                        self.waiting_for_enter = False
                        if self.moves_remaining <= 0:
                            self.end_turn()
                        else:
                            self.game_state = "MOVING"
                            self.move_current_player()
                    elif self.game_state == "MINIGAME":
                        self.launch_minigame()
                    elif self.game_state == "ROUND_SUMMARY":
                        self.start_new_round_after_summary()
                    elif self.game_state == "RECYCLING_STATUS":
                        self.start_new_round()
                    elif self.game_state == "NEW_ROUND":
                        self.show_recycling_status()
                    elif self.game_state == "RECYCLING_MESSAGE":
                        self.start_turn()

                elif self.game_state == "DICE_ROLL":
                    if self.dice1_rolling:
                        self.stop_first_dice()
                    elif self.dice2_rolling:
                        self.stop_second_dice()

                elif self.game_state == "PURPLE_DICE":
                    if self.purple_dice_rolling:
                        self.stop_purple_dice()

            elif self.game_state == "PLAYER_TURN":
                self.start_dice_roll()

            elif self.game_state == "CHOICE":
                if event.key == pygame.K_LEFT:
                    self.make_choice(0)
                elif event.key == pygame.K_RIGHT:
                    self.make_choice(1 if len(self.choice_options) > 1 else 0)

            elif self.game_state == "MOVING":
                self.move_current_player()
            
    def _start_transition(self, callback):
        self.transitioning = True
        self.can_handle_input = False
        self.transition.start_fade_out(callback)

    def update(self, dt):
        self.transition.update(dt)

        if not self.transition.active and self.transitioning:
            self.transitioning = False
            self.can_handle_input = True

        self.update_dice_animation(dt)

        self.update_player_movement(dt)

        if (
            self.bot_thinking
            and pygame.time.get_ticks() - self.bot_timer > self.bot_action_delay):
            self.execute_bot_action()

        if (
            self.bot_second_dice_timer > 0
            and self.dice2_rolling
            and self.is_bot_mode
            and self.current_player == 2
            and pygame.time.get_ticks() - self.bot_second_dice_timer > self.bot_second_dice_delay):
            self.stop_second_dice()

        if self.game_state == "MOVING" and self.moves_remaining > 0:
            player_data = (
                self.player1_data if self.current_player == 1 else self.player2_data)
            if not player_data["moving"]:
                if self.is_bot_mode and self.current_player == 2:
                    if not self.bot_thinking:
                        self.schedule_bot_action(
                            "move_current_player", random.randint(300, 600))
                else:
                    if pygame.time.get_ticks() - self.message_timer > 500:
                        self.move_current_player()

        if self.game_state == "PLAYER_TURN":
            if pygame.time.get_ticks() - self.message_timer > 1000:
                self.start_dice_roll()

    def render(self, screen):
        if self.bg_image:
            screen.blit(self.bg_image, (0, 0))

        render_items = []

        for point in self.recycling_points:
            pos = self.casillas[point.id]
            icon = self.OpenR_image if point.timeout == 0 else self.CloseR_image

            icon_width = icon.get_width()
            icon_height = icon.get_height()

            offset_pos = (pos[0] + icon_width / 3, pos[1] - icon_height / 3)

            icon_rect = icon.get_rect(center=offset_pos)
            render_items.append(
                (icon_rect.bottom, icon, icon_rect))

        players_to_draw = [
            (1, self.player1_data, self.player1_frames),
            (2, self.player2_data, self.player2_frames),]

        for player_id, player_data, frames in players_to_draw:
            if player_data["moving"]:
                walk_frames = frames[1:]
                frame_index = (player_data["anim_frame"] // 8) % len(walk_frames)
                current_frame = walk_frames[frame_index]

                if player_data["move_from"][0] > player_data["move_to"][0]:
                    current_frame = pygame.transform.flip(current_frame, True, False)
            else:
                current_frame = frames[0]

            char_rect = current_frame.get_rect(center=player_data["pos_actual"])
            render_items.append((char_rect.bottom, current_frame, char_rect))

        render_items.sort(key=lambda x: x[0])
        for _, image, rect in render_items:
            screen.blit(image, rect)

        has_center_message = bool(self.center_message)
        has_dice = (
            self.dice_rolling
            or self.game_state == "INITIAL_ROLL"
            or self.game_state == "PURPLE_DICE"
            or self.game_state == "PURPLE_DICE_RESULT"
            or self.game_state == "DICE_SHOWING_RESULT"
            or (
                self.dice1_value is not None
                and self.dice2_value is not None
                and self.game_state in ["DICE_ROLL", "DICE_SHOWING_RESULT"]))
        has_dice_total = bool(self.dice_total_message)

        total_height = 0
        if has_center_message:
            lines = self.center_message.split("\n")
            total_height += len([l for l in lines if l.strip()]) * 25 + 40

        if has_dice:
            total_height += 80 + 20

        if has_dice_total:
            total_height += 30 + 10

        start_y = (SCREEN_HEIGHT - total_height) // 2
        current_y = start_y

        if has_center_message:
            lines = self.center_message.split("\n")
            line_height = 25
            max_width = 0

            rendered_lines = []
            for line in lines:
                if line.strip():
                    text_surface = self.font_message.render(line, True, WHITE)
                    rendered_lines.append(text_surface)
                    max_width = max(max_width, text_surface.get_width())

            if rendered_lines:
                box_width = min(max_width + 40, SCREEN_WIDTH - 40)
                box_height = len(rendered_lines) * line_height + 20
                box_x = (SCREEN_WIDTH - box_width) // 2

                if self.game_state in ["RULES", "COUNTDOWN"]:
                    bg_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                    bg_surface.fill((0, 0, 0, 180))
                    screen.blit(bg_surface, (0, 0))
                    
                    msg_bg_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
                    msg_bg_surface.fill((0, 0, 0, 200))
                    screen.blit(msg_bg_surface, (box_x, current_y))
                else:
                    bg_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
                    bg_surface.fill((0, 0, 0, 200))
                    screen.blit(bg_surface, (box_x, current_y))

                pygame.draw.rect(
                    screen, WHITE, (box_x, current_y, box_width, box_height), 2)

                for i, line_surface in enumerate(rendered_lines):
                    line_rect = line_surface.get_rect(
                        center=(SCREEN_WIDTH // 2, current_y + 20 + i * line_height))
                    screen.blit(line_surface, line_rect)

                current_y += box_height + 20

        if has_dice:
            dice_y = current_y

            if self.game_state == "INITIAL_ROLL":
                if self.initial_dice_phase == 1:
                    dice_pos = (SCREEN_WIDTH // 2, dice_y)
                    if self.initial_dice1_rolling:
                        dice_img = self.dice_images[self.current_initial_dice1_frame]
                    else:
                        dice_img = self.dice_images[(self.initial_dice1_value or 1) - 1]
                    screen.blit(
                        dice_img, (dice_pos[0] - dice_img.get_width() // 2, dice_pos[1]))

                    p1_label = self.font_small.render(self.player1_name, True, WHITE)
                    screen.blit(
                        p1_label,
                        (dice_pos[0] - p1_label.get_width() // 2, dice_pos[1] + 90),)

                elif self.initial_dice_phase >= 2:
                    dice_width = 80
                    dice_spacing = 40
                    total_width = dice_width * 2 + dice_spacing
                    start_x = (SCREEN_WIDTH - total_width) // 2
                    
                    dice1_pos = (start_x, dice_y)
                    dice2_pos = (start_x + dice_width + dice_spacing, dice_y)

                    dice1_img = self.dice_images[self.initial_dice1_value - 1]
                    if self.initial_dice2_rolling:
                        dice2_img = self.dice_images[self.current_initial_dice2_frame]
                    else:
                        dice2_img = self.dice_images[
                            (self.initial_dice2_value or 1) - 1]

                    screen.blit(dice1_img, dice1_pos)
                    screen.blit(dice2_img, dice2_pos)

                    p1_label = self.font_small.render(self.player1_name, True, WHITE)
                    p2_label = self.font_small.render(self.player2_name, True, WHITE)
                    screen.blit(
                        p1_label,
                        (
                            dice1_pos[0] + dice_width // 2 - p1_label.get_width() // 2,
                            dice1_pos[1] + 90,),)
                    screen.blit(
                        p2_label,
                        (
                            dice2_pos[0] + dice_width // 2 - p2_label.get_width() // 2,
                            dice2_pos[1] + 90,),)

            elif (
                self.game_state == "PURPLE_DICE"
                or self.game_state == "PURPLE_DICE_RESULT"):
                dice_pos = (SCREEN_WIDTH // 2, dice_y)
                if self.purple_dice_rolling:
                    dice_img = self.dice_images[self.current_purple_dice_frame]
                else:
                    dice_img = self.dice_images[(self.purple_dice_value or 1) - 1]
                screen.blit(
                    dice_img, (dice_pos[0] - dice_img.get_width() // 2, dice_pos[1]))

            else:
                dice_width = 80
                spacing = 40 
                total_dice_width = dice_width * 2 + spacing
                start_x = (SCREEN_WIDTH - total_dice_width) // 2
                
                dice1_pos = (start_x, dice_y)
                dice2_pos = (start_x + dice_width + spacing, dice_y)

                if self.dice1_rolling:
                    dice1_img = self.dice_images[self.current_dice1_frame]
                elif self.dice1_value is not None:
                    dice1_img = self.dice_images[self.dice1_value - 1]
                else:
                    dice1_img = None

                if self.dice2_rolling:
                    dice2_img = self.dice_images[self.current_dice2_frame]
                elif self.dice2_value is not None:
                    dice2_img = self.dice_images[self.dice2_value - 1]
                else:
                    dice2_img = None

                if dice1_img:
                    screen.blit(dice1_img, dice1_pos)

                if dice2_img:
                    screen.blit(dice2_img, dice2_pos)
                
                if self.dice1_value is not None or self.dice1_rolling:
                    plus_font = load_font("assets/fonts/PublicPixel.ttf", 48)
                    plus_text = plus_font.render("+", True, WHITE)
                    plus_x = dice1_pos[0] + dice_width + (spacing // 2)
                    plus_y = dice_y + (dice_width // 2)
                    plus_rect = plus_text.get_rect(center=(plus_x, plus_y))
                    screen.blit(plus_text, plus_rect)

            current_y += 80 + 20

        if has_dice_total:
            dice_text = self.font_title.render(self.dice_total_message, True, WHITE)
            dice_rect = dice_text.get_rect(center=(SCREEN_WIDTH // 2, current_y))

            bg_rect = pygame.Rect(
                dice_rect.x - 20,
                dice_rect.y - 10,
                dice_rect.width + 40,
                dice_rect.height + 20,)
            bg_surface = pygame.Surface(
                (bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 200))
            screen.blit(bg_surface, bg_rect)
            pygame.draw.rect(screen, WHITE, bg_rect, 2)
            screen.blit(dice_text, dice_rect)

        if self.bottom_message:
            bottom_text = self.font_small.render(self.bottom_message, True, WHITE)
            bottom_rect = bottom_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))

            bg_rect = pygame.Rect(
                bottom_rect.x - 10,
                bottom_rect.y - 5,
                bottom_rect.width + 20,
                bottom_rect.height + 10,)
            bg_surface = pygame.Surface(
                (bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 150))
            screen.blit(bg_surface, bg_rect)
            screen.blit(bottom_text, bottom_rect)

        self.draw_game_info(screen)

        if self.bot_thinking and self.current_player == 2 and self.is_bot_mode:
            thinking_text = self.font_small.render("Pensando...", True, WHITE)
            thinking_rect = thinking_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
            screen.blit(thinking_text, thinking_rect)

        self.transition.render(screen)

    def draw_game_info(self, screen):
        if self.turn_message:
            turn_text = self.font_turn.render(self.turn_message, True, WHITE)
            turn_rect = turn_text.get_rect(topleft=(20, 20))

            bg_rect = pygame.Rect(
                turn_rect.x - 10,
                turn_rect.y - 5,
                turn_rect.width + 20,
                turn_rect.height + 10,)
            bg_surface = pygame.Surface(
                (bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surface.fill((0, 100, 0, 150))
            screen.blit(bg_surface, bg_rect)
            screen.blit(turn_text, turn_rect)

        display_round = min(self.current_round, self.rounds)
        round_text = self.font_title.render(
            f"RONDA {display_round}/{self.rounds}", True, WHITE)
        round_rect = round_text.get_rect(topright=(SCREEN_WIDTH - 20, 20))

        bg_rect = pygame.Rect(
            round_rect.x - 10,
            round_rect.y - 5,
            round_rect.width + 20,
            round_rect.height + 10,)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))
        screen.blit(bg_surface, bg_rect)
        screen.blit(round_text, round_rect)

        y_offset = 70

        p1_info = f"{self.player1_name}: Insignias {self.player1.badges} | Basura {self.player1.trash}"
        p1_text = self.font_small.render(p1_info, True, WHITE)
        p1_rect = p1_text.get_rect(topright=(SCREEN_WIDTH - 20, y_offset))

        bg_rect = pygame.Rect(
            p1_rect.x - 10, p1_rect.y - 5, p1_rect.width + 20, p1_rect.height + 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))
        screen.blit(bg_surface, bg_rect)
        screen.blit(p1_text, p1_rect)

        y_offset += 30
        p2_info = f"{self.player2_name}: Insignias {self.player2.badges} | Basura {self.player2.trash}"
        p2_text = self.font_small.render(p2_info, True, WHITE)
        p2_rect = p2_text.get_rect(topright=(SCREEN_WIDTH - 20, y_offset))

        bg_rect = pygame.Rect(
            p2_rect.x - 10, p2_rect.y - 5, p2_rect.width + 20, p2_rect.height + 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))
        screen.blit(bg_surface, bg_rect)
        screen.blit(p2_text, p2_rect)