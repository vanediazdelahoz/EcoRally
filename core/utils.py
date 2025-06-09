# Funciones utilitarias para cargar recursos del juego

import pygame

def load_font(path, size):
    return pygame.font.Font(path, size)

def load_image(path, scale=1):
    image = pygame.image.load(path).convert_alpha()
    if scale != 1:
        new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
        image = pygame.transform.scale(image, new_size)
    return image

def load_sound(path):
    return pygame.mixer.Sound(path)


def get_character(id_character):
    if id_character == 0:
            frames = [
                pygame.image.load("./assets/images/characters/granny/granny1.png").convert_alpha(),
                pygame.image.load("./assets/images/characters/granny/granny7.png").convert_alpha(),
                pygame.image.load("./assets/images/characters/granny/granny9.png").convert_alpha()
            ]
    elif id_character == 1:
            frames = [
                pygame.image.load("./assets/images/characters/tinu_titi/tinu_titi1.png").convert_alpha(),
                pygame.image.load("./assets/images/characters/tinu_titi/tinu_titi5.png").convert_alpha(),
                pygame.image.load("./assets/images/characters/tinu_titi/tinu_titi7.png").convert_alpha()
            ]
    elif id_character == 2:
            frames = [
                pygame.image.load("./assets/images/characters/sofia/sofia1.png").convert_alpha(),
                pygame.image.load("./assets/images/characters/sofia/sofia7.png").convert_alpha(),
                pygame.image.load("./assets/images/characters/sofia/sofia9.png").convert_alpha()
            ]
    elif id_character == 3:
            frames = [
                pygame.image.load("./assets/images/characters/luis/luis1.png").convert_alpha(),
                pygame.image.load("./assets/images/characters/luis/luis2.png").convert_alpha(),
                pygame.image.load("./assets/images/characters/luis/luis3.png").convert_alpha()
            ]
    elif id_character == 4:
            frames = [
                "./assets/images/characters/granny/granny1.png",
                "./assets/images/characters/tinu_titi/tinu_titi1.png",
                "./assets/images/characters/sofia/sofia1.png",
                "./assets/images/characters/luis/luis1.png"
            ]

    else:
        print(f"Error: id_character {id_character} no reconocido. Usando personaje por defecto.")
        frames = [
            pygame.image.load("./assets/images/characters/granny/granny1.png").convert_alpha(),
            pygame.image.load("./assets/images/characters/granny/granny7.png").convert_alpha(),
            pygame.image.load("./assets/images/characters/granny/granny9.png").convert_alpha()
            ]
        
    return frames