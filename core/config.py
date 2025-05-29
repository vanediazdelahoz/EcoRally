#core/config.py
# Configuración dinámica (personajes, volumen, dificultad)

class Config:
    def __init__(self):
        self.volume = 0.5
        self.sound_effects = True
        self.difficulty = "medium"  # easy, medium, hard
        self.characters = []  # Personajes seleccionados
        self.machine_mode = False
        self.agent = None  # Almacenará la instancia del agente
        
config = Config()