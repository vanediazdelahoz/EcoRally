# Minijuego "Pesca Responsable"

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

        self.transition = TransitionEffect(0.15)
        self.transition.start_fade_in()

        self.transitioning = False
        self.can_handle_input = True

        self.font = load_font("assets/fonts/PublicPixel.ttf", 22)
        self.font_small = load_font("assets/fonts/PublicPixel.ttf", 16)
        self.font_final = load_font("assets/fonts/PublicPixel.ttf", 32)

        character_names = ["Rosalba", "Tinú", "Sofia", "Luis"]
        self.player1_name = character_names[config.characters[0]]
        self.player2_name = (
            character_names[config.characters[1]]
            if not config.machine_mode
            else f"Bot {character_names[config.characters[1]]}")

        self.FPS = 60
        self.ROUND_TIME = 30
        self.PLAYER_SIZE = 150
        self.TRASH_SIZE = 40
        self.TOP_MARGIN = 250
        self.TRASH_LIMIT_BOTTOM = SCREEN_HEIGHT - 50

        self.BARCO1_POS = (80, self.TOP_MARGIN - 160)
        self.BARCO2_POS = (SCREEN_WIDTH - 280, self.TOP_MARGIN - 160)

        self.players = [
            {
                "rect": pygame.Rect(
                    self.BARCO1_POS[0] + 100,
                    self.BARCO1_POS[1] + 120,
                    self.PLAYER_SIZE // 2,
                    self.PLAYER_SIZE // 2,),
                "score": 0,
                "image": None,
                "keys": {
                    "up": pygame.K_w,
                    "down": pygame.K_s,
                    "left": pygame.K_a,
                    "right": pygame.K_d,},},
            {
                "rect": pygame.Rect(
                    self.BARCO2_POS[0] - 50,
                    self.BARCO2_POS[1] + 120,
                    self.PLAYER_SIZE // 2,
                    self.PLAYER_SIZE // 2,),
                "score": 0,
                "image": None,
                "keys": {
                    "up": pygame.K_UP,
                    "down": pygame.K_DOWN,
                    "left": pygame.K_LEFT,
                    "right": pygame.K_RIGHT,},},]

        self.load_images()
        self.trash_list = []
        self.start_ticks = pygame.time.get_ticks()
        
        # Estados del minijuego
        self.game_state = "RULES"
        self.countdown = 3
        self.countdown_timer = 0
        
        self.trash_spawn_counter = 0
        self.trash_spawn_frequency = (1)

    def load_images(self):
        try:
            self.background_img = pygame.image.load(
                "assets/images/minigames/responsible_fishing/background_responsible_fishing.jpg").convert()
            self.background_img = pygame.transform.scale(
                self.background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception as e:
            self.background_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background_img.fill((0, 100, 200))

        try:
            self.BARCO1_IMAGE = pygame.image.load(
                "assets/images/minigames/responsible_fishing/boat_left.png").convert_alpha()
            self.BARCO2_IMAGE = pygame.image.load(
                "assets/images/minigames/responsible_fishing/boat_right.png").convert_alpha()
            self.BARCO1_IMAGE = pygame.transform.scale(self.BARCO1_IMAGE, (200, 200))
            self.BARCO2_IMAGE = pygame.transform.scale(self.BARCO2_IMAGE, (200, 200))
        except Exception as e:
            self.BARCO1_IMAGE = pygame.Surface((200, 200))
            self.BARCO1_IMAGE.fill((139, 69, 19))
            self.BARCO2_IMAGE = pygame.Surface((200, 200))
            self.BARCO2_IMAGE.fill((139, 69, 19))

        try:
            player1_img = pygame.image.load(
                "assets/images/minigames/responsible_fishing/bait_left.png").convert_alpha()
            player2_img = pygame.image.load(
                "assets/images/minigames/responsible_fishing/bait_right.png").convert_alpha()
            self.players[0]["image"] = pygame.transform.scale(
                player1_img, (self.PLAYER_SIZE, self.PLAYER_SIZE))
            self.players[1]["image"] = pygame.transform.scale(
                player2_img, (self.PLAYER_SIZE, self.PLAYER_SIZE))
        except Exception as e:
            self.players[0]["image"] = pygame.Surface(
                (self.PLAYER_SIZE, self.PLAYER_SIZE))
            self.players[0]["image"].fill((255, 255, 0))
            self.players[1]["image"] = pygame.Surface(
                (self.PLAYER_SIZE, self.PLAYER_SIZE))
            self.players[1]["image"].fill((255, 255, 0))

        try:
            aluminio_img = pygame.image.load(
                "assets/images/minigames/trash/aluminum.png").convert_alpha()
            botella_img = pygame.image.load(
                "assets/images/minigames/trash/bottle.png").convert_alpha()
            lata_img = pygame.image.load(
                "assets/images/minigames/trash/can.png").convert_alpha()

            self.ALL_TRASH_IMAGES = [
                pygame.transform.scale(
                    aluminio_img, (self.TRASH_SIZE, self.TRASH_SIZE)),
                pygame.transform.scale(botella_img, (self.TRASH_SIZE, self.TRASH_SIZE)),
                pygame.transform.scale(lata_img, (self.TRASH_SIZE, self.TRASH_SIZE)),]
        except Exception as e:
            self.ALL_TRASH_IMAGES = []
            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
            for color in colors:
                trash_surf = pygame.Surface((self.TRASH_SIZE, self.TRASH_SIZE))
                trash_surf.fill(color)
                self.ALL_TRASH_IMAGES.append(trash_surf)

    def spawn_trash(self):
        direction = random.choice(["left", "right"])
        y = random.randint(self.TOP_MARGIN, self.TRASH_LIMIT_BOTTOM - self.TRASH_SIZE)
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
        for trash in self.trash_list:
            trash["rect"].x += trash["speed"]

    def handle_player_input(self, player, keys_pressed):
        speed = 4
        if keys_pressed[player["keys"]["up"]]:
            player["rect"].y -= speed
        if keys_pressed[player["keys"]["down"]]:
            player["rect"].y += speed
        if keys_pressed[player["keys"]["left"]]:
            player["rect"].x -= speed
        if keys_pressed[player["keys"]["right"]]:
            player["rect"].x += speed

        player["rect"].clamp_ip(
            pygame.Rect(
                0,
                self.TOP_MARGIN - player["rect"].height // 2,
                SCREEN_WIDTH,
                self.TRASH_LIMIT_BOTTOM - (self.TOP_MARGIN - player["rect"].height),))

    def check_collisions(self):
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

            elif self.game_state == "RULES" and event.key == pygame.K_RETURN:
                self.game_state = "COUNTDOWN"
                self.countdown_timer = pygame.time.get_ticks()
            elif self.game_state == "GAME_OVER":
                if event.key == pygame.K_RETURN:
                    self._end_minigame()

    def bot_move(self, player):
        if not self.trash_list:
            return

        target = min(
            self.trash_list,
            key=lambda t: abs(t["rect"].x - player["rect"].x)
            + abs(t["rect"].y - player["rect"].y),)
        speed = 3

        if player["rect"].x < target["rect"].x:
            player["rect"].x += speed
        elif player["rect"].x > target["rect"].x:
            player["rect"].x -= speed

        if player["rect"].y < target["rect"].y:
            player["rect"].y += speed
        elif player["rect"].y > target["rect"].y:
            player["rect"].y -= speed

        player["rect"].clamp_ip(
            pygame.Rect(
                0,
                self.TOP_MARGIN - player["rect"].height // 2,
                SCREEN_WIDTH,
                self.TRASH_LIMIT_BOTTOM - (self.TOP_MARGIN - player["rect"].height),))

    def _start_transition(self, callback):
        self.transitioning = True
        self.can_handle_input = False
        self.transition.start_fade_out(callback)

    def _end_minigame(self):
        if len(self.game.state_stack) >= 2:
            board_game = self.game.state_stack[-2]
            if hasattr(board_game, "continue_after_minigame"):
                board_game.continue_after_minigame(
                    self.players[0]["score"], self.players[1]["score"])

        self._start_transition(lambda: self.game.state_stack.pop())

    def update(self, dt):
        self.transition.update(dt)

        if not self.transition.active and self.transitioning:
            self.transitioning = False
            self.can_handle_input = True

        if self.game_state == "COUNTDOWN":
            current_time = pygame.time.get_ticks()
            if current_time - self.countdown_timer >= 1000:
                self.countdown -= 1
                self.countdown_timer = current_time
                
                if self.countdown <= 0:
                    self.game_state = "PLAYING"
                    self.start_ticks = pygame.time.get_ticks()

        elif self.game_state == "PLAYING":
            elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000
            time_left = self.ROUND_TIME - elapsed_time

            if time_left <= 0:
                self.game_state = "GAME_OVER"
                return

            keys_pressed = pygame.key.get_pressed()

            self.handle_player_input(
                self.players[0], keys_pressed)

            if config.machine_mode:
                self.bot_move(self.players[1])
            else:
                self.handle_player_input(
                    self.players[1], keys_pressed)

            self.trash_spawn_counter += 1
            if self.trash_spawn_counter >= self.trash_spawn_frequency:
                self.spawn_trash()
                self.trash_spawn_counter = 0

            self.move_trash()

            self.trash_list[:] = [
                t
                for t in self.trash_list
                if -self.TRASH_SIZE <= t["rect"].x <= SCREEN_WIDTH]

            self.check_collisions()

    def render(self, screen):
        screen.blit(self.background_img, (0, 0))

        if self.game_state == "RULES":
            overlay_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay_surface.fill((0, 0, 0, 180))
            screen.blit(overlay_surface, (0, 0))
            
            rules_text = [
                "Pesca Responsable",
                "",
                "Pesca responsable en el océano:",
                "• Muévete para recoger la basura flotante",
                "• Cada pieza de basura vale 1 punto",
                "• Limpia el océano de contaminación",
                "",
                "Controles:",
                f"{self.player1_name}: W, A, S, D",
                f"{self.player2_name}: ↑, ←, ↓, →",
                "",
                "Tienes 30 segundos para limpiar el océano.",
                "",
                "Presiona ENTER para comenzar"
            ]
            
            line_surfaces = [self.font_small.render(line, True, WHITE) for line in rules_text]
            
            line_height = 30
            total_height = len(line_surfaces) * line_height
            
            y_offset = (SCREEN_HEIGHT - total_height) // 2
            
            for text_surface in line_surfaces:
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
                screen.blit(text_surface, text_rect)
                y_offset += line_height
            return

        elif self.game_state == "COUNTDOWN":
            countdown_text = str(self.countdown) if self.countdown > 0 else "¡EMPEZAR!"
            countdown_surface = self.font_final.render(countdown_text, True, WHITE)
            countdown_rect = countdown_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            
            bg_rect = pygame.Rect(
                countdown_rect.x - 50,
                countdown_rect.y - 30,
                countdown_rect.width + 100,
                countdown_rect.height + 60
            )
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 200))
            screen.blit(bg_surface, bg_rect)
            pygame.draw.rect(screen, WHITE, bg_rect, 3)
            
            screen.blit(countdown_surface, countdown_rect)
            return

        screen.blit(self.BARCO1_IMAGE, self.BARCO1_POS)
        screen.blit(self.BARCO2_IMAGE, self.BARCO2_POS)

        for player in self.players:
            screen.blit(player["image"], player["rect"])

        if self.game_state == "PLAYING":
            for trash in self.trash_list:
                screen.blit(trash["image"], trash["rect"])

        texto1 = self.font.render(
            f"{self.player1_name}: {self.players[0]['score']}", True, WHITE)
        screen.blit(texto1, (20, 10))

        texto2 = self.font.render(
            f"{self.player2_name}: {self.players[1]['score']}", True, WHITE)
        texto2_rect = texto2.get_rect(topright=(SCREEN_WIDTH - 20, 10))
        screen.blit(texto2, texto2_rect)

        if self.game_state == "PLAYING":
            elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000
            time_left = max(0, self.ROUND_TIME - elapsed_time)
        else:
            time_left = 0

        tiempo_rect = pygame.Rect(SCREEN_WIDTH // 2 - 40, 10, 80, 40)
        pygame.draw.rect(screen, BLACK, tiempo_rect)
        pygame.draw.rect(screen, WHITE, tiempo_rect, 2)
        tiempo_txt = self.font.render(str(int(time_left)), True, WHITE)
        txt_rect = tiempo_txt.get_rect(center=tiempo_rect.center)
        screen.blit(tiempo_txt, txt_rect)

        if self.game_state == "GAME_OVER":
            self.draw_end_game_overlay(screen)

        self.transition.render(screen)

    def draw_end_game_overlay(self, screen):
        s1 = self.players[0]["score"]
        s2 = self.players[1]["score"]
        if s1 > s2:
            mensaje = f"¡Felicidades {self.player1_name}, ganaste!"
        elif s2 > s1:
            mensaje = f"¡Felicidades {self.player2_name}, ganaste!"
        else:
            mensaje = "¡Empate!"

        lines = [mensaje, f"{self.player1_name}: {s1}   {self.player2_name}: {s2}"]

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

        resumen = f"{self.player1_name}: {s1}   {self.player2_name}: {s2}"
        resumen_surf = self.font.render(resumen, True, WHITE)
        resumen_rect = resumen_surf.get_rect(center=(cuadro.centerx, cuadro.y + 70))
        screen.blit(resumen_surf, resumen_rect)

        continuar = "Presiona ENTER para continuar"
        continuar_surf = self.font_small.render(continuar, True, WHITE)
        continuar_rect = continuar_surf.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))

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