import pygame
import sys
import os
import political_chess
import chess
import random


# Inicializimi i Pygame
pygame.init()

WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

WHITE = (240, 217, 181)
BROWN = (181, 136, 99)
HIGHLIGHT = (0, 255, 0)
SELECTED = (255, 0, 0)
FONT = pygame.font.SysFont('arial', 32)
END_FONT = pygame.font.SysFont('arial', 48)

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Political Chess: USA vs EU")

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

# Map python-chess piece symbol to sprite key
def piece_symbol_to_key(piece):
    if piece is None:
        return None
    symbol = piece.symbol()
    if symbol.isupper():
        color = 'w'
    else:
        color = 'b'
    kind = symbol.upper()
    return f"{color}{kind}"

# Map python-chess piece to political name
def piece_to_political_name(piece, square):
    # White
    if piece is None:
        return None
    if piece.symbol() == 'K':
        return "Trump"
    if piece.symbol() == 'Q':
        return "Yellen"
    if piece.symbol() == 'R':
        return "Elon Musk" if political_chess.square_file(square) == 0 else "Kamala"
    if piece.symbol() == 'B':
        return "FED" if political_chess.square_file(square) == 2 else "Pentagon"
    if piece.symbol() == 'N':
        return "CIA" if political_chess.square_file(square) == 1 else "Tesla"
    if piece.symbol() == 'P':
        return "Pawn"
    # Black
    if piece.symbol() == 'k':
        return "Ursula"
    if piece.symbol() == 'q':
        return "Lagarde"
    if piece.symbol() == 'r':
        return "Macron" if political_chess.square_file(square) == 0 else "Scholz"
    if piece.symbol() == 'b':
        return "Commission" if political_chess.square_file(square) == 2 else "Parliament"
    if piece.symbol() == 'n':
        return "NATO" if political_chess.square_file(square) == 1 else "Polonia"
    if piece.symbol() == 'p':
        return "Pawn"
    return "?"

def draw_board(win, board, selected_square=None, possible_moves=[]):
    win.fill(WHITE)
    for row in range(ROWS):
        for col in range(COLS):
            color = WHITE if (row + col) % 2 == 0 else BROWN
            rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(win, color, rect)
            square = political_chess.square(col, 7-row)
            if selected_square == (row, col):
                pygame.draw.rect(win, SELECTED, rect, 4)
            elif (row, col) in possible_moves:
                pygame.draw.rect(win, HIGHLIGHT, rect, 4)
            piece = board.piece_at(square)
            if piece:
                key = piece_symbol_to_key(piece)
                if key in IMAGES:
                    win.blit(IMAGES[key], rect)
                else:
                    text = FONT.render(piece.symbol().upper(), True, (0, 0, 0))
                    text_rect = text.get_rect(center=rect.center)
                    win.blit(text, text_rect)
    pygame.display.update()

def get_square_under_mouse(pos):
    x, y = pos
    col = x // SQUARE_SIZE
    row = y // SQUARE_SIZE
    return row, col

def get_legal_moves_for_square(board, row, col):
    square = political_chess.square(col, 7-row)
    return [move for move in board.legal_moves if move.from_square == square]

def ai_move(board):
    moves = list(board.legal_moves)
    if moves:
        move = random.choice(moves)
        board.push(move)

def show_end_screen(win, board):
    win.fill(WHITE)
    if board.is_checkmate():
        if board.turn == political_chess.WHITE:
            msg = "EU Wins! (Checkmate)"
        else:
            msg = "USA Wins! (Checkmate)"
    elif board.is_stalemate():
        msg = "Draw (Stalemate)"
    elif board.is_insufficient_material():
        msg = "Draw (Insufficient Material)"
    else:
        msg = "Game Over"
    text = END_FONT.render(msg, True, (0, 0, 0))
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
    win.blit(text, text_rect)
    pygame.display.update()
    pygame.time.wait(4000)

def main():
    board = political_chess.Board()
    run = True
    selected = None
    possible_moves = []
    game_over = False

    while run:
        draw_board(WIN, board, selected, possible_moves)
        if board.is_game_over():
            show_end_screen(WIN, board)
            run = False
            continue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if not board.is_game_over() and board.turn == political_chess.WHITE and event.type == pygame.MOUSEBUTTONDOWN:
                row, col = get_square_under_mouse(pygame.mouse.get_pos())
                square = political_chess.square(col, 7-row)
                piece = board.piece_at(square)

                if selected:
                    # Try to make move
                    move = None
                    for m in possible_moves:
                        if m.to_square == square:
                            move = m
                            break
                    if move:
                        board.push(move)
                        selected = None
                        possible_moves = []
                    else:
                        selected = None
                        possible_moves = []
                else:
                    if piece and piece.color == political_chess.WHITE:
                        selected = (row, col)
                        possible_moves = get_legal_moves_for_square(board, row, col)

        # AI move for EU (black)
        if not board.is_game_over() and board.turn == political_chess.BLACK:
            pygame.time.delay(500)
            ai_move(board)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()