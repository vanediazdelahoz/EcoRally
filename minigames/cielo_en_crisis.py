import pygame
import sys
import random
import time
from pathlib import Path

ruta = Path(__file__).parent

random_j1 = random.Random()
random_j2 = random.Random()

pygame.init()
ANCHO, ALTO = 800, 600
VENTANA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Lluvia de Basura")

NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
fuente = pygame.font.SysFont("consolas", 22)

fondo = pygame.image.load(
    str((ruta / ".." / "assets" / "CosasDeMinijuegos" / "FondoLluvia.png").resolve())
)
fondo = pygame.transform.scale(fondo, (ANCHO, ALTO))

caneca_img = pygame.image.load(
    str(
        (
            ruta
            / ".."
            / "assets"
            / "CosasDeMinijuegos"
            / "Canasta de basura"
            / "CanecaX.png"
        ).resolve()
    )
)
caneca_img = pygame.transform.scale(caneca_img, (100, 100))

tipos_basura = [
    {"nombre": "Aluminio", "img": "Aluminio.png", "puntos": 1},
    {"nombre": "Banano", "img": "Banano.png", "puntos": 1},
    {"nombre": "Botella", "img": "Botella.png", "puntos": 1},
    {"nombre": "Lata", "img": "Lata.png", "puntos": 1},
    {"nombre": "Manzana", "img": "Manzana.png", "puntos": 1},
    {"nombre": "Papel", "img": "Papel.png", "puntos": 1},
    {"nombre": "Pescado", "img": "Pescado.png", "puntos": 1},
    {"nombre": "Carton", "img": "Carton.png", "puntos": 1},
]
for basura in tipos_basura:
    imagen = pygame.image.load(
        str(
            (
                ruta / ".." / "assets" / "CosasDeMinijuegos" / "Basura" / basura["img"]
            ).resolve()
        )
    )
    # imagen = pygame.image.load(basura["img"]).convert_alpha()
    imagen = pygame.transform.scale(imagen, (40, 40))
    basura["superficie"] = imagen

jugador1_pos = pygame.Rect(ANCHO // 4 - 50, ALTO - 110, 100, 100)
jugador2_pos = pygame.Rect(3 * ANCHO // 4 - 50, ALTO - 110, 100, 100)
basura_jugador1 = []
basura_jugador2 = []
puntaje1 = 0
puntaje2 = 0
velocidad = 5
vel_bajada = 9

GENERAR_EVENTO_J1 = pygame.USEREVENT + 1
GENERAR_EVENTO_J2 = pygame.USEREVENT + 2
pygame.time.set_timer(GENERAR_EVENTO_J1, 600)
pygame.time.set_timer(GENERAR_EVENTO_J2, 600)

TIEMPO_JUEGO = 30
inicio_tiempo = time.time()
clock = pygame.time.Clock()

while True:
    clock.tick(60)
    tiempo_restante = max(0, int(TIEMPO_JUEGO - (time.time() - inicio_tiempo)))
    if tiempo_restante <= 0:
        break

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if evento.type == GENERAR_EVENTO_J1:
            tipo1 = random_j1.choice(tipos_basura)
            x1 = random_j1.randint(0, ANCHO // 2 - 40)
            basura_jugador1.append(
                {"rect": pygame.Rect(x1, -40, 40, 40), "tipo": tipo1}
            )

        if evento.type == GENERAR_EVENTO_J2:
            tipo2 = random_j2.choice(tipos_basura)
            x2 = random_j2.randint(ANCHO // 2, ANCHO - 40)
            basura_jugador2.append(
                {"rect": pygame.Rect(x2, -40, 40, 40), "tipo": tipo2}
            )

    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_a] and jugador1_pos.left > 0:
        jugador1_pos.x -= velocidad
    if teclas[pygame.K_d] and jugador1_pos.right < ANCHO // 2:
        jugador1_pos.x += velocidad
    if teclas[pygame.K_LEFT] and jugador2_pos.left > ANCHO // 2:
        jugador2_pos.x -= velocidad
    if teclas[pygame.K_RIGHT] and jugador2_pos.right < ANCHO:
        jugador2_pos.x += velocidad

    VENTANA.blit(fondo, (0, 0))
    pygame.draw.line(VENTANA, NEGRO, (ANCHO // 2, 0), (ANCHO // 2, ALTO), 2)

    for b in basura_jugador1[:]:
        b["rect"].y += vel_bajada - (tiempo_restante // 10)
        VENTANA.blit(b["tipo"]["superficie"], b["rect"])
        if b["rect"].colliderect(jugador1_pos):
            puntaje1 += b["tipo"]["puntos"]
            basura_jugador1.remove(b)
        elif b["rect"].y > ALTO:
            basura_jugador1.remove(b)

    for b in basura_jugador2[:]:
        b["rect"].y += vel_bajada - (tiempo_restante // 10)
        VENTANA.blit(b["tipo"]["superficie"], b["rect"])
        if b["rect"].colliderect(jugador2_pos):
            puntaje2 += b["tipo"]["puntos"]
            basura_jugador2.remove(b)
        elif b["rect"].y > ALTO:
            basura_jugador2.remove(b)

    VENTANA.blit(caneca_img, jugador1_pos)
    VENTANA.blit(caneca_img, jugador2_pos)

    texto1 = fuente.render(f"Jugador 1: {puntaje1}", True, BLANCO)
    texto2 = fuente.render(f"Jugador 2: {puntaje2}", True, BLANCO)
    VENTANA.blit(texto1, (20, 10))
    VENTANA.blit(texto2, (ANCHO - 220, 10))

    tiempo_rect = pygame.Rect(ANCHO // 2 - 40, 10, 80, 40)
    pygame.draw.rect(VENTANA, NEGRO, tiempo_rect)
    pygame.draw.rect(VENTANA, BLANCO, tiempo_rect, 2)
    tiempo_txt = fuente.render(str(tiempo_restante), True, BLANCO)
    txt_rect = tiempo_txt.get_rect(center=tiempo_rect.center)
    VENTANA.blit(tiempo_txt, txt_rect)

    pygame.display.flip()

# Pantalla final
VENTANA.blit(fondo, (0, 0))
pygame.draw.line(VENTANA, NEGRO, (ANCHO // 2, 0), (ANCHO // 2, ALTO), 2)
VENTANA.blit(caneca_img, jugador1_pos)
VENTANA.blit(caneca_img, jugador2_pos)

for b in basura_jugador1:
    VENTANA.blit(b["tipo"]["superficie"], b["rect"])
for b in basura_jugador2:
    VENTANA.blit(b["tipo"]["superficie"], b["rect"])

VENTANA.blit(fuente.render(f"Jugador 1: {puntaje1}", True, BLANCO), (20, 10))
VENTANA.blit(fuente.render(f"Jugador 2: {puntaje2}", True, BLANCO), (ANCHO - 220, 10))

tiempo_rect = pygame.Rect(ANCHO // 2 - 40, 10, 80, 40)
pygame.draw.rect(VENTANA, NEGRO, tiempo_rect)
pygame.draw.rect(VENTANA, BLANCO, tiempo_rect, 2)
VENTANA.blit(fuente.render("0", True, BLANCO), tiempo_rect.move(20, 5))

if puntaje1 > puntaje2:
    mensaje = "¡Felicidades Jugador 1, ganaste!"
elif puntaje2 > puntaje1:
    mensaje = "¡Felicidades Jugador 2, ganaste!"
else:
    mensaje = "¡Empate!"

cuadro = pygame.Rect(ANCHO // 2 - 250, ALTO // 2 - 100, 500, 200)
pygame.draw.rect(VENTANA, NEGRO, cuadro)
pygame.draw.rect(VENTANA, BLANCO, cuadro, 4)

VENTANA.blit(fuente.render(mensaje, True, BLANCO), (ANCHO // 2 - 200, ALTO // 2 - 30))
VENTANA.blit(
    fuente.render(f"Jugador 1: {puntaje1}   Jugador 2: {puntaje2}", True, BLANCO),
    (ANCHO // 2 - 200, ALTO // 2 + 30),
)

pygame.display.flip()

esperando = True
while esperando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            esperando = False

pygame.quit()
