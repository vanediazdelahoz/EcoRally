# Script de animación de dados

import pygame
import random
from pathlib import Path

ruta = Path(__file__).parent

pygame.init()
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dados")

WHITE = (255, 255, 255)

FPS = 60
ROUND_TIME = 30
PLAYER_SIZE = 150
TRASH_SIZE = 40

background_img = pygame.image.load(
    str(
        (ruta / ".." / "assets" / "images" / "minigames" / "to_the_bin" / "background_to_the_bin.png").resolve()
    )
)
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))


def roll_dice_animation(two_dice=False, duration=1.5):
    dice_images = [
        pygame.image.load(
            str((ruta / ".." / "assets" / "images" / "map" / "dice" / f"dice{i}.png").resolve())
        )
        for i in range(1, 7)
    ]
    dice_images = [pygame.transform.scale(img, (100, 100)) for img in dice_images]

    start_time = pygame.time.get_ticks()
    roll_interval = 100

    while (pygame.time.get_ticks() - start_time) < duration * 1000:
        WIN.blit(background_img, (0, 0))

        if two_dice:
            img1 = random.choice(dice_images)
            img2 = random.choice(dice_images)
            WIN.blit(img1, (WIDTH // 2 - 120, HEIGHT // 2 - 50))
            WIN.blit(img2, (WIDTH // 2 + 20, HEIGHT // 2 - 50))
        else:
            img = random.choice(dice_images)
            WIN.blit(img, (WIDTH // 2 - 50, HEIGHT // 2 - 50))

        pygame.display.update()
        pygame.time.delay(roll_interval)

    WIN.blit(background_img, (0, 0))

    result1 = random.randint(0, 5)
    img1 = dice_images[result1]

    if two_dice:
        result2 = random.randint(0, 5)
        img2 = dice_images[result2]
        WIN.blit(img1, (WIDTH // 2 - 120, HEIGHT // 2 - 50))
        WIN.blit(img2, (WIDTH // 2 + 20, HEIGHT // 2 - 50))
    else:
        WIN.blit(img1, (WIDTH // 2 - 50, HEIGHT // 2 - 50))

    pygame.display.update()
    pygame.time.delay(1000)
    if two_dice:
        return result1 + 1, result2 + 1
    return result1 + 1

resultado = roll_dice_animation()
resultado1, resultado2 = roll_dice_animation(two_dice=True)
