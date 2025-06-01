import pygame
import random
import sys
from pathlib import Path

ruta = Path(__file__).parent

# Inicializar Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pesca Responsable")

# Colores
NEGRO = (0, 0, 0)
fuente = pygame.font.SysFont("consolas", 22)
WHITE = (255, 255, 255)
TOP_MARGIN = 250
TRASH_LIMIT_BOTTOM = HEIGHT - 50  # Límite visual inferior (fondo de tierra)

# Configuración del juego
FPS = 60
ROUND_TIME = 30  # segundos
PLAYER_SIZE = 150
TRASH_SIZE = 40

# Cargar imagen de fondo
background_img = pygame.image.load(
    str((ruta / ".." / "assets" / "CosasDeMinijuegos" / "FondoPesca.jpg").resolve())
)
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

BARCO1_IMAGE = pygame.image.load(
    str(
        (
            ruta
            / ".."
            / "assets"
            / "CosasDeMinijuegos"
            / "Barco"
            / "Barco Izquierda.png"
        ).resolve()
    )
)
BARCO2_IMAGE = pygame.image.load(
    str(
        (
            ruta / ".." / "assets" / "CosasDeMinijuegos" / "Barco" / "Barco Derecha.png"
        ).resolve()
    )
)

# Escalar barcos (ajusta el tamaño según tus imágenes)
BARCO1_IMAGE = pygame.transform.scale(BARCO1_IMAGE, (200, 200))
BARCO2_IMAGE = pygame.transform.scale(BARCO2_IMAGE, (200, 200))

# Posiciones fijas de los barcos (sobre el área acuática)
BARCO1_POS = (80, TOP_MARGIN - 160)  # barco de izquierda
BARCO2_POS = (WIDTH - 280, TOP_MARGIN - 160)  # barco de derecha

# Cargar assets de basura y jugadores
ALUMINIO_IMAGE = pygame.image.load(
    str(
        (
            ruta / ".." / "assets" / "CosasDeMinijuegos" / "Basura" / "Aluminio.png"
        ).resolve()
    )
)
BOTELLA_IMAGE = pygame.image.load(
    str(
        (
            ruta / ".." / "assets" / "CosasDeMinijuegos" / "Basura" / "Botella.png"
        ).resolve()
    )
)
LATA_IMAGE = pygame.image.load(
    str(
        (ruta / ".." / "assets" / "CosasDeMinijuegos" / "Basura" / "Lata.png").resolve()
    )
)
PLAYER1_IMAGE = pygame.image.load(
    str(
        (
            ruta
            / ".."
            / "assets"
            / "CosasDeMinijuegos"
            / "Barco"
            / "Cebo Izquierda.png"
        ).resolve()
    )
)
PLAYER2_IMAGE = pygame.image.load(
    str(
        (
            ruta / ".." / "assets" / "CosasDeMinijuegos" / "Barco" / "Cebo Derecha.png"
        ).resolve()
    )
)

# Escalar imágenes
ALL_TRASH_IMAGES = [
    pygame.transform.scale(ALUMINIO_IMAGE, (TRASH_SIZE, TRASH_SIZE)),
    pygame.transform.scale(BOTELLA_IMAGE, (TRASH_SIZE, TRASH_SIZE)),
    pygame.transform.scale(LATA_IMAGE, (TRASH_SIZE, TRASH_SIZE)),
]
PLAYER1_IMAGE = pygame.transform.scale(PLAYER1_IMAGE, (PLAYER_SIZE, PLAYER_SIZE))
PLAYER2_IMAGE = pygame.transform.scale(PLAYER2_IMAGE, (PLAYER_SIZE, PLAYER_SIZE))

# Jugadores
players = [
    {
        "rect": pygame.Rect(
            BARCO1_POS[0] + 100,  # Centrado respecto al barco
            BARCO1_POS[1] + 120,  # Justo debajo del barco
            PLAYER_SIZE / 2,
            PLAYER_SIZE / 2,
        ),
        "score": 0,
        "image": PLAYER1_IMAGE,
        "keys": {
            "up": pygame.K_w,
            "down": pygame.K_s,
            "left": pygame.K_a,
            "right": pygame.K_d,
        },
    },
    {
        "rect": pygame.Rect(
            BARCO2_POS[0] - 50,
            BARCO2_POS[1] + 120,
            PLAYER_SIZE / 2,
            PLAYER_SIZE / 2,
        ),
        "score": 0,
        "image": PLAYER2_IMAGE,
        "keys": {
            "up": pygame.K_UP,
            "down": pygame.K_DOWN,
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
        },
    },
]


trash_list = []


def spawn_trash():
    direction = random.choice(["left", "right"])
    y = random.randint(TOP_MARGIN, TRASH_LIMIT_BOTTOM - TRASH_SIZE)
    image = random.choice(ALL_TRASH_IMAGES)

    if direction == "right":
        x = WIDTH + random.randint(0, 100)
        speed = -3
    else:
        x = -TRASH_SIZE - random.randint(0, 100)
        speed = 3

    rect = pygame.Rect(x, y, TRASH_SIZE, TRASH_SIZE)
    trash_list.append({"rect": rect, "image": image, "speed": speed})


