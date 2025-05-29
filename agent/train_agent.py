import sys
import os
# Agregar el directorio padre al path para poder importar desde states/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dynaq_agent import DynaQAgent
from states.board_game import BoardGame

def train_agent(episodes=1000, save_interval=100):
    agent = DynaQAgent(train_mode=True)
    
    # Intentar cargar política previa si existe
    try:
        agent.load_policy("agent_policy.pkl")
        print("Política previa cargada. Continuando entrenamiento...")
    except:
        print("No se encontró política previa. Iniciando entrenamiento desde cero.")
    
    victorias = 0
    
    # Entrenar por muchas partidas sin frontend
    for i in range(episodes):
        if i % 50 == 0:  # Mostrar progreso cada 50 episodios
            print(f"Entrenando episodio {i+1}/{episodes}")
        
        # Usar silent_mode=True para entrenar más rápido
        won = BoardGame(use_agent=True, train_agent=True, agent=agent, silent_mode=True)
        if won:
            victorias += 1
        
        # Guardar política periódicamente
        if (i + 1) % save_interval == 0:
            agent.save_policy("agent_policy.pkl")
            tasa_victoria = (victorias / (i + 1)) * 100
            print(f"Progreso: {i+1}/{episodes} - Victorias: {tasa_victoria:.1f}%")

    # Guardar política final
    agent.save_policy("agent_policy.pkl")
    print(f"\n✅ ENTRENAMIENTO COMPLETADO")
    print(f"Tasa final de victorias: {(victorias/episodes)*100:.1f}%")
    print(f"Estados aprendidos: {len(agent.Q)}")
    return agent

def test_agent(episodes=5):
    """
    Prueba el agente entrenado sin aprendizaje
    """
    print("\nProbando agente entrenado...")
    agent = DynaQAgent(train_mode=False)
    
    # Cargar política entrenada
    if not agent.load_policy("agent_policy.pkl"):
        print("No se pudo cargar la política. Abortando pruebas.")
        return
    
    victorias = 0
    
    # Jugar episodios de prueba
    for i in range(episodes):
        print(f"\n--- Episodio de prueba {i+1}/{episodes} ---")
        won = BoardGame(use_agent=True, train_agent=False, agent=agent, silent_mode=False)
        if won:
            victorias += 1
    
    print(f"\n📊 RESULTADOS DE PRUEBA:")
    print(f"Victorias del agente: {victorias}/{episodes} ({(victorias/episodes)*100:.1f}%)")

if __name__ == "__main__":
    # Entrenar agente
    train_agent(episodes=1000, save_interval=50)
    
    # Probar agente
    test_agent(episodes=3)
