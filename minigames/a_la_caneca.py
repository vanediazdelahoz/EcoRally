import pygame
import random
import sys
from pathlib import Path

ruta = Path(__file__).parent

pygame.init()
ANCHO, ALTO = 1200, 600
VENTANA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Clasifica la Basura - Planta de Reciclaje")

BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
fuente = pygame.font.SysFont("consolas", 24)
fuente_final = pygame.font.SysFont("consolas", 48)

# Fondo nuevo
fondo = pygame.image.load(
    str(
        (ruta / ".." / "assets" / "CosasDeMinijuegos" / "FondoClasificar.png").resolve()
    )
)
fondo = pygame.transform.scale(fondo, (ANCHO, ALTO))

# Canecas
canecaB = pygame.transform.scale(
    pygame.image.load(
        str(
            (
                ruta
                / ".."
                / "assets"
                / "CosasDeMinijuegos"
                / "Canasta de basura"
                / "CanecaB.png"
            ).resolve()
        )
    ),
    (100, 100),
)
canecaV = pygame.transform.scale(
    pygame.image.load(
        str(
            (
                ruta
                / ".."
                / "assets"
                / "CosasDeMinijuegos"
                / "Canasta de basura"
                / "CanecaV.png"
            ).resolve()
        )
    ),
    (100, 100),
)
canecaN = pygame.transform.scale(
    pygame.image.load(
        str(
            (
                ruta
                / ".."
                / "assets"
                / "CosasDeMinijuegos"
                / "Canasta de basura"
                / "CanecaN.png"
            ).resolve()
        )
    ),
    (100, 100),
)

canecas_j1 = {"negra": (100, 450), "blanca": (250, 450), "verde": (400, 450)}
canecas_j2 = {"negra": (700, 450), "blanca": (850, 450), "verde": (1000, 450)}

clasificacion = {
    "Botella.png": "blanca",
    "Lata.png": "blanca",
    "Papel.png": "blanca",
    "Carton.png": "blanca",
    "Aluminio.png": "negra",
    "Banano.png": "verde",
    "Manzana.png": "verde",
    "Pescado.png": "verde",
}

nombres = list(clasificacion.keys())
imagenes = {
    n: pygame.transform.scale(
        pygame.image.load(
            str((ruta / ".." / "assets" / "CosasDeMinijuegos" / "Basura" / n).resolve())
        ),
        (80, 80),
    )
    for n in nombres
}


puntaje1, puntaje2 = 0, 0
tiempo_limite = 30
clock = pygame.time.Clock()
inicio = pygame.time.get_ticks()

basura_j1 = random.choice(nombres)
basura_j2 = random.choice(nombres)


def dibujar():
    VENTANA.blit(fondo, (0, 0))

    # Tapar la línea negra con un color oscuro para disimularla
    pygame.draw.rect(VENTANA, (30, 30, 40), (ANCHO // 2 - 1, 0, 3, ALTO))

    for tipo, pos in canecas_j1.items():
        VENTANA.blit(eval("caneca" + tipo[0].upper()), pos)
    for tipo, pos in canecas_j2.items():
        VENTANA.blit(eval("caneca" + tipo[0].upper()), pos)

    # Posición sobre las pantallas del fondo
    VENTANA.blit(imagenes[basura_j1], (ANCHO // 4 - 40, 200))
    VENTANA.blit(imagenes[basura_j2], ((3 * ANCHO) // 4 - 40, 200))

    tiempo = max(0, tiempo_limite - (pygame.time.get_ticks() - inicio) // 1000)

    VENTANA.blit(fuente.render(f"P1: {puntaje1}", True, BLANCO), (30, 20))
    VENTANA.blit(fuente.render(f"P2: {puntaje2}", True, BLANCO), (ANCHO - 200, 20))

    pygame.draw.rect(VENTANA, NEGRO, (ANCHO // 2 - 40, 15, 80, 35))
    tiempo_txt = fuente.render(f"{tiempo}", True, BLANCO)
    VENTANA.blit(tiempo_txt, (ANCHO // 2 - tiempo_txt.get_width() // 2, 20))

    return tiempo


def nueva_basura(jugador):
    if jugador == 1:
        global basura_j1
        basura_j1 = random.choice(nombres)
    else:
        global basura_j2
        basura_j2 = random.choice(nombres)


def mostrar_overlay_ganador():
    mensaje = ""
    if puntaje1 > puntaje2:
        mensaje = "¡Felicidades Jugador 1, ganaste!"
    elif puntaje2 > puntaje1:
        mensaje = "¡Felicidades Jugador 2, ganaste!"
    else:
        mensaje = "¡Empate!"

    cuadro = pygame.Rect(ANCHO // 2 - 250, ALTO // 2 - 100, 500, 200)
    pygame.draw.rect(VENTANA, NEGRO, cuadro)
    pygame.draw.rect(VENTANA, BLANCO, cuadro, 4)

    VENTANA.blit(fuente.render(mensaje, True, BLANCO), (cuadro.x + 50, cuadro.y + 50))
    marcador = f"Jugador 1: {puntaje1}   Jugador 2: {puntaje2}"
    VENTANA.blit(fuente.render(marcador, True, BLANCO), (cuadro.x + 50, cuadro.y + 100))

    pygame.display.flip()
    pygame.time.delay(5000)


# Bucle principal
ejecutando = True
while ejecutando:
    clock.tick(60)
    tiempo = dibujar()
    pygame.display.flip()

    if tiempo == 0:
        mostrar_overlay_ganador()
        break

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif evento.type == pygame.KEYDOWN:
            correcta_j1 = clasificacion[basura_j1]
            correcta_j2 = clasificacion[basura_j2]

            if evento.key == pygame.K_w:
                puntaje1 += 1 if correcta_j1 == "blanca" else -1
                nueva_basura(1)
            elif evento.key == pygame.K_a:
                puntaje1 += 1 if correcta_j1 == "negra" else -1
                nueva_basura(1)
            elif evento.key == pygame.K_d:
                puntaje1 += 1 if correcta_j1 == "verde" else -1
                nueva_basura(1)

            elif evento.key == pygame.K_UP:
                puntaje2 += 1 if correcta_j2 == "blanca" else -1
                nueva_basura(2)
            elif evento.key == pygame.K_LEFT:
                puntaje2 += 1 if correcta_j2 == "negra" else -1
                nueva_basura(2)
            elif evento.key == pygame.K_RIGHT:
                puntaje2 += 1 if correcta_j2 == "verde" else -1
                nueva_basura(2)

pygame.quit()
