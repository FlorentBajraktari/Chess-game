import pygame
import sys
import os
import chess
import random
import time
import json

pygame.init()

WIDTH, HEIGHT = 800, 700
ROWS, COLS = 8, 8
SQUARE_SIZE = 70

WHITE = (240, 217, 181)
BROWN = (181, 136, 99)
HIGHLIGHT = (0, 255, 0)
SELECTED = (255, 0, 0)
BG = (30, 30, 30)
FONT = pygame.font.SysFont('arial', 32)
END_FONT = pygame.font.SysFont('arial', 48)
SMALL_FONT = pygame.font.SysFont('arial', 24)

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Political Chess: USA vs EU")

START_TIME = 10 * 60
STATS_FILE = "game_stats.json"

move_history = []


def load_images_from_sprite():
    pieces = ['wK','wQ','wR','wB','wN','wP','bK','bQ','bR','bB','bN','bP']
    images = {}
    sprite_path = os.path.join("images", "ChessPiecesArray.png")
    sprite = pygame.image.load(sprite_path).convert_alpha()
    piece_width = sprite.get_width() // 6
    piece_height = sprite.get_height() // 2
    for idx, piece in enumerate(pieces):
        col = idx % 6
        row = idx // 6
        rect = pygame.Rect(col * piece_width, row * piece_height, piece_width, piece_height)
        image = sprite.subsurface(rect)
        images[piece] = pygame.transform.smoothscale(image, (SQUARE_SIZE, SQUARE_SIZE))
    return images

IMAGES = load_images_from_sprite()


def piece_symbol_to_key(piece):
    if piece is None:
        return None
    symbol = piece.symbol()
    color = 'w' if symbol.isupper() else 'b'
    kind = symbol.upper()
    return f"{color}{kind}"


def draw_board(win, board, selected_square=None, possible_moves=[]):
    for row in range(ROWS):
        for col in range(COLS):
            color = WHITE if (row + col) % 2 == 0 else BROWN
            rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(win, color, rect)
            square = chess.square(col, 7 - row)
            if selected_square == (row, col):
                pygame.draw.rect(win, SELECTED, rect, 4)
            elif (row, col) in possible_moves:
                pygame.draw.rect(win, HIGHLIGHT, rect, 4)
            piece = board.piece_at(square)
            if piece:
                key = piece_symbol_to_key(piece)
                win.blit(IMAGES[key], rect)


def get_legal_moves_for_square(board, row, col):
    square = chess.square(col, 7 - row)
    return [move for move in board.legal_moves if move.from_square == square]


def get_square_under_mouse(pos):
    x, y = pos
    col = x // SQUARE_SIZE
    row = y // SQUARE_SIZE
    return row, col


def ai_move(board):
    moves = list(board.legal_moves)
    if moves:
        move = random.choice(moves)
        board.push(move)
        move_history.append(move)


def save_stats(result):
    stats = {"usa_wins": 0, "eu_wins": 0, "draws": 0}
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f:
            stats.update(json.load(f))
    stats[result] += 1
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f)


def show_end_screen(win, board, mode, white_score, black_score):
    win.fill(BG)
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            msg = "EU Wins! (Checkmate)"
            save_stats("eu_wins")
        else:
            msg = "USA Wins! (Checkmate)"
            save_stats("usa_wins")
    elif board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves() or board.is_fivefold_repetition():
        msg = "Draw"
        save_stats("draws")
    else:
        msg = "Game Over"

    text = END_FONT.render(msg, True, (255, 255, 255))
    win.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 40))
    score_text = SMALL_FONT.render("Press 'R' to Play Again or 'Q' to Quit", True, (255, 255, 255))
    win.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 20))
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()
                    return
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()


