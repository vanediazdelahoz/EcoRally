# Archivo principal de entrada del videojuego

import pygame
from core.game import Game


def main():
    pygame.init()
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