def move_objects(obj_list):
    for obj in obj_list:
        obj["rect"].x += obj["speed"]


def draw_window(time_left):
    WIN.blit(background_img, (0, 0))

    # Dibujar los barcos antes que los jugadores y la basura
    WIN.blit(BARCO1_IMAGE, BARCO1_POS)
    WIN.blit(BARCO2_IMAGE, BARCO2_POS)

    # Dibujar jugadores
    for player in players:
        WIN.blit(player["image"], player["rect"])

    # Dibujar basura
    for trash in trash_list:
        WIN.blit(trash["image"], trash["rect"])

    font = pygame.font.SysFont("consolas", 22)

    # Puntaje jugador 1 (esquina izquierda)
    texto1 = font.render(f"Jugador 1: {players[0]['score']}", True, WHITE)
    WIN.blit(texto1, (20, 10))

    # Puntaje jugador 2 (esquina derecha)
    texto2 = font.render(f"Jugador 2: {players[1]['score']}", True, WHITE)
    texto2_rect = texto2.get_rect(topright=(WIDTH - 20, 10))
    WIN.blit(texto2, texto2_rect)

    # Cronómetro (centro superior, con fondo negro y borde blanco)
    tiempo_rect = pygame.Rect(WIDTH // 2 - 40, 10, 80, 40)
    pygame.draw.rect(WIN, NEGRO, tiempo_rect)
    pygame.draw.rect(WIN, WHITE, tiempo_rect, 2)
    tiempo_txt = font.render(str(int(time_left)), True, WHITE)
    txt_rect = tiempo_txt.get_rect(center=tiempo_rect.center)
    WIN.blit(tiempo_txt, txt_rect)

    pygame.display.update()


def handle_player_input(player, keys_pressed):
    speed = 4
    if keys_pressed[player["keys"]["up"]]:
        player["rect"].y -= speed
    if keys_pressed[player["keys"]["down"]]:
        player["rect"].y += speed
    if keys_pressed[player["keys"]["left"]]:
        player["rect"].x -= speed
    if keys_pressed[player["keys"]["right"]]:
        player["rect"].x += speed

    # Limitar al área acuática
    player["rect"].clamp_ip(
        pygame.Rect(
            0,
            TOP_MARGIN - player["rect"].height / 2,
            WIDTH,
            TRASH_LIMIT_BOTTOM - (TOP_MARGIN - player["rect"].height),
        )
    )


def check_collisions():
    for player in players:
        for trash in trash_list[:]:
            if player["rect"].colliderect(trash["rect"]):
                player["score"] += 1
                trash_list.remove(trash)


def end_game():
    WIN.blit(background_img, (0, 0))
    WIN.blit(BARCO1_IMAGE, BARCO1_POS)
    WIN.blit(BARCO2_IMAGE, BARCO2_POS)
    for player in players:
        WIN.blit(player["image"], player["rect"])
    for trash in trash_list:
        WIN.blit(trash["image"], trash["rect"])

    # Puntajes
    WIN.blit(fuente.render(f"Jugador 1: {players[0]['score']}", True, WHITE), (20, 10))
    WIN.blit(
        fuente.render(f"Jugador 2: {players[1]['score']}", True, WHITE),
        (WIDTH - 220, 10),
    )

    # Cronómetro en 0
    tiempo_rect = pygame.Rect(WIDTH // 2 - 40, 10, 80, 40)
    pygame.draw.rect(WIN, NEGRO, tiempo_rect)
    pygame.draw.rect(WIN, WHITE, tiempo_rect, 2)
    WIN.blit(fuente.render("0", True, WHITE), tiempo_rect.move(20, 5))

    # Mensaje de fin
    s1 = players[0]["score"]
    s2 = players[1]["score"]
    if s1 > s2:
        mensaje = "¡Felicidades Jugador 1, ganaste!"
    elif s2 > s1:
        mensaje = "¡Felicidades Jugador 2, ganaste!"
    else:
        mensaje = "¡Empate!"

    cuadro = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 - 100, 500, 200)
    pygame.draw.rect(WIN, NEGRO, cuadro)
    pygame.draw.rect(WIN, WHITE, cuadro, 4)

    WIN.blit(fuente.render(mensaje, True, WHITE), (WIDTH // 2 - 200, HEIGHT // 2 - 30))
    resumen = f"Jugador 1: {s1}   Jugador 2: {s2}"
    WIN.blit(fuente.render(resumen, True, WHITE), (WIDTH // 2 - 200, HEIGHT // 2 + 30))

    pygame.display.flip()

    # Esperar cierre
    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                esperando = False


def main():
    clock = pygame.time.Clock()
    run = True
    start_ticks = pygame.time.get_ticks()

    while run:
        clock.tick(FPS)
        keys_pressed = pygame.key.get_pressed()
        elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000
        time_left = ROUND_TIME - elapsed_time

        if time_left <= 0:
            end_game()
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        for player in players:
            handle_player_input(player, keys_pressed)

        spawn_trash()

        move_objects(trash_list)
        trash_list[:] = [t for t in trash_list if -TRASH_SIZE <= t["rect"].x <= WIDTH]

        check_collisions()
        draw_window(time_left)

    pygame.quit()


if __name__ == "__main__":
    main()