def choose_mode():
    WIN.fill(BG)
    pvp = FONT.render("1. Multiplayer (1vs1)", True, (255, 255, 255))
    pvc = FONT.render("2. Player vs Computer", True, (255, 255, 255))
    WIN.blit(pvp, (WIDTH // 2 - pvp.get_width() // 2, HEIGHT // 2 - 40))
    WIN.blit(pvc, (WIDTH // 2 - pvc.get_width() // 2, HEIGHT // 2 + 20))
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 'pvp'
                elif event.key == pygame.K_2:
                    return 'pvc'


def get_captured_pieces(board, color):
    start = {'P': 8, 'N': 2, 'B': 2, 'R': 2, 'Q': 1}
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and ((piece.color == chess.WHITE and color == chess.WHITE) or (piece.color == chess.BLACK and color == chess.BLACK)):
            s = piece.symbol().upper()
            if s in start:
                start[s] -= 1
    return {k: v for k, v in start.items() if v > 0}


def draw_score_and_time(win, white_score, black_score, white_time, black_time):
    y = HEIGHT - 60
    x = 10
    win.fill(BG, (0, HEIGHT - 100, WIDTH, 100))
    win.blit(SMALL_FONT.render("USA captured:", True, (0, 0, 0)), (x, y))
    x += 140
    for k, v in white_score.items():
        for _ in range(v):
            win.blit(IMAGES['b' + k], (x, y))
            x += 40
    x = 10
    y += 40
    win.blit(SMALL_FONT.render("EU captured:", True, (0, 0, 0)), (x, y))
    x += 140
    for k, v in black_score.items():
        for _ in range(v):
            win.blit(IMAGES['w' + k], (x, y))
            x += 40
    t1 = SMALL_FONT.render(f"USA Time: {int(white_time // 60):02}:{int(white_time % 60):02}", True, (0, 0, 0))
    t2 = SMALL_FONT.render(f"EU Time: {int(black_time // 60):02}:{int(black_time % 60):02}", True, (0, 0, 0))
    win.blit(t1, (WIDTH - 250, HEIGHT - 60))
    win.blit(t2, (WIDTH - 250, HEIGHT - 20))


def main():
    global move_history
    board = chess.Board()
    mode = choose_mode()
    run = True
    selected = None
    possible_moves = []
    white_time = START_TIME
    black_time = START_TIME
    last_time = time.time()
    white_score = get_captured_pieces(board, chess.BLACK)
    black_score = get_captured_pieces(board, chess.WHITE)
    move_history = []

    while run:
        now = time.time()
        if board.turn == chess.WHITE:
            white_time -= now - last_time
        else:
            black_time -= now - last_time
        last_time = now

        draw_board(WIN, board, selected, possible_moves)
        white_score = get_captured_pieces(board, chess.BLACK)
        black_score = get_captured_pieces(board, chess.WHITE)
        draw_score_and_time(WIN, white_score, black_score, white_time, black_time)
        pygame.display.update()

        if white_time <= 0 or black_time <= 0 or board.is_game_over():
            show_end_screen(WIN, board, mode, sum(white_score.values()), sum(black_score.values()))
            run = False
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u and move_history:
                    board.pop()
                    move_history.pop()

            if not board.is_game_over() and event.type == pygame.MOUSEBUTTONDOWN:
                row, col = get_square_under_mouse(pygame.mouse.get_pos())
                square = chess.square(col, 7 - row)
                piece = board.piece_at(square)

                if selected:
                    if (row, col) == selected:
                        selected = None
                        possible_moves = []
                    elif piece and piece.color == board.turn:
                        selected = (row, col)
                        possible_moves = get_legal_moves_for_square(board, row, col)
                    else:
                        move = None
                        for m in possible_moves:
                            if m.to_square == square:
                                move = m
                                break
                        if move:
                            board.push(move)
                            move_history.append(move)
                            selected = None
                            possible_moves = []
                else:
                    if piece and piece.color == board.turn:
                        selected = (row, col)
                        possible_moves = get_legal_moves_for_square(board, row, col)

        if mode == 'pvc' and not board.is_game_over() and board.turn == chess.BLACK:
            pygame.time.delay(500)
            ai_move(board)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()