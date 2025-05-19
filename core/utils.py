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