# states/visual_board_game.py
import pygame
import random
import sys
import os
from core.config import config
from core.state import State
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, GREEN, get_coordinate
from core.utils import load_font, get_character
from core.background_manager import BackgroundManager
from core.effects import TransitionEffect

# Importar lógica del juego desde el directorio correcto
from states.board_game import create_board, setup_recycling_points, Player
from states.square import Square

class BoardGameView(State):
    def __init__(self, game):
        super().__init__(game)
        pygame.mouse.set_visible(False)
        
        # Gestor de fondo con Mapa.png
        self.background = BackgroundManager("Mapa.png")
        
        # Efecto de transición
        self.transition = TransitionEffect(0.15)
        self.transition.start_fade_in()
        
        # Control de transición
        self.transitioning = False
        self.can_handle_input = True
        
        # Fuentes
        self.font_title = load_font("assets/fonts/PublicPixel.ttf", 24)
        self.font_message = load_font("assets/fonts/PublicPixel.ttf", 16)
        self.font_small = load_font("assets/fonts/PublicPixel.ttf", 12)
        
        # === CONFIGURACIÓN DEL JUEGO ===
        self.rounds = 10
        self.current_round = 1
        self.total_recycling_points = 3
        self.recycle_timeout = 2
        self.initial_trash = 10
        
        # Coordenadas del tablero
        self.casillas = get_coordinate(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Crear tablero usando la lógica exacta de board_game.py
        self.squares = create_board()
        self.recycling_points = setup_recycling_points(self.squares, self.total_recycling_points)
        
        # Crear jugadores
        self.player1 = Player("Jugador 1")
        self.player2 = Player("Bot" if config.machine_mode else "Jugador 2")
        self.player1.trash = self.initial_trash
        self.player2.trash = self.initial_trash
        
        # Posicionar jugadores en casilla inicial
        self.player1.move_to(self.squares[0])
        self.player2.move_to(self.squares[0])
        
        # Cargar imágenes de personajes
        self.load_character_images()
        
        # Cargar dados
        self.load_dice_images()
        
        # Estado del juego
        self.game_state = "INITIAL_ROLL"  # INITIAL_ROLL, PLAYER_TURN, DICE_ROLL, MOVING, CHOICE, MINIGAME, GAME_OVER
        self.current_player = 1  # 1 o 2
        self.dice_result = None
        self.moves_remaining = 0
        self.message = "¡Bienvenidos a EcoRally!"
        self.message_timer = 0
        self.choice_options = []
        
        # Animación de dados - AUTOMÁTICA CON ENTER PARA DETENER
        self.dice_rolling = False
        self.dice_start_time = 0
        self.dice_auto_duration = 3000  # 3 segundos de giro automático
        self.dice_roll_interval = 100
        self.dice_last_update = 0
        self.current_dice_frame = 0
        self.dice_result_display_time = 2000
        self.dice_result_time = 0
        self.dice_can_stop = False  # Flag para permitir detener con Enter
        
        # Posiciones visuales de jugadores
        self.player1_visual_pos = list(self.casillas[0])
        self.player2_visual_pos = list(self.casillas[0])
        self.player1_target_pos = list(self.casillas[0])
        self.player2_target_pos = list(self.casillas[0])
        self.move_speed = 200  # píxeles por segundo
        
        # Minijuegos disponibles
        self.available_minigames = ["a_la_caneca", "cielo_en_crisis", "pesca_responsable"]
        self.selected_minigame = None
        
        # Determinar quién empieza
        self.determine_starting_player()
    
    def load_character_images(self):
        """Cargar imágenes de personajes seleccionados"""
        try:
            # Cargar personajes según selección
            character_paths = get_character(4)
            
            # Player 1
            char1_path = character_paths[config.characters[0]]
            self.player1_img = pygame.image.load(char1_path).convert_alpha()
            self.player1_img = pygame.transform.scale(self.player1_img, (40, 60))
            
            # Player 2
            char2_path = character_paths[config.characters[1]]
            self.player2_img = pygame.image.load(char2_path).convert_alpha()
            self.player2_img = pygame.transform.scale(self.player2_img, (40, 60))
            # Voltear player 2
            self.player2_img = pygame.transform.flip(self.player2_img, True, False)
            
        except Exception as e:
            print(f"Error cargando personajes: {e}")
            # Crear rectángulos como fallback
            self.player1_img = pygame.Surface((40, 60))
            self.player1_img.fill((0, 255, 0))
            self.player2_img = pygame.Surface((40, 60))
            self.player2_img.fill((255, 0, 0))
    
    def load_dice_images(self):
        """Cargar imágenes de dados"""
        try:
            self.dice_images = []
            for i in range(1, 7):
                img = pygame.image.load(f"assets/Dado/Dado{i}.png").convert_alpha()
                img = pygame.transform.scale(img, (80, 80))
                self.dice_images.append(img)
        except Exception as e:
            print(f"Error cargando dados: {e}")
            # Crear dados simples como fallback
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
    
    def determine_starting_player(self):
        """Determinar quién empieza con dados iniciales"""
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        
        self.message = f"Tiro inicial — {self.player1.character}: {dice1} | {self.player2.character}: {dice2}"
        
        if dice1 > dice2:
            self.current_player = 1
            self.message += f"\n{self.player1.character} comienza"
        elif dice2 > dice1:
            self.current_player = 2
            self.message += f"\n{self.player2.character} comienza"
        else:
            self.message += "\nEmpate. Se lanzan los dados de nuevo"
            # En caso de empate, volver a tirar (simplificado: elegir aleatoriamente)
            self.current_player = random.choice([1, 2])
        
        self.message_timer = pygame.time.get_ticks()
        self.game_state = "PLAYER_TURN"
    
    def start_dice_roll(self):
        """Iniciar animación de dados - INFINITA HASTA ENTER"""
        if not self.dice_rolling:
            self.dice_rolling = True
            self.dice_start_time = pygame.time.get_ticks()
            self.dice_last_update = self.dice_start_time
            self.current_dice_frame = 0
            self.dice_can_stop = True
            self.game_state = "DICE_ROLL"
        
            current_player_obj = self.player1 if self.current_player == 1 else self.player2
            self.message = f"Turno de {current_player_obj.character}\nDados girando... Presiona ENTER para detener"
            self.message_timer = pygame.time.get_ticks()
    
    def stop_dice_roll(self):
        """Detener dados y mostrar resultado"""
        if self.dice_rolling and self.dice_can_stop:
            self.dice_rolling = False
            self.dice_can_stop = False
            
            dice1 = random.randint(1, 6)
            dice2 = random.randint(1, 6)
            self.dice_result = dice1 + dice2
            self.dice_result_time = pygame.time.get_ticks()
            
            current_player_obj = self.player1 if self.current_player == 1 else self.player2
            self.message = f"Turno de {current_player_obj.character}\nDados: {dice1} y {dice2} → Total {self.dice_result}"
            self.message_timer = pygame.time.get_ticks()
            
            self.moves_remaining = self.dice_result
            self.game_state = "MOVING"
    
    def update_dice_animation(self, dt):
        """Actualizar animación de dados - INFINITA HASTA ENTER"""
        if self.dice_rolling:
            now = pygame.time.get_ticks()
            
            # Cambiar frame del dado
            if now - self.dice_last_update > self.dice_roll_interval:
                self.current_dice_frame = (self.current_dice_frame + 1) % 6
                self.dice_last_update = now
            
            # NO terminar automáticamente - esperar a que el jugador presione ENTER
    
    def update_player_movement(self, dt):
        """Actualizar movimiento visual de jugadores"""
        # Player 1
        if self.player1_visual_pos != self.player1_target_pos:
            dx = self.player1_target_pos[0] - self.player1_visual_pos[0]
            dy = self.player1_target_pos[1] - self.player1_visual_pos[1]
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance > 2:
                move_distance = self.move_speed * dt
                self.player1_visual_pos[0] += (dx / distance) * move_distance
                self.player1_visual_pos[1] += (dy / distance) * move_distance
            else:
                self.player1_visual_pos = list(self.player1_target_pos)
        
        # Player 2
        if self.player2_visual_pos != self.player2_target_pos:
            dx = self.player2_target_pos[0] - self.player2_visual_pos[0]
            dy = self.player2_target_pos[1] - self.player2_visual_pos[1]
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance > 2:
                move_distance = self.move_speed * dt
                self.player2_visual_pos[0] += (dx / distance) * move_distance
                self.player2_visual_pos[1] += (dy / distance) * move_distance
            else:
                self.player2_visual_pos = list(self.player2_target_pos)
    
    def move_current_player(self):
        """Mover jugador actual una casilla"""
        if self.moves_remaining <= 0:
            return
        
        current_player_obj = self.player1 if self.current_player == 1 else self.player2
        
        # Verificar si hay bifurcación
        if len(current_player_obj.position.next_squares) > 1:
            self.choice_options = []
            for i, square in enumerate(current_player_obj.position.next_squares):
                self.choice_options.append((i, square.id))
            
            self.message = f"Selecciona el camino:\n"
            for i, square_id in self.choice_options:
                self.message += f"{i} → Casilla {square_id}\n"
            
            if self.current_player == 1:
                self.message += "Presiona A/D para elegir"
            else:
                if config.machine_mode:
                    # Bot elige automáticamente
                    choice = random.choice(range(len(self.choice_options)))
                    self.make_choice(choice)
                    return
                else:
                    self.message += "Presiona ←/→ para elegir"
            
            self.game_state = "CHOICE"
            self.message_timer = pygame.time.get_ticks()
            return
        
        # Mover a la siguiente casilla
        if current_player_obj.position.next_squares:
            next_square = current_player_obj.position.next_squares[0]
            current_player_obj.move_to(next_square)
            
            # Actualizar posición visual objetivo
            if self.current_player == 1:
                self.player1_target_pos = list(self.casillas[next_square.id])
            else:
                self.player2_target_pos = list(self.casillas[next_square.id])
            
            self.moves_remaining -= 1
            
            # Verificar si terminó el movimiento
            if self.moves_remaining <= 0:
                self.apply_square_effect(current_player_obj)
                self.end_turn()
    
    def make_choice(self, choice_index):
        """Hacer elección en bifurcación"""
        if choice_index < len(self.choice_options):
            current_player_obj = self.player1 if self.current_player == 1 else self.player2
            chosen_square = current_player_obj.position.next_squares[choice_index]
            current_player_obj.move_to(chosen_square)
            
            # Actualizar posición visual objetivo
            if self.current_player == 1:
                self.player1_target_pos = list(self.casillas[chosen_square.id])
            else:
                self.player2_target_pos = list(self.casillas[chosen_square.id])
            
            self.moves_remaining -= 1
            self.game_state = "MOVING"
            
            if self.moves_remaining <= 0:
                self.apply_square_effect(current_player_obj)
                self.end_turn()
    
    def apply_square_effect(self, player):
        """Aplicar efecto de la casilla usando la lógica exacta de square.py"""
        square = player.position
        
        # Usar el método effect de la casilla
        if square.type == "blue":
            self.message = "Casilla azul"
        elif square.type == "green":
            self.message = f"Casilla verde: {player.character} gana 3 de basura"
            player.collect_trash(3)
        elif square.type == "red":
            self.message = f"Oh no… ¡Casilla roja! {player.character} ha perdido 3 de basura."
            player.collect_trash(-3)
        elif square.type == "purple":
            dice = random.randint(1, 6)
            dicepurple = dice * 2
            self.message = f"¡Casilla morada! Dado bonus {dice} → +{dicepurple} de basura"
            player.collect_trash(dicepurple)
        
        # Verificar punto de reciclaje
        if square.recycle:
            player.try_recycle(self.recycle_timeout, silent_mode=True)
            self.message += f"\n¡{player.character} llegó a un Punto de Reciclaje!"
            if square.timeout == 0:
                if player.trash >= 20:
                    self.message += "\n¡Nueva insignia obtenida!"
                else:
                    self.message += f"\nNo tiene suficiente basura (necesita 20, tiene {player.trash})"
            else:
                self.message += "\nPunto de reciclaje ocupado!"
        
        self.message += f"\nInventario — Insignias: {player.badges} | Basura: {player.trash}"
        self.message_timer = pygame.time.get_ticks()
    
    def end_turn(self):
        """Terminar turno actual"""
        # Reducir timeout de puntos de reciclaje
        for point in self.recycling_points:
            if point.timeout > 0:
                point.timeout -= 1
        
        # Cambiar jugador
        self.current_player = 2 if self.current_player == 1 else 1
        
        # Verificar si terminó la ronda
        if self.current_player == 1:  # Volvió al jugador 1, terminó la ronda
            self.current_round += 1
            
            if self.current_round > self.rounds:
                self.end_game()
            else:
                self.start_minigame()
        else:
            self.game_state = "PLAYER_TURN"
    
    def start_minigame(self):
        """Iniciar minijuego aleatorio - SELECCIÓN ALEATORIA"""
        self.selected_minigame = random.choice(self.available_minigames)
        
        minigame_names = {
            "a_la_caneca": "A La Caneca",
            "cielo_en_crisis": "Cielo En Crisis", 
            "pesca_responsable": "Pesca Responsable"
        }
        
        self.message = f"¡Fin de la ronda {self.current_round - 1}!\nMinijuego: {minigame_names[self.selected_minigame]}\nPresiona ENTER para continuar"
        self.message_timer = pygame.time.get_ticks()
        self.game_state = "MINIGAME"
    
    def launch_minigame(self):
        """Lanzar el minijuego seleccionado como estado"""
        if self.selected_minigame == "a_la_caneca":
            from minigames.a_la_caneca import ALaCanecaState
            self.game.state_stack.append(ALaCanecaState(self.game))
        elif self.selected_minigame == "cielo_en_crisis":
            from minigames.cielo_en_crisis import CieloEnCrisisState
            self.game.state_stack.append(CieloEnCrisisState(self.game))
        elif self.selected_minigame == "pesca_responsable":
            from minigames.pesca_responsable import PescaResponsableState
            self.game.state_stack.append(PescaResponsableState(self.game))
        
        # El minijuego se ejecutará y cuando termine, volveremos automáticamente al tablero
        self.game_state = "PLAYER_TURN"
        self.message = f"¡Ronda {self.current_round}!"
        self.message_timer = pygame.time.get_ticks()
    
    def continue_after_minigame(self, player1_score, player2_score):
        """Continuar después del minijuego - SUMAR BASURA OBTENIDA"""
        # Sumar la basura obtenida en el minijuego
        self.player1.collect_trash(player1_score)
        self.player2.collect_trash(player2_score)
        
        # Continuar con la siguiente ronda
        self.game_state = "PLAYER_TURN"
        self.message = f"¡Ronda {self.current_round}!\n{self.player1.character} +{player1_score} basura\n{self.player2.character} +{player2_score} basura"
        self.message_timer = pygame.time.get_ticks()
    
    def end_game(self):
        """Terminar el juego"""
        self.game_state = "GAME_OVER"
        
        # Determinar ganador usando la lógica exacta de board_game.py
        if self.player1.badges > self.player2.badges:
            winner = f'{self.player1.character} gana la partida con más insignias que su oponente.'
        elif self.player2.badges > self.player1.badges:
            winner = f'{self.player2.character} gana la partida con más insignias que su oponente.'
        else:
            if self.player1.trash > self.player2.trash:
                winner = f'¡Qué duelo tan parejo!\nAmbos jugadores tienen la misma cantidad de insignias,\npero {self.player1.character} gana la partida gracias a su mayor esfuerzo recolectando basura.'
            elif self.player2.trash > self.player1.trash:
                winner = f'¡Qué duelo tan parejo!\nAmbos jugadores tienen la misma cantidad de insignias,\npero {self.player2.character} gana la partida gracias a su mayor esfuerzo recolectando basura.'
            else:
                winner = "¡Es un empate total! Ambos jugadores tienen las mismas insignias y basura."
        
        self.message = f"¡Fin del juego!\n\nResultados finales:\n{self.player1.character} — Insignias: {self.player1.badges} | Basura: {self.player1.trash}\n{self.player2.character} — Insignias: {self.player2.badges} | Basura: {self.player2.trash}\n\n{winner}\n\nPresiona ESC para salir"
        self.message_timer = pygame.time.get_ticks()
    
    def handle_event(self, event):
        if not self.can_handle_input or self.transitioning or self.transition.active:
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.game_state == "GAME_OVER":
                    self._start_transition(lambda: self.game.state_stack.pop())
                else:
                    # Confirmar salida durante el juego
                    self._start_transition(lambda: self.game.state_stack.pop())
            
            elif self.game_state == "PLAYER_TURN":
                # DADOS EMPIEZAN AUTOMÁTICAMENTE
                self.start_dice_roll()
            
            elif self.game_state == "DICE_ROLL":
                if event.key == pygame.K_RETURN and self.dice_can_stop:
                    # DETENER DADOS CON ENTER
                    self.stop_dice_roll()
            
            elif self.game_state == "MOVING":
                if event.key == pygame.K_RETURN:
                    self.move_current_player()
            
            elif self.game_state == "CHOICE":
                if self.current_player == 1:
                    if event.key == pygame.K_a:
                        self.make_choice(0)
                    elif event.key == pygame.K_d:
                        self.make_choice(1 if len(self.choice_options) > 1 else 0)
                else:
                    if not config.machine_mode:
                        if event.key == pygame.K_LEFT:
                            self.make_choice(0)
                        elif event.key == pygame.K_RIGHT:
                            self.make_choice(1 if len(self.choice_options) > 1 else 0)
            
            elif self.game_state == "MINIGAME":
                if event.key == pygame.K_RETURN:
                    self.launch_minigame()
    
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
        
        # Actualizar animación de dados
        self.update_dice_animation(dt)
        
        # Actualizar movimiento de jugadores
        self.update_player_movement(dt)
        
        # Auto-mover en estado MOVING
        if self.game_state == "MOVING" and self.moves_remaining > 0:
            # Auto-mover cada 0.5 segundos
            if pygame.time.get_ticks() - self.message_timer > 500:
                self.move_current_player()
        
        # Auto-iniciar dados en PLAYER_TURN después de un breve delay
        if self.game_state == "PLAYER_TURN":
            if pygame.time.get_ticks() - self.message_timer > 1000:  # 1 segundo de delay
                self.start_dice_roll()
    
    def render(self, screen):
        # Renderizar fondo Mapa.png
        self.background.render(screen)
        
        # Comentar estas líneas ya que el mapa de fondo ya muestra las casillas
        # # Dibujar puntos de reciclaje
        # for point in self.recycling_points:
        #     pos = self.casillas[point.id]
        #     color = GREEN if point.timeout == 0 else (100, 100, 100)
        #     pygame.draw.circle(screen, color, pos, 15)
        #     pygame.draw.circle(screen, WHITE, pos, 15, 2)
        
        # Dibujar indicadores sutiles de puntos de reciclaje (opcional)
        for point in self.recycling_points:
            pos = self.casillas[point.id]
            if point.timeout == 0:
                # Pequeño indicador verde disponible
                pygame.draw.circle(screen, GREEN, pos, 8)
                pygame.draw.circle(screen, WHITE, pos, 8, 2)
            else:
                # Pequeño indicador gris ocupado
                pygame.draw.circle(screen, (100, 100, 100), pos, 6)
        
        # Dibujar jugadores
        p1_rect = self.player1_img.get_rect(center=self.player1_visual_pos)
        p2_rect = self.player2_img.get_rect(center=self.player2_visual_pos)
        screen.blit(self.player1_img, p1_rect)
        screen.blit(self.player2_img, p2_rect)
        
        # Dibujar dados
        if self.dice_rolling or (self.dice_result and pygame.time.get_ticks() - self.dice_result_time < self.dice_result_display_time):
            dice_img = self.dice_images[self.current_dice_frame if self.dice_rolling else (self.dice_result - 1) % 6]
            dice_rect = dice_img.get_rect(center=(SCREEN_WIDTH // 2, 100))
            screen.blit(dice_img, dice_rect)
        
        # Dibujar información del juego
        self.draw_game_info(screen)
        
        # Dibujar mensaje
        self.draw_message(screen)
        
        # Renderizar transición
        self.transition.render(screen)
    
    def draw_game_info(self, screen):
        """Dibujar información del juego"""
        # Ronda actual
        round_text = self.font_title.render(f"RONDA {self.current_round}/{self.rounds}", True, WHITE)
        round_rect = round_text.get_rect(topright=(SCREEN_WIDTH - 20, 20))
        
        # Fondo para el texto
        bg_rect = pygame.Rect(round_rect.x - 10, round_rect.y - 5, round_rect.width + 20, round_rect.height + 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))
        screen.blit(bg_surface, bg_rect)
        screen.blit(round_text, round_rect)
        
        # Información de jugadores
        y_offset = 70
        
        # Player 1
        p1_info = f"{self.player1.character}: Insignias {self.player1.badges} | Basura {self.player1.trash}"
        p1_text = self.font_small.render(p1_info, True, WHITE)
        p1_rect = p1_text.get_rect(topright=(SCREEN_WIDTH - 20, y_offset))
        
        bg_rect = pygame.Rect(p1_rect.x - 10, p1_rect.y - 5, p1_rect.width + 20, p1_rect.height + 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0, 100, 0, 150) if self.current_player == 1 else (0, 0, 0, 150))
        screen.blit(bg_surface, bg_rect)
        screen.blit(p1_text, p1_rect)
        
        # Player 2
        y_offset += 30
        p2_info = f"{self.player2.character}: Insignias {self.player2.badges} | Basura {self.player2.trash}"
        p2_text = self.font_small.render(p2_info, True, WHITE)
        p2_rect = p2_text.get_rect(topright=(SCREEN_WIDTH - 20, y_offset))
        
        bg_rect = pygame.Rect(p2_rect.x - 10, p2_rect.y - 5, p2_rect.width + 20, p2_rect.height + 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0, 100, 0, 150) if self.current_player == 2 else (0, 0, 0, 150))
        screen.blit(bg_surface, bg_rect)
        screen.blit(p2_text, p2_rect)
        
        # Instrucciones según estado
        instructions = ""
        if self.game_state == "PLAYER_TURN":
            instructions = "Dados iniciando automáticamente..."
        elif self.game_state == "DICE_ROLL":
            instructions = "Presiona ENTER para detener dados" if self.dice_can_stop else "Dados girando..."
        elif self.game_state == "MOVING":
            instructions = f"Movimientos restantes: {self.moves_remaining} - ENTER para mover"
        elif self.game_state == "CHOICE":
            if self.current_player == 1:
                instructions = "A/D para elegir camino"
            else:
                instructions = "←/→ para elegir camino" if not config.machine_mode else "Bot eligiendo..."
        elif self.game_state == "MINIGAME":
            instructions = "ENTER para iniciar minijuego"
        elif self.game_state == "GAME_OVER":
            instructions = "ESC para salir"
        
        if instructions:
            inst_text = self.font_small.render(instructions, True, WHITE)
            inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
            
            bg_rect = pygame.Rect(inst_rect.x - 10, inst_rect.y - 5, inst_rect.width + 20, inst_rect.height + 10)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 150))
            screen.blit(bg_surface, bg_rect)
            screen.blit(inst_text, inst_rect)
    
    def draw_message(self, screen):
        """Dibujar mensaje principal"""
        if not self.message:
            return
        
        # Dividir mensaje en líneas
        lines = self.message.split('\n')
        
        # Calcular dimensiones del cuadro de mensaje
        line_height = 25
        max_width = 0
        
        rendered_lines = []
        for line in lines:
            if line.strip():  # Solo renderizar líneas no vacías
                text_surface = self.font_message.render(line, True, WHITE)
                rendered_lines.append(text_surface)
                max_width = max(max_width, text_surface.get_width())
        
        if not rendered_lines:
            return
        
        # Crear cuadro de mensaje
        box_width = max_width + 40
        box_height = len(rendered_lines) * line_height + 20
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = 150
        
        # Fondo del mensaje
        bg_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 200))
        screen.blit(bg_surface, (box_x, box_y))
        
        # Borde del mensaje
        pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height), 2)
        
        # Renderizar líneas
        for i, line_surface in enumerate(rendered_lines):
            line_rect = line_surface.get_rect(center=(SCREEN_WIDTH // 2, box_y + 20 + i * line_height))
            screen.blit(line_surface, line_rect)

print("BoardGameView - Juego completo con todas las mejoras solicitadas")
