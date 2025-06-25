# Pantalla para seleccionar personajes

import pygame
import random
from core.config import config
from core.state import State
from core.settings import SCREEN_WIDTH, WHITE
from core.utils import load_font, get_character
from core.background_manager import BackgroundManager
from core.effects import TransitionEffect


class CharacterSelection(State):
    def __init__(self, game):
        super().__init__(game)
        pygame.mouse.set_visible(False)

        self.background = BackgroundManager()

        self.transition = TransitionEffect(0.15)
        self.transition.start_fade_in()

        self.transitioning = False
        self.can_handle_input = True

        self.font_title = load_font("assets/fonts/PublicPixel.ttf", 28)
        self.font_button = load_font("assets/fonts/PublicPixel.ttf", 18)
        self.font_controls = load_font("assets/fonts/mc-ten-lowercase-alt.ttf", 11)
        self.label_font = load_font("assets/fonts/PublicPixel.ttf", 14)

        self.title_y_position = 80
        self.panels_y_position = 180
        self.panel_width = 160
        self.panel_height = 220
        self.panels_spacing = 200
        self.arrow_distance = 90
        self.arrow_size = 150

        self.controls_offset_y = (80)
        self.controls_line_spacing = 15
        self.controls_font_size = 12

        self.font_controls = load_font("assets/fonts/mc-ten-lowercase-alt.ttf", self.controls_font_size)

        self.title_surface = self._render_text_with_shadow(self.font_title, "SELECCIONA TU PERSONAJE", WHITE)
        self.title_rect = self.title_surface.get_rect(center=(SCREEN_WIDTH // 2, self.title_y_position))

        # Cargar personajes
        character_paths = get_character(4)
        self.character_names = ["Rosalba", "Tinú", "Sofia", "Luis"]
        self.characters = []

        for i, path in enumerate(character_paths):
            img = pygame.image.load(path).convert_alpha()
            if i < 2:
                img = pygame.transform.scale(img, (99, 180))
            else:
                img = pygame.transform.scale(img, (107, 153))
            self.characters.append(img)

        self.selected_p1 = 0
        self.selected_p2 = 1
        self.confirmed_p1 = False
        self.confirmed_p2 = False
        self.final_p1 = None
        self.final_p2 = None

        config.characters.clear()
        config.characters.extend([None, None])

        total_width = self.panel_width * 2 + self.panels_spacing
        start_x = (SCREEN_WIDTH - total_width) // 2

        self.p1_rect = pygame.Rect(
            start_x, self.panels_y_position, self.panel_width, self.panel_height)
        self.p2_rect = pygame.Rect(
            start_x + self.panel_width + self.panels_spacing,
            self.panels_y_position,
            self.panel_width,
            self.panel_height,)

        self.p1_label = self._render_text_with_shadow(
            self.label_font, "JUGADOR 1", WHITE)
        self.p2_label = self._render_text_with_shadow(
            self.label_font, "JUGADOR 2" if not config.machine_mode else "BOT", WHITE)

        try:
            flecha_original = pygame.image.load(
                "assets/images/selection/arrow.png"
            ).convert_alpha()

            original_width = flecha_original.get_width()
            original_height = flecha_original.get_height()

            scale = self.arrow_size / max(original_width, original_height)

            new_width = int(original_width * scale)
            new_height = int(original_height * scale)

            flecha_base = pygame.transform.scale(
                flecha_original, (new_width, new_height)
            )
            self.flecha_left = flecha_base
            self.flecha_right = pygame.transform.rotate(flecha_base, 180)

        except Exception as e:
            self.flecha_right = pygame.Surface((self.arrow_size, self.arrow_size))
            self.flecha_right.fill(WHITE)
            self.flecha_left = self.flecha_right.copy()

        self.controls_p1 = ["A/D - Cambiar", "F - Confirmar"]
        self.controls_p2 = (
            ["<-/-> - Cambiar", "Enter - Confirmar"]
            if not config.machine_mode
            else ["Automático"])

        self.both_confirmed = False

    def _render_text_with_shadow(
        self, font, text, text_color, shadow_color=(128, 128, 128), shadow_offset=2):
        shadow_surface = font.render(text, True, shadow_color)
        text_surface = font.render(text, True, text_color)

        combined_width = text_surface.get_width() + shadow_offset
        combined_height = text_surface.get_height() + shadow_offset
        combined_surface = pygame.Surface(
            (combined_width, combined_height), pygame.SRCALPHA
        )

        combined_surface.blit(shadow_surface, (shadow_offset, shadow_offset))
        combined_surface.blit(text_surface, (0, 0))

        return combined_surface

    def check_both_confirmed(self):
        if self.confirmed_p1 and self.confirmed_p2 and not self.both_confirmed:
            self.both_confirmed = True
            pygame.time.set_timer(pygame.USEREVENT + 10, 500)

    def handle_event(self, event):
        if not self.can_handle_input or self.transitioning or self.transition.active:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and not self.both_confirmed:
                self._start_transition(lambda: self.game.state_stack.pop())

            # Controles Player 1
            elif event.key == pygame.K_a and not self.confirmed_p1:
                self.selected_p1 = (self.selected_p1 - 1) % len(self.characters)
            elif event.key == pygame.K_d and not self.confirmed_p1:
                self.selected_p1 = (self.selected_p1 + 1) % len(self.characters)
            elif event.key == pygame.K_f:
                if not self.confirmed_p1:
                    # Confirmar selección P1
                    if not self.confirmed_p2 or self.selected_p1 != self.final_p2:
                        self.confirmed_p1 = True
                        self.final_p1 = self.selected_p1
                        config.characters[0] = self.final_p1

                        if config.machine_mode:
                            available_chars = [
                                i
                                for i in range(len(self.characters))
                                if i != self.final_p1
                            ]
                            self.final_p2 = random.choice(available_chars)
                            self.selected_p2 = self.final_p2
                            self.confirmed_p2 = True
                            config.characters[1] = self.final_p2
                        self.check_both_confirmed()
                else:
                    if not self.both_confirmed:
                        self.confirmed_p1 = False
                        self.final_p1 = None
                        config.characters[0] = None

                        if config.machine_mode:
                            self.confirmed_p2 = False
                            self.final_p2 = None
                            config.characters[1] = None
                            self.both_confirmed = False

            # Controles Player 2 (solo si no es bot)
            elif not config.machine_mode:
                if event.key == pygame.K_LEFT and not self.confirmed_p2:
                    self.selected_p2 = (self.selected_p2 - 1) % len(self.characters)
                elif event.key == pygame.K_RIGHT and not self.confirmed_p2:
                    self.selected_p2 = (self.selected_p2 + 1) % len(self.characters)
                elif event.key == pygame.K_RETURN:
                    if not self.confirmed_p2:
                        # Confirmar selección P2
                        if not self.confirmed_p1 or self.selected_p2 != self.final_p1:
                            self.confirmed_p2 = True
                            self.final_p2 = self.selected_p2
                            config.characters[1] = self.final_p2
                            self.check_both_confirmed()
                    else:
                        if not self.both_confirmed:
                            self.confirmed_p2 = False
                            self.final_p2 = None
                            config.characters[1] = None

        if event.type == pygame.USEREVENT + 10:
            pygame.time.set_timer(pygame.USEREVENT + 10, 0)
            if None not in config.characters:

                def go_to_game():
                    from states.visual_board_game import BoardGameView

                    self.game.state_stack.append(BoardGameView(self.game))

                self._start_transition(go_to_game)

    def _start_transition(self, callback):
        self.transitioning = True
        self.can_handle_input = False
        self.transition.start_fade_out(callback)

    def update(self, dt):
        self.background.update(dt)
        self.transition.update(dt)

        if not self.transition.active and self.transitioning:
            self.transitioning = False
            self.can_handle_input = True

    def render(self, screen):
        self.background.render(screen)

        screen.blit(self.title_surface, self.title_rect)

        p1_label_rect = self.p1_label.get_rect(
            center=(self.p1_rect.centerx, self.p1_rect.top - 20))
        p2_label_rect = self.p2_label.get_rect(
            center=(self.p2_rect.centerx, self.p2_rect.top - 20))
        screen.blit(self.p1_label, p1_label_rect)
        screen.blit(self.p2_label, p2_label_rect)

        self._draw_character_panel(
            screen, self.p1_rect, self.selected_p1, self.confirmed_p1, "p1")
        self._draw_character_panel(
            screen, self.p2_rect, self.selected_p2, self.confirmed_p2, "p2")

        self._draw_character_button(
            screen, self.p1_rect, self.confirmed_p1, self.selected_p1, "p1")
        self._draw_character_button(
            screen, self.p2_rect, self.confirmed_p2, self.selected_p2, "p2")

        self._draw_controls(screen)

        if not self.confirmed_p1:
            left_arrow_pos = (
                self.p1_rect.left - self.arrow_distance,
                self.p1_rect.centery - self.flecha_left.get_height() // 2,
            )
            screen.blit(self.flecha_left, left_arrow_pos)

            right_arrow_pos = (
                self.p1_rect.right
                + self.arrow_distance
                - self.flecha_right.get_width(),
                self.p1_rect.centery - self.flecha_right.get_height() // 2,
            )
            screen.blit(self.flecha_right, right_arrow_pos)

        if not config.machine_mode and not self.confirmed_p2:
            left_arrow_pos = (
                self.p2_rect.left - self.arrow_distance,
                self.p2_rect.centery - self.flecha_left.get_height() // 2,
            )
            screen.blit(self.flecha_left, left_arrow_pos)

            right_arrow_pos = (
                self.p2_rect.right
                + self.arrow_distance
                - self.flecha_right.get_width(),
                self.p2_rect.centery - self.flecha_right.get_height() // 2,
            )
            screen.blit(self.flecha_right, right_arrow_pos)

        self.transition.render(screen)

    def _draw_controls(self, screen):
        y_start = self.p1_rect.bottom + self.controls_offset_y
        for i, control in enumerate(self.controls_p1):
            text = self._render_text_with_shadow(
                self.font_controls, control, WHITE, (100, 100, 100), 1
            )
            text_rect = text.get_rect(
                center=(self.p1_rect.centerx, y_start + i * self.controls_line_spacing)
            )
            screen.blit(text, text_rect)

        y_start = self.p2_rect.bottom + self.controls_offset_y
        for i, control in enumerate(self.controls_p2):
            text = self._render_text_with_shadow(
                self.font_controls, control, WHITE, (100, 100, 100), 1
            )
            text_rect = text.get_rect(
                center=(self.p2_rect.centerx, y_start + i * self.controls_line_spacing)
            )
            screen.blit(text, text_rect)

    def _draw_character_panel(self, screen, rect, selected_idx, is_confirmed, player):
        if is_confirmed:
            panel_color = (40, 80, 40, 100)
        else:
            panel_color = (60, 60, 60, 100)

        panel_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        panel_surface.fill(panel_color)
        screen.blit(panel_surface, rect)

        pygame.draw.rect(screen, WHITE, rect, 2)

        char = self.characters[selected_idx]

        if player == "p2":
            char = pygame.transform.flip(char, True, False)

        char_rect = char.get_rect(center=rect.center)
        screen.blit(char, char_rect)

    def _draw_character_button(
        self, screen, panel_rect, is_confirmed, selected_idx, player):
        name = self.character_names[selected_idx]

        if player == "p2" and config.machine_mode:
            name = f"Bot: {name}"

        if is_confirmed:
            name += " ✓"

        if is_confirmed:
            button_font = load_font("assets/fonts/PublicPixel.ttf", 20)
            text_surface = self._render_text_with_shadow(
                button_font, name, WHITE, (100, 100, 100), 2
            )
        else:
            text_surface = self._render_text_with_shadow(
                self.font_button, name, WHITE, (100, 100, 100), 1
            )

        text_rect = text_surface.get_rect(
            center=(panel_rect.centerx, panel_rect.bottom + 30)
        )

        padding = 8
        bg_rect = pygame.Rect(
            text_rect.left - padding,
            text_rect.top - padding // 2,
            text_rect.width + padding * 2,
            text_rect.height + padding,
        )

        if is_confirmed:
            bg_color = (40, 80, 40, 180)
        else:
            bg_color = (40, 40, 40, 180)

        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill(bg_color)
        screen.blit(bg_surface, bg_rect)

        pygame.draw.rect(screen, WHITE, bg_rect, 1)

        screen.blit(text_surface, text_rect)