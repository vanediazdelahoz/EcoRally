import random
from collections import defaultdict
import pickle
import os

class DynaQAgent:
    def __init__(self, train_mode=True, alpha=0.1, gamma=0.95, epsilon=0.1, planning_steps=5):
        # Modo de entrenamiento: True = aprende, False = solo actúa
        self.train_mode = train_mode

        # Q-table: Q[estado][accion] = valor
        self.Q = defaultdict(lambda: defaultdict(float))

        # Modelo del entorno para planeación: modelo[estado][accion] = (siguiente_estado, recompensa)
        self.model = defaultdict(dict)

        # Parámetros
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon if train_mode else 0.05  # Menor exploración en modo juego
        self.planning_steps = planning_steps
        
        # Historial para calcular recompensas
        self.last_state = None
        self.last_action = None
        self.last_trash = 0
        self.last_badges = 0
        
        # Contador de episodios para decaimiento de epsilon
        self.episode_count = 0
        self.min_epsilon = 0.01
        self.epsilon_decay = 0.995

    def encode_state(self, current_square, remaining_steps, trash, recycling_positions, badges, opponent_badges=0):
        """
        Representa el estado como una tupla discreta. Puede personalizarse más.
        """
        # Simplificar el estado para mejor generalización
        trash_level = min(trash // 5, 10)  # Agrupar basura en niveles de 5
        badge_diff = badges - opponent_badges  # Diferencia de insignias
        
        recycle_ids = tuple(sorted([sq.id for sq in recycling_positions if sq.recycle and sq.timeout == 0]))
        return (current_square.id, remaining_steps, trash_level, recycle_ids, badge_diff)

    def calculate_reward(self, player, opponent, recycling_points):
        """
        Calcula la recompensa basada en el cambio de estado
        """
        reward = 0
        
        # Recompensa por ganar insignias
        badge_gain = player.badges - self.last_badges
        if badge_gain > 0:
            reward += 100 * badge_gain  # Gran recompensa por insignias
        
        # Recompensa por recolectar basura (pero no demasiado)
        trash_gain = player.trash - self.last_trash
        if trash_gain > 0:
            reward += min(trash_gain * 2, 10)  # Limitado para evitar acumulación excesiva
        elif trash_gain < 0 and player.trash < 20:
            reward -= abs(trash_gain) * 3  # Penalizar pérdida de basura si está bajo
        
        # Recompensa por estar cerca de puntos de reciclaje con suficiente basura
        if player.trash >= 20:
            for rp in recycling_points:
                if rp.recycle and rp.timeout == 0:
                    distance = abs(player.position.id - rp.id)
                    if distance <= 6:
                        reward += 15 - distance * 2  # Más cerca = mejor recompensa
        
        # Penalizar si el oponente está ganando por mucho
        badge_diff = player.badges - opponent.badges
        if badge_diff < -1:
            reward -= 15
        elif badge_diff > 0:
            reward += 5 * badge_diff
        
        # Pequeña penalización por cada turno para fomentar eficiencia
        reward -= 1
        
        return reward

    def get_action(self, state, possible_actions):
        """
        Selecciona una acción usando política epsilon-greedy.
        """
        if self.train_mode and random.random() < self.epsilon:
            return random.choice(possible_actions)
        q_values = self.Q[state]
        
        # Si no hay valores Q para este estado, elegir aleatoriamente
        if not q_values:
            return random.choice(possible_actions)
        
        return max(possible_actions, key=lambda a: q_values[a])

    def update(self, state, action, next_state, reward, next_possible_actions):
        """
        Aprende solo si está en modo de entrenamiento.
        """
        if not self.train_mode:
            return

        # Actualización Q-learning
        max_q_next = max([self.Q[next_state][a] for a in next_possible_actions], default=0)
        self.Q[state][action] += self.alpha * (
            reward + self.gamma * max_q_next - self.Q[state][action]
        )

        # Guardar en el modelo para planificación
        self.model[state][action] = (next_state, reward)

        # Simulación de planificación (modelo)
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
        """
        Llamar al final de cada episodio para actualizar parámetros
        """
        if self.train_mode:
            self.episode_count += 1
            # Decaimiento de epsilon
            self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
            
            # Bonus por ganar
            if won and self.last_state is not None and self.last_action is not None:
                self.Q[self.last_state][self.last_action] += 50
            
            if self.episode_count % 100 == 0:
                print(f"Episodio {self.episode_count}, Epsilon: {self.epsilon:.3f}")

    def set_train_mode(self, train_mode):
        """
        Cambiar entre modo entrenamiento y juego
        """
        self.train_mode = train_mode
        if not train_mode:
            self.epsilon = 0.05  # Exploración mínima en modo juego
        else:
            self.epsilon = 0.1  # Exploración normal en entrenamiento

    def save_policy(self, filepath="agent_policy.pkl"):
        try:
            with open(filepath, "wb") as f:
                pickle.dump(dict(self.Q), f)
            print(f"✓ Política guardada en {filepath}")
        except Exception as e:
            print(f"✗ Error al guardar política: {e}")

    def load_policy(self, filepath="agent_policy.pkl"):
        try:
            with open(filepath, "rb") as f:
                loaded_q = pickle.load(f)
                self.Q = defaultdict(lambda: defaultdict(float), {
                    state: defaultdict(float, actions) for state, actions in loaded_q.items()
                })
            print(f"✓ Política cargada desde {filepath}")
            return True
        except FileNotFoundError:
            print(f"⚠️  No se encontró el archivo {filepath}")
            print("💡 Para entrenar el agente, ejecuta:")
            print("   python agent/train_agent.py")
            print("   O cambia MODO_ENTRENAMIENTO = True en board_game.py")
            return False
        except Exception as e:
            print(f"✗ Error al cargar política: {e}")
            return False
