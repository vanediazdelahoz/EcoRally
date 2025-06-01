import random
from collections import defaultdict
import pickle
import os

class DynaQAgent:
    def __init__(self, train_mode=True, alpha=0.15, gamma=0.95, epsilon=0.3, planning_steps=20):

        # Modo de entrenamiento: True = aprende, False = solo actúa
        self.train_mode = train_mode

        # Q-table: Q[estado][accion] = valor
        self.Q = defaultdict(lambda: defaultdict(float))

        # Modelo del entorno para planeación: modelo[estado][accion] = (siguiente_estado, recompensa)
        self.model = defaultdict(dict)

        # Parámetros
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon if train_mode else 0.0
        self.planning_steps = planning_steps
        
        # Historial para calcular recompensas
        self.last_state = None
        self.last_action = None
        self.last_trash = 0
        self.last_badges = 0
        self.last_position_id = 0
        
        # Contador de episodios para decaimiento de epsilon
        self.episode_count = 0
        self.min_epsilon = 0.01
        self.epsilon_decay = 0.9995

    def encode_state(self, current_square, remaining_steps, trash, recycling_positions, badges, opponent_badges=0):

        # Fase estratégica basada en la cantidad de basura
        if trash < 20:
            strategic_phase = 0  # Fase de acumulación
            trash_level = min(trash // 3, 6)
        else:
            strategic_phase = 1  # Fase de reciclaje
            trash_level = min((trash - 20) // 5, 4) + 7
        
        # Diferencia de insignias (crítico para ganar)
        badge_diff = min(max(badges - opponent_badges, -3), 3)
        
        # Puntos de reciclaje activos
        active_recycle_points = [sq.id for sq in recycling_positions if sq.recycle and sq.timeout == 0]
        
        # Información de proximidad solo si está en fase de reciclaje
        if strategic_phase == 1 and active_recycle_points:
            # Encontrar el punto de reciclaje más cercano
            closest_rp_distance = min([abs(current_square.id - rp_id) for rp_id in active_recycle_points])
            
            # Discretizar distancia
            if closest_rp_distance <= 2:
                distance_category = 0  # Muy cerca
            elif closest_rp_distance <= 5:
                distance_category = 1  # Cerca
            elif closest_rp_distance <= 10:
                distance_category = 2  # Medio
            else:
                distance_category = 3  # Lejos
        else:
            distance_category = 4
        
        # Turnos restantes (importante para urgencia)
        turns_left = min(remaining_steps // 2, 5)
        
        return (current_square.id, strategic_phase, trash_level, badge_diff, distance_category, turns_left)

    def predict_path_outcome(self, current_square, path_choice, steps_ahead=3):

        if not current_square.next_squares or path_choice >= len(current_square.next_squares):
            return 0
        
        next_square = current_square.next_squares[path_choice]
        predicted_reward = 0
        current_pos = next_square
        
        # Simular algunos pasos adelante
        for step in range(min(steps_ahead, 3)):
            # Evaluar el efecto de la casilla actual
            if current_pos.type == "green":
                predicted_reward += 3  # Gana basura
            elif current_pos.type == "red":
                predicted_reward -= 3  # Pierde basura
            elif current_pos.type == "purple":
                predicted_reward += 7  # Promedio del dado bonus (1-6)*2
            # blue no hace nada
            
            # Avanzar al siguiente cuadro (tomar el primer camino disponible)
            if current_pos.next_squares:
                current_pos = current_pos.next_squares[0]
            else:
                break
        
        return predicted_reward

    def calculate_reward(self, player, opponent, recycling_points):

        reward = 0
        
        # RECOMPENSA MÁXIMA POR INSIGNIAS
        badge_gain = player.badges - self.last_badges
        if badge_gain > 0:
            reward += 300 * badge_gain  # Recompensa muy alta por insignias
        
        # RECOMPENSAS BASADAS EN LA FASE ESTRATÉGICA
        trash_gain = player.trash - self.last_trash
        
        # FASE 1: Acumulación de basura (< 20)
        if self.last_trash < 20:
            if trash_gain > 0:
                # Recompensa progresiva por acercarse a 20
                progress_bonus = 1 + (player.trash / 20)  # Más recompensa cerca de 20
                reward += trash_gain * progress_bonus * 3
            elif trash_gain < 0:
                # Penalización severa por perder basura en fase de acumulación
                penalty = abs(trash_gain) * 4
                if self.last_trash >= 15:  # Muy cerca de 20
                    penalty *= 2
                reward -= penalty
        
        # FASE 2: Búsqueda de reciclaje (≥ 20)
        else:
            if trash_gain > 0:
                # Recompensa moderada por ganar más basura
                reward += trash_gain * 1
            elif trash_gain < 0:
                # Penalización muy severa por perder basura cuando puede reciclar
                reward -= abs(trash_gain) * 8
        
        # RECOMPENSAS POR PROXIMIDAD ESTRATÉGICA
        if player.trash >= 20:
            # Buscar punto de reciclaje activo más cercano
            active_points = [rp for rp in recycling_points if rp.recycle and rp.timeout == 0]
            if active_points:
                current_distance = min([abs(player.position.id - rp.id) for rp in active_points])
                last_distance = min([abs(self.last_position_id - rp.id) for rp in active_points])
                
                # Recompensa por acercarse al punto de reciclaje
                if current_distance < last_distance:
                    reward += (last_distance - current_distance) * 15
                elif current_distance > last_distance:
                    # Penalización por alejarse
                    reward -= (current_distance - last_distance) * 10
                
                # Recompensa extra por estar muy cerca
                if current_distance <= 2:
                    reward += 25
                elif current_distance <= 5:
                    reward += 10
        
        # RECOMPENSAS COMPETITIVAS
        badge_diff = player.badges - opponent.badges
        if badge_diff > 0:
            reward += 15 * badge_diff
        elif badge_diff < 0:
            reward -= 20 * abs(badge_diff)
        
        # PENALIZACIÓN POR INEFICIENCIA
        reward -= 2  # Penalización base por turno
        
        # Actualizar posición para próxima evaluación
        self.last_position_id = player.position.id
        
        return reward

    def get_action(self, state, possible_actions):
 
        if self.train_mode and random.random() < self.epsilon:
            return random.choice(possible_actions)
        
        q_values = self.Q[state]
        
        # Si no hay valores Q, usar heurística simple
        if not q_values or all(q_values[a] == 0 for a in possible_actions):
            # Usar heurística basada en predicción de caminos
            if len(possible_actions) > 1:
                # Evaluar cada camino posible
                path_scores = []
                for action in possible_actions:
                    # Obtener información del estado actual
                    current_square_id = state[0]
                    strategic_phase = state[1]
                    trash_level = state[2]
                    
                    # Heurística simple: en fase de acumulación, preferir caminos que den basura
                    # En fase de reciclaje, preferir caminos hacia puntos de reciclaje
                    score = random.random()  # Base aleatoria
                    path_scores.append((action, score))
                
                # Elegir el mejor camino según heurística
                best_action = max(path_scores, key=lambda x: x[1])[0]
                return best_action
            else:
                return random.choice(possible_actions)
        
        # Usar valores Q aprendidos
        max_q = float('-inf')
        best_actions = []
        
        for action in possible_actions:
            q_val = q_values[action]
            if q_val > max_q:
                max_q = q_val
                best_actions = [action]
            elif q_val == max_q:
                best_actions.append(action)
        
        return random.choice(best_actions)

    def update(self, state, action, next_state, reward, next_possible_actions):

        if not self.train_mode:
            return

        # Actualización Q-learning
        max_q_next = max([self.Q[next_state][a] for a in next_possible_actions], default=0)
        self.Q[state][action] += self.alpha * (
            reward + self.gamma * max_q_next - self.Q[state][action]
        )

        # Guardar en el modelo para planificación
        self.model[state][action] = (next_state, reward)

        # Planificación Dyna-Q
        for _ in range(self.planning_steps):
            if not self.model:
                break
                
            s = random.choice(list(self.model.keys()))
            if not self.model[s]:
                continue
                
            a = random.choice(list(self.model[s].keys()))
            s_next, r = self.model[s][a]
            
            possible = list(self.Q[s_next].keys()) or next_possible_actions
            max_q_model = max([self.Q[s_next][a2] for a2 in possible], default=0)
            self.Q[s][a] += self.alpha * (r + self.gamma * max_q_model - self.Q[s][a])

    def end_episode(self, won=False):

        if self.train_mode:
            self.episode_count += 1
            self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
            
            # Recompensa extra por ganar
            if won and self.last_state is not None and self.last_action is not None:
                self.Q[self.last_state][self.last_action] += 150

    def set_train_mode(self, train_mode):

        self.train_mode = train_mode
        if not train_mode:
            self.epsilon = 0.0
        else:
            self.epsilon = 0.1

    def save_policy(self, filepath="agent_policy.pkl"):
        try:
            with open(filepath, "wb") as f:
                pickle.dump(dict(self.Q), f)
        except Exception as e:
            print(f"X Error al guardar política: {e}")

    def load_policy(self, filepath="agent_policy.pkl"):
        try:
            with open(filepath, "rb") as f:
                loaded_q = pickle.load(f)
                self.Q = defaultdict(lambda: defaultdict(float), {
                    state: defaultdict(float, actions) for state, actions in loaded_q.items()
                })
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"X Error al cargar política: {e}")
            return False