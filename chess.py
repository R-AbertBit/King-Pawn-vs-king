import pygame
import sys

# --- Configuración ---
TAM = 80
ANCHO = ALTO = 8 * TAM

BLANCO = (240, 217, 181)
NEGRO = (181, 136, 99)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Ajedrez Mini")
fuente = pygame.font.SysFont(None, 60)
reloj = pygame.time.Clock()

# --- Estado inicial ---
rey_blanco = [7, 4]
rey_negro = [0, 4]
peon = [1, 3]
coronado = False
turno_blanco = True

seleccionado = False
movs_legales = []

# --- Funciones auxiliares ---
def dentro(f, c):
    return 0 <= f < 8 and 0 <= c < 8

def adyacentes(a, b):
    return max(abs(a[0]-b[0]), abs(a[1]-b[1])) == 1

def posiciones_iguales(a, b):
    return a[0] == b[0] and a[1] == b[1]

def dibujar_tablero():
    for f in range(8):
        for c in range(8):
            color = BLANCO if (f + c) % 2 == 0 else NEGRO
            pygame.draw.rect(pantalla, color, (c * TAM, f * TAM, TAM, TAM))

def dibujar_piezas():
    # Peón o reina negra
    pieza_negra = "♛" if coronado else "♟"
    x, y = peon[1]*TAM + 20, peon[0]*TAM + 10
    render = fuente.render(pieza_negra, True, (0, 0, 0))
    pantalla.blit(render, (x, y))
    # Rey negro
    x, y = rey_negro[1]*TAM + 20, rey_negro[0]*TAM + 10
    render = fuente.render("♚", True, (0, 0, 0))
    pantalla.blit(render, (x, y))
    # Rey blanco
    x, y = rey_blanco[1]*TAM + 20, rey_blanco[0]*TAM + 10
    render = fuente.render("♔", True, (255, 255, 255))
    pantalla.blit(render, (x, y))

def es_casilla_libre(pos):
    return not (posiciones_iguales(pos, rey_blanco) or posiciones_iguales(pos, rey_negro) or posiciones_iguales(pos, peon))

def reina_ataca(pos, reina_pos):
    f, c = pos
    rf, rc = reina_pos
    if f == rf or c == rc or abs(f-rf) == abs(c-rc):
        # Para simplicidad, no se bloquea el ataque
        return True
    return False

def esta_en_jaque(pos):
    if coronado and reina_ataca(pos, peon):
        return True
    if not coronado:
        f, c = peon
        posibles_capturas = [[f+1, c-1], [f+1, c+1]]
        if pos in posibles_capturas:
            return True
    if adyacentes(pos, rey_negro):
        return True
    return False

def movimientos_legales_rey_blanco():
    movimientos = []
    for df in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if df == 0 and dc == 0:
                continue
            nf, nc = rey_blanco[0] + df, rey_blanco[1] + dc
            destino = [nf, nc]
            if not dentro(nf, nc):
                continue
            if adyacentes(destino, rey_negro):
                continue
            if posiciones_iguales(destino, rey_blanco):
                continue
            if posiciones_iguales(destino, peon) and adyacentes(peon, rey_negro):
                continue
            if esta_en_jaque(destino):
                continue
            movimientos.append(destino)
    return movimientos

def movimientos_peon():
    f, c = peon
    movs = []
    if dentro(f+1, c):
        adelante = [f+1, c]
        if es_casilla_libre(adelante):
            movs.append(adelante)
    for dc in [-1, 1]:
        nf, nc = f+1, c+dc
        if dentro(nf, nc) and posiciones_iguales([nf, nc], rey_blanco):
            movs.append([nf, nc])
    return movs

def movimientos_rey_negro():
    movs = []
    for df in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if df == 0 and dc == 0:
                continue
            nf, nc = rey_negro[0]+df, rey_negro[1]+dc
            destino = [nf, nc]
            if not dentro(nf, nc):
                continue
            if posiciones_iguales(destino, peon) or posiciones_iguales(destino, rey_blanco):
                continue
            if adyacentes(destino, rey_blanco):
                continue
            movs.append(destino)
    return movs

def computadora_mueve():
    global coronado, peon, rey_negro

    # Intentar mover peon primero si no coronado y movimiento seguro
    if not coronado:
        mov_peon = movimientos_peon()
        mov_peon_seguro = []
        for m in mov_peon:
            if adyacentes(m, rey_negro):
                mov_peon_seguro.append(m)
        if mov_peon_seguro:
            peon = mov_peon_seguro[0]
            if peon[0] == 7:
                coronado = True
            return
    # Mover rey negro para proteger peon o acercarse
    opciones = []
    dist_actual = abs(rey_negro[0]-peon[0]) + abs(rey_negro[1]-peon[1])
    for m in movimientos_rey_negro():
        dist_peon = abs(m[0]-peon[0]) + abs(m[1]-peon[1])
        if dist_peon <= dist_actual + 1:
            opciones.append((dist_peon, m))
    if opciones:
        opciones.sort(key=lambda x: x[0])
        rey_negro = opciones[0][1]

def juego_terminado():
    # Rey blanco captura peon (solo si no coronado y rey negro no protege)
    if posiciones_iguales(rey_blanco, peon) and not coronado:
        return "¡Rey blanco capturó el peón! ¡Gana jugador!"
    # Peon captura rey blanco
    if posiciones_iguales(peon, rey_blanco):
        return "¡Peón negro capturó al rey blanco! ¡Gana computadora!"
    # Rey negro captura rey blanco
    if posiciones_iguales(rey_negro, rey_blanco):
        return "¡Rey negro capturó al rey blanco! ¡Gana computadora!"
    # Reina ataca rey blanco
    if coronado and reina_ataca(rey_blanco, peon):
        return "¡Reina negra ataca al rey blanco! ¡Gana computadora!"
    return None

def dibujar_movimientos_legales(movs):
    for pos in movs:
        f, c = pos
        pygame.draw.rect(pantalla, VERDE, (c * TAM + 5, f * TAM + 5, TAM - 10, TAM - 10), 3)

# --- Bucle principal ---
while True:
    pantalla.fill((0, 0, 0))
    dibujar_tablero()
    dibujar_piezas()
    if seleccionado:
        dibujar_movimientos_legales(movs_legales)

    resultado = juego_terminado()
    if resultado:
        texto = fuente.render(resultado, True, ROJO)
        pantalla.blit(texto, (20, ALTO//2 - 30))
        pygame.display.flip()
        pygame.time.wait(4000)
        pygame.quit()
        sys.exit()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif evento.type == pygame.MOUSEBUTTONDOWN and turno_blanco:
            mx, my = pygame.mouse.get_pos()
            f, c = my // TAM, mx // TAM
            if not seleccionado:
                if posiciones_iguales([f, c], rey_blanco):
                    seleccionado = True
                    movs_legales = movimientos_legales_rey_blanco()
            else:
                if [f, c] in movs_legales:
                    rey_blanco = [f, c]
                    seleccionado = False
                    turno_blanco = False
                else:
                    seleccionado = False

    if not turno_blanco:
        computadora_mueve()
        turno_blanco = True

    pygame.display.flip()
    reloj.tick(30)