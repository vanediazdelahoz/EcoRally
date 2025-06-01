# Funciones reutilizables (cargar imágenes, sonidos, etc.)

import pygame
import os

def load_font(path, size):
    try:
        return pygame.font.Font(path, size)
    except Exception as e:
        print(f"Error cargando fuente {path}: {e}. Usando fuente por defecto")
        return pygame.font.Font(None, size)

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
                pygame.image.load("assets/personajes/Abuelita/abuelita1.png").convert_alpha(),
                pygame.image.load("assets/personajes/Abuelita/abuelita7.png").convert_alpha(),
                pygame.image.load("assets/personajes/Abuelita/abuelita9.png").convert_alpha()
            ]
    elif id_character == 1:
            frames = [
                pygame.image.load("assets/personajes/IndigenaMono/IndioConMono1.png").convert_alpha(),
                pygame.image.load("assets/personajes/IndigenaMono/IndioConMono5.png").convert_alpha(),
                pygame.image.load("assets/personajes/IndigenaMono/IndioConMono7.png").convert_alpha()
            ]
    elif id_character == 2:
            frames = [
                pygame.image.load("assets/personajes/SillaDeRuedas/SillaDeRuedas1.png").convert_alpha(),
                pygame.image.load("assets/personajes/SillaDeRuedas/SillaDeRuedas7.png").convert_alpha(),
                pygame.image.load("assets/personajes/SillaDeRuedas/SillaDeRuedas9.png").convert_alpha()
            ]
    elif id_character == 3:
            frames = [
                pygame.image.load("assets/personajes/Luis/Luis1.png").convert_alpha(),
                pygame.image.load("assets/personajes/Luis/Luis2.png").convert_alpha(),
                pygame.image.load("assets/personajes/Luis/Luis3.png").convert_alpha()
            ]
    elif id_character == 4:
            frames = [
                "assets/personajes/Abuelita/abuelita1.png",
                "assets/personajes/IndigenaMono/IndioConMono1.png",
                "assets/personajes/SillaDeRuedas/SillaDeRuedas1.png",
                "assets/personajes/Luis/Luis1.png"
            ]

    else:
        print(f"Error: id_character {id_character} no reconocido. Usando personaje por defecto.")
        frames = [
            pygame.image.load("assets/personajes/Abuelita/abuelita1.png").convert_alpha(),
            pygame.image.load("assets/personajes/Abuelita/abuelita7.png").convert_alpha(),
            pygame.image.load("assets/personajes/Abuelita/abuelita9.png").convert_alpha()
            ]
        
    return frames