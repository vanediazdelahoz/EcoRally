#!/usr/bin/env python3
import sys
import os
from pathlib import Path
import time
from collections import deque

# Agregar el directorio padre al path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from agent.dynaq_agent import DynaQAgent
from states.board_game import BoardGame

def show_progress_bar(current, total, prefix='Progreso', suffix='Completo', length=50):
    # Barra de progreso
    percent = (current / total) * 100
    filled_length = int(length * current // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent:.1f}% {suffix}', end='', flush=True)
    if current == total:
        print()

class TrainingReporter:
    # Reportes detallados del entrenamiento
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.recent_wins = deque(maxlen=100)
        
    def update(self, episode, won, agent):
        self.recent_wins.append(1 if won else 0)
    
    def generate_report(self, agent, total_episodes, total_time, total_wins):
        print(f"\n{'='*80}")
        print(f"📊 REPORTE COMPLETO DE ENTRENAMIENTO")
        print(f"{'='*80}")
        
        # Estadísticas generales
        win_rate = (total_wins / total_episodes) * 100
        eps_per_sec = total_episodes / total_time
        
        print(f"🎯 ESTADÍSTICAS GENERALES:")
        print(f"   ├─ Episodios totales: {total_episodes:,}")
        print(f"   ├─ Tiempo total: {total_time:.1f} segundos ({total_time/60:.1f} minutos)")
        print(f"   ├─ Velocidad: {eps_per_sec:.1f} episodios/segundo")
        print(f"   ├─ Victorias totales: {total_wins:,}")
        print(f"   └─ Tasa de victoria: {win_rate:.2f}%")
        
        # Estadísticas del agente
        print(f"\n🧠 PARÁMETROS DEL AGENTE:")
        print(f"   ├─ Alpha (aprendizaje): {agent.alpha}")
        print(f"   ├─ Gamma (descuento): {agent.gamma}")
        print(f"   ├─ Epsilon inicial: 0.4")
        print(f"   ├─ Epsilon actual: {agent.epsilon:.4f}")
        print(f"   ├─ Epsilon mínimo: {agent.min_epsilon}")
        print(f"   ├─ Decaimiento epsilon: {agent.epsilon_decay}")
        print(f"   └─ Pasos de planificación: {agent.planning_steps}")
        
        # Análisis del aprendizaje
        print(f"\n📈 ANÁLISIS DEL APRENDIZAJE:")
        print(f"   ├─ Estados totales aprendidos: {len(agent.Q):,}")
        print(f"   ├─ Transiciones en modelo: {sum(len(actions) for actions in agent.model.values()):,}")
        
        # Análisis de rendimiento reciente
        if len(self.recent_wins) >= 50:
            recent_50 = list(self.recent_wins)[-50:]
            recent_win_rate = sum(recent_50) / len(recent_50) * 100
            print(f"   ├─ Rendimiento últimas 50 partidas: {recent_win_rate:.1f}%")
            
            if len(self.recent_wins) >= 100:
                recent_100 = list(self.recent_wins)
                recent_win_rate_100 = sum(recent_100) / len(recent_100) * 100
                print(f"   └─ Rendimiento últimas 100 partidas: {recent_win_rate_100:.1f}%")
        
        # Evaluación del modelo
        print(f"\n🎖️  EVALUACIÓN DEL MODELO:")
        if win_rate >= 70:
            print(f"   🏆 EXCELENTE: El agente tiene un rendimiento superior")
        elif win_rate >= 60:
            print(f"   🥈 MUY BUENO: El agente muestra buen aprendizaje")
        elif win_rate >= 50:
            print(f"   🥉 BUENO: El agente está aprendiendo efectivamente")
        elif win_rate >= 40:
            print(f"   ⚠️  REGULAR: El agente necesita más entrenamiento")
        else:
            print(f"   ❌ DEFICIENTE: Revisar parámetros de entrenamiento")
        
        print(f"{'='*80}")
        
        return {
            'win_rate': win_rate,
            'total_episodes': total_episodes,
            'states_learned': len(agent.Q),
            'epsilon_final': agent.epsilon,
            'training_time': total_time
        }

def show_training_menu():
    # Menú de configuración de entrenamiento
    print(f"\n🤖 ENTRENAMIENTO DEL AGENTE")
    print(f"{'='*50}")
    print(f"1. Entrenamiento rápido (500 episodios)")
    print(f"2. Entrenamiento estándar (1500 episodios)")
    print(f"3. Entrenamiento intensivo (3000 episodios)")
    print(f"4. Configuración personalizada")
    print(f"5. Solo evaluar agente existente")
    print(f"6. Ver información del modelo")
    print(f"7. Volver al menú principal")
    print(f"{'='*50}")

def get_custom_config():
    # Obtiene configuración personalizada
    print(f"\n⚙️  CONFIGURACIÓN PERSONALIZADA")
    print(f"{'='*40}")
    
    while True:
        try:
            episodes = int(input("Número de episodios (100-10000): "))
            if 100 <= episodes <= 10000:
                break
            else:
                print("❌ Debe estar entre 100 y 10000")
        except ValueError:
            print("❌ Por favor ingresa un número válido")
    
    while True:
        try:
            save_interval = int(input(f"Guardar cada cuántos episodios (10-{episodes//2}): "))
            if 10 <= save_interval <= episodes//2:
                break
            else:
                print(f"❌ Debe estar entre 10 y {episodes//2}")
        except ValueError:
            print("❌ Por favor ingresa un número válido")
    
    return episodes, save_interval

def train_agent(episodes=1500, save_interval=100):
    # Entrena el agente DynaQ usando la lógica exacta de board_game.py
    model_path = "agent/agent_policy.pkl"
    
    print(f"\n🚀 INICIANDO ENTRENAMIENTO DEL AGENTE")
    print(f"{'='*60}")
    print(f"Episodios: {episodes:,}")
    print(f"Intervalo de guardado: cada {save_interval} episodios")
    print(f"Archivo del modelo: {model_path}")
    print(f"Oponente: Jugador aleatorio (Lulo)")
    print(f"{'='*60}\n")
    
    # Crear directorio agent si no existe
    os.makedirs("agent", exist_ok=True)
    
    # Parámetros optimizados para mejor rendimiento
    agent = DynaQAgent(
        train_mode=True,
        alpha=0.2,           # Tasa de aprendizaje
        gamma=0.99,          # Factor de descuento (visión a largo plazo)
        epsilon=0.4,         # Exploración inicial
        planning_steps=15    # Pasos de planificación
    )
    
    agent.min_epsilon = 0.01
    agent.epsilon_decay = 0.9998
    
    print(f"🧠 PARÁMETROS OPTIMIZADOS:")
    print(f"   ├─ Alpha (aprendizaje): {agent.alpha}")
    print(f"   ├─ Gamma (descuento): {agent.gamma}")
    print(f"   ├─ Epsilon inicial: {agent.epsilon}")
    print(f"   ├─ Epsilon mínimo: {agent.min_epsilon}")
    print(f"   ├─ Decaimiento epsilon: {agent.epsilon_decay}")
    print(f"   └─ Pasos planificación: {agent.planning_steps}")
    print()
    
    # Intentar cargar política previa
    if os.path.exists(model_path):
        if agent.load_policy(model_path):
            print("✅ Política previa cargada. Continuando entrenamiento...")
        else:
            print("⚠️ Error al cargar política previa. Iniciando desde cero.")
    else:
        print("💡 No se encontró política previa. Iniciando entrenamiento desde cero.")
    
    # Inicializar reporter
    reporter = TrainingReporter()
    
    # Estadísticas
    victorias = 0
    start_time = time.time()
    
    print(f"\n🎮 INICIANDO ENTRENAMIENTO...")
    print(f"🤖 El agente entrena contra oponente aleatorio")
    print(f"{'─'*60}")
    
    # Entrenar
    for episode in range(episodes):
        # Mostrar progreso cada 1% del total
        if episode % max(1, episodes // 100) == 0 or episode == episodes - 1:
            show_progress_bar(episode + 1, episodes, 'Entrenamiento')
        
        # USAR LA LÓGICA EXACTA DE BOARD_GAME.PY
        won = BoardGame(use_agent=True, train_agent=True, agent=agent, silent_mode=True)
        
        if won:
            victorias += 1
        
        # Actualizar reporter
        reporter.update(episode, won, agent)
        
        # Guardar periódicamente
        if (episode + 1) % save_interval == 0:
            agent.save_policy(model_path)
    
    # Asegurar que la barra llegue al 100%
    show_progress_bar(episodes, episodes, 'Entrenamiento')
    
    # Guardar final
    agent.save_policy(model_path)
    total_time = time.time() - start_time
    
    # Generar reporte
    reporter.generate_report(agent, episodes, total_time, victorias)
    
    return agent

def test_agent(episodes=10):
    model_path = "agent/agent_policy.pkl"
    
    print(f"\n🧪 EVALUACIÓN DEL AGENTE")
    print(f"{'='*40}")
    
    if not os.path.exists(model_path):
        print("❌ No se encontró el modelo entrenado")
        print("💡 Primero debes entrenar el agente")
        return
    
    agent = DynaQAgent(train_mode=False)
    if not agent.load_policy(model_path):
        print("❌ Error al cargar el modelo")
        return
    
    print(f"✅ Modelo cargado: {len(agent.Q):,} estados")
    print(f"🎯 Evaluando con {episodes} partidas...")
    print(f"{'─'*40}")
    
    victorias = 0
    
    for i in range(episodes):
        # Mostrar progreso de evaluación
        show_progress_bar(i + 1, episodes, 'Evaluación')
        
        won = BoardGame(use_agent=True, train_agent=False, agent=agent, silent_mode=True)
        
        if won:
            victorias += 1
    
    tasa_victoria = (victorias / episodes) * 100
    
    print(f"\n📊 RESULTADOS:")
    print(f"   ├─ Victorias: {victorias}/{episodes}")
    print(f"   └─ Tasa de victoria: {tasa_victoria:.1f}%")
    
    if tasa_victoria >= 70:
        print(f"🌟 RENDIMIENTO: EXCELENTE")
    elif tasa_victoria >= 60:
        print(f"🥇 RENDIMIENTO: MUY BUENO")
    elif tasa_victoria >= 50:
        print(f"🥈 RENDIMIENTO: BUENO")
    else:
        print(f"⚠️ RENDIMIENTO: NECESITA MEJORA")

def show_model_info():
    """Muestra información del modelo"""
    model_path = "agent/agent_policy.pkl"
    
    print(f"\n📊 INFORMACIÓN DEL MODELO")
    print(f"{'='*40}")
    
    if not os.path.exists(model_path):
        print("❌ No se encontró el modelo")
        return
    
    agent = DynaQAgent(train_mode=False)
    if agent.load_policy(model_path):
        print(f"✅ Modelo cargado correctamente")
        print(f"📈 Estados aprendidos: {len(agent.Q):,}")
        print(f"📁 Tamaño del archivo: {os.path.getsize(model_path):,} bytes")
        print(f"🧠 Parámetros:")
        print(f"   ├─ Alpha: {agent.alpha}")
        print(f"   ├─ Gamma: {agent.gamma}")
        print(f"   ├─ Epsilon: {agent.epsilon}")
        print(f"   └─ Planning steps: {agent.planning_steps}")
    else:
        print("❌ Error al cargar el modelo")

def main():
    """Función principal con menú interactivo"""
    while True:
        show_training_menu()
        
        try:
            choice = input("\nSelecciona una opción (1-7): ").strip()
            
            if choice == "1":
                print("\n⚡ ENTRENAMIENTO RÁPIDO")
                train_agent(episodes=500, save_interval=50)
                
            elif choice == "2":
                print("\n📈 ENTRENAMIENTO ESTÁNDAR")
                train_agent(episodes=1500, save_interval=100)
                
            elif choice == "3":
                print("\n🎯 ENTRENAMIENTO INTENSIVO")
                train_agent(episodes=3000, save_interval=150)
                
            elif choice == "4":
                episodes, save_interval = get_custom_config()
                print(f"\n⚙️  ENTRENAMIENTO PERSONALIZADO")
                train_agent(episodes=episodes, save_interval=save_interval)
                
            elif choice == "5":
                test_agent(episodes=10)
                
            elif choice == "6":
                show_model_info()
                
            elif choice == "7":
                print("\n👋 Volviendo al menú principal...")
                break
                
            else:
                print("❌ Opción inválida")
                
            # Preguntar si quiere continuar después del entrenamiento
            if choice in ["1", "2", "3", "4"]:
                print(f"\n¿Quieres evaluar el agente entrenado? (s/n): ", end="")
                response = input().strip().lower()
                if response.startswith('s'):
                    test_agent()
                    
        except KeyboardInterrupt:
            print(f"\n\n⏹️  Operación cancelada")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()