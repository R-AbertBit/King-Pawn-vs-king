import pygame
import sys

# --- Configuration ---
TAM = 80  # Size of each square on the board
WIDTH = HEIGHT = 8 * TAM  # Board is 8x8 squares

# Colors for the board and highlights
WHITE = (240, 217, 181)
BLACK = (181, 136, 99)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

pygame.init()

# Load piece images
img_pawn = pygame.image.load("images/black-pawn.png")
img_queen = pygame.image.load("images/black-queen.png")
img_white_king = pygame.image.load("images/white-king.png")
img_black_king = pygame.image.load("images/black-king.png")

# Resize images to fit the board squares
img_pawn = pygame.transform.scale(img_pawn, (TAM, TAM))
img_queen = pygame.transform.scale(img_queen, (TAM, TAM))
img_white_king = pygame.transform.scale(img_white_king, (TAM, TAM))
img_black_king = pygame.transform.scale(img_black_king, (TAM, TAM))

# Set up the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Chess")
font = pygame.font.SysFont(None, 60)
clock = pygame.time.Clock()

# --- Initial Game State ---
white_king = [7, 4]
black_king = [0, 4]
pawn = [1, 3]
promoted = False
white_turn = True

selected = False
legal_moves = []

# --- Helper Functions ---

def inside_board(r, c):
    return 0 <= r < 8 and 0 <= c < 8

def adjacent(a, b):
    return max(abs(a[0]-b[0]), abs(a[1]-b[1])) == 1

def same_position(a, b):
    return a[0] == b[0] and a[1] == b[1]

def draw_board():
    for r in range(8):
        for c in range(8):
            color = WHITE if (r + c) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, (c * TAM, r * TAM, TAM, TAM))

def draw_pieces():
    image = img_queen if promoted else img_pawn
    screen.blit(image, (pawn[1] * TAM, pawn[0] * TAM))
    screen.blit(img_black_king, (black_king[1] * TAM, black_king[0] * TAM))
    screen.blit(img_white_king, (white_king[1] * TAM, white_king[0] * TAM))

def is_square_free(pos):
    return not (same_position(pos, white_king) or same_position(pos, black_king) or same_position(pos, pawn))

def queen_attacks(pos, queen_pos):
    r, c = pos
    qr, qc = queen_pos
    if r == qr or c == qc or abs(r - qr) == abs(c - qc):
        return True
    return False

def is_in_check(pos):
    if promoted and queen_attacks(pos, pawn):
        return True
    if not promoted:
        r, c = pawn
        possible_captures = [[r+1, c-1], [r+1, c+1]]
        if pos in possible_captures:
            return True
    if adjacent(pos, black_king):
        return True
    return False

def white_king_legal_moves():
    moves = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = white_king[0] + dr, white_king[1] + dc
            dest = [nr, nc]
            if not inside_board(nr, nc):
                continue
            if adjacent(dest, black_king):
                continue
            if same_position(dest, white_king):
                continue
            if same_position(dest, pawn) and adjacent(pawn, black_king):
                continue
            if is_in_check(dest):
                continue
            moves.append(dest)
    return moves

def pawn_moves():
    r, c = pawn
    moves = []
    if inside_board(r+1, c):
        forward = [r+1, c]
        if is_square_free(forward):
            moves.append(forward)
    for dc in [-1, 1]:
        nr, nc = r+1, c+dc
        if inside_board(nr, nc) and same_position([nr, nc], white_king):
            moves.append([nr, nc])
    return moves

def black_king_moves():
    moves = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = black_king[0] + dr, black_king[1] + dc
            dest = [nr, nc]
            if not inside_board(nr, nc):
                continue
            if same_position(dest, pawn) or same_position(dest, white_king):
                continue
            if adjacent(dest, white_king):
                continue
            moves.append(dest)
    return moves

def queen_moves(pos):
    moves = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                  (-1, -1), (-1, 1), (1, -1), (1, 1)]

    for dr, dc in directions:
        r, c = pos
        while True:
            r += dr
            c += dc
            if not inside_board(r, c):
                break
            dest = [r, c]
            if same_position(dest, white_king) or same_position(dest, black_king):
                moves.append(dest)
                break
            if not is_square_free(dest):
                break
            moves.append(dest)
    return moves

def evaluate_state(black_king_pos, pawn_pos, promoted_state, white_king_pos):
    distance = abs(black_king_pos[0] - pawn_pos[0]) + abs(black_king_pos[1] - pawn_pos[1])
    distance_penalty = -20 * (distance - 1) if distance > 1 else 0

    white_range = 1
    distance_to_white = abs(pawn_pos[0] - white_king_pos[0]) + abs(pawn_pos[1] - white_king_pos[1])
    danger_penalty = -30 if distance_to_white <= white_range else 0

    if not promoted_state and same_position(pawn_pos, white_king_pos):
        return -1000  # Pawn captured

    promotion_reward = 10 if promoted_state else 0
    score = distance_penalty + danger_penalty + promotion_reward
    return score

def game_over():
    if same_position(white_king, pawn) and not promoted:
        return "White king captured the pawn! Player wins!"
    if same_position(pawn, white_king):
        return "Black pawn captured the white king! Computer wins!"
    if same_position(black_king, white_king):
        return "Black king captured the white king! Computer wins!"
    if promoted and queen_attacks(white_king, pawn):
        return "Black queen attacks white king! Computer wins!"
    return None

def draw_legal_moves(moves):
    for pos in moves:
        r, c = pos
        pygame.draw.rect(screen, GREEN, (c * TAM + 5, r * TAM + 5, TAM - 10, TAM - 10), 3)

# --- Funciones para Minimax y simulación de estados ---

def is_square_free_for_state(pos, black_king_pos, pawn_pos, white_king_pos):
    return not (same_position(pos, white_king_pos) or same_position(pos, black_king_pos) or same_position(pos, pawn_pos))

def queen_attacks_for_state(pos, queen_pos):
    r, c = pos
    qr, qc = queen_pos
    if r == qr or c == qc or abs(r - qr) == abs(c - qc):
        return True
    return False

def is_in_check_for_state(pos, black_king_pos, pawn_pos, promoted_state, white_king_pos):
    if promoted_state and queen_attacks_for_state(pos, pawn_pos):
        return True
    if not promoted_state:
        r, c = pawn_pos
        possible_captures = [[r+1, c-1], [r+1, c+1]]
        if pos in possible_captures:
            return True
    if adjacent(pos, black_king_pos):
        return True
    return False

def white_king_legal_moves_for_state(black_king_pos, pawn_pos, promoted_state, white_king_pos):
    moves = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = white_king_pos[0] + dr, white_king_pos[1] + dc
            dest = [nr, nc]
            if not inside_board(nr, nc):
                continue
            if adjacent(dest, black_king_pos):
                continue
            if same_position(dest, white_king_pos):
                continue
            if same_position(dest, pawn_pos) and adjacent(pawn_pos, black_king_pos):
                continue
            if is_in_check_for_state(dest, black_king_pos, pawn_pos, promoted_state, white_king_pos):
                continue
            moves.append(dest)
    return moves

def pawn_moves_for_state(black_king_pos, pawn_pos, promoted_state, white_king_pos):
    r, c = pawn_pos
    moves = []
    if inside_board(r+1, c):
        forward = [r+1, c]
        if is_square_free_for_state(forward, black_king_pos, pawn_pos, white_king_pos):
            moves.append(forward)
    for dc in [-1, 1]:
        nr, nc = r+1, c+dc
        if inside_board(nr, nc) and same_position([nr, nc], white_king_pos):
            moves.append([nr, nc])
    return moves

def black_king_moves_for_state(black_king_pos, pawn_pos, promoted_state, white_king_pos):
    moves = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = black_king_pos[0] + dr, black_king_pos[1] + dc
            dest = [nr, nc]
            if not inside_board(nr, nc):
                continue
            if same_position(dest, pawn_pos) or same_position(dest, white_king_pos):
                continue
            if adjacent(dest, white_king_pos):
                continue
            moves.append(dest)
    return moves

def queen_moves_for_state(black_king_pos, pawn_pos, promoted_state, white_king_pos):
    moves = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                  (-1, -1), (-1, 1), (1, -1), (1, 1)]

    for dr, dc in directions:
        r, c = pawn_pos
        while True:
            r += dr
            c += dc
            if not inside_board(r, c):
                break
            dest = [r, c]
            if same_position(dest, white_king_pos) or same_position(dest, black_king_pos):
                moves.append(dest)
                break
            if not is_square_free_for_state(dest, black_king_pos, pawn_pos, white_king_pos):
                break
            moves.append(dest)
    return moves

def evaluate_state(black_king_pos, pawn_pos, promoted_state, white_king_pos):
    distance = abs(black_king_pos[0] - pawn_pos[0]) + abs(black_king_pos[1] - pawn_pos[1])
    distance_penalty = -20 * (distance - 1) if distance > 1 else 0

    white_range = 1
    distance_to_white = abs(pawn_pos[0] - white_king_pos[0]) + abs(pawn_pos[1] - white_king_pos[1])
    danger_penalty = -30 if distance_to_white <= white_range else 0

    if not promoted_state and same_position(pawn_pos, white_king_pos):
        return -1000

    promotion_reward = 10 if promoted_state else 0
    score = distance_penalty + danger_penalty + promotion_reward
    return score

def minimax(black_king_pos, pawn_pos, promoted_state, white_king_pos, depth, maximizing_player):
    if depth == 0 or game_over() is not None:
        score = evaluate_state(black_king_pos, pawn_pos, promoted_state, white_king_pos)
        return score, None

    if maximizing_player:
        max_eval = -float('inf')
        best_move = None

        moves = []

        # Peón o reina (computadora)
        if not promoted_state:
            for m in pawn_moves_for_state(black_king_pos, pawn_pos, promoted_state, white_king_pos):
                if adjacent(m, black_king_pos):
                    moves.append(('pawn', m))
        else:
            for m in queen_moves_for_state(black_king_pos, pawn_pos, promoted_state, white_king_pos):
                moves.append(('queen', m))

        # Rey negro
        for m in black_king_moves_for_state(black_king_pos, pawn_pos, promoted_state, white_king_pos):
            moves.append(('king', m))

        for piece, move in moves:
            new_black_king = black_king_pos[:]
            new_pawn = pawn_pos[:]
            new_promoted = promoted_state

            if piece == 'pawn' or piece == 'queen':
                new_pawn = move[:]
                if not promoted_state and new_pawn[0] == 7:
                    new_promoted = True
            else:
                new_black_king = move[:]

            eval_score, _ = minimax(new_black_king, new_pawn, new_promoted, white_king_pos, depth - 1, False)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = (piece, move, new_promoted, new_black_king, new_pawn)

        return max_eval, best_move

    else:
        min_eval = float('inf')
        best_move = None

        for move in white_king_legal_moves_for_state(black_king_pos, pawn_pos, promoted_state, white_king_pos):
            new_white_king = move[:]
            eval_score, _ = minimax(black_king_pos, pawn_pos, promoted_state, new_white_king, depth - 1, True)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = new_white_king

        return min_eval, best_move

# --- Modificar función de movimiento de computadora para usar Minimax ---

def computer_move():
    global promoted, pawn, black_king, white_turn

    depth = 3  # Ajusta profundidad para balance fuerza/velocidad
    score, best_move = minimax(black_king, pawn, promoted, white_king, depth, True)

    if best_move is not None:
        piece, move, new_promoted, new_black_king, new_pawn = best_move
        promoted = new_promoted
        if piece == 'pawn' or piece == 'queen':
            pawn = new_pawn
        else:
            black_king = new_black_king

    white_turn = True

# --- Main loop ---

def main():
    global white_turn, selected, legal_moves, white_king, black_king, pawn, promoted

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if white_turn and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                c, r = x // TAM, y // TAM

                if selected:
                    if [r, c] in legal_moves:
                        white_king = [r, c]
                        white_turn = False
                        selected = False
                        legal_moves = []
                    else:
                        selected = False
                        legal_moves = []
                else:
                    if same_position([r, c], white_king):
                        selected = True
                        legal_moves = white_king_legal_moves()

        screen.fill((0, 0, 0))
        draw_board()
        draw_pieces()

        if selected:
            draw_legal_moves(legal_moves)

        pygame.display.flip()

        if not white_turn:
            computer_move()

        winner = game_over()
        if winner:
            print(winner)
            text = font.render(winner, True, RED)
            screen.blit(text, (10, HEIGHT // 2 - 30))
            pygame.display.flip()
            pygame.time.wait(5000)
            pygame.quit()
            sys.exit()

        clock.tick(30)

if __name__ == "__main__":
    main()