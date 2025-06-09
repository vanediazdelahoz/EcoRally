# Clase de configuración global

class Config:
    def __init__(self):
        self.volume = 0.5
        self.sound_effects = True
        self.characters = []
        self.machine_mode = False
        self.agent = None
        
config = Config()