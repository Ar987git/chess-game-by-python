import pygame
import sys
from typing import List, Tuple, Optional
import tkinter as tk
from tkinter import messagebox
warning = messagebox.askyesno("Warning!", "All intellectual and material rights of this game belong to 'Aria Karimi' and any copying of it is prosecuted.")
if warning == 1:
    # Constants
    WIDTH, HEIGHT = 800, 800
    SQUARE_SIZE = WIDTH // 8
    FPS = 60
    # Colors
    white = (255, 255, 255)
    black = (0, 0, 0)
    LIGHT_BROWN = (222, 184, 135)
    DARK_BROWN = (139, 69, 19)
    HIGHLIGHT_COLOR = (50, 205, 50, 100)
    # Piece types
    class Piece:
        def __init__(self, color: str, piece_type: str, position: Tuple[int, int]):
            self.color = color
            self.type = piece_type
            self.position = position
            self.image = pygame.image.load(f'{color}_{piece_type}.png')
            self.image = pygame.transform.scale(self.image, (SQUARE_SIZE, SQUARE_SIZE))
        def valid_moves(self, board: 'Board') -> List[Tuple[int, int]]:
            moves = []
            x, y = self.position
            # Pawn movement
            if self.type == 'pawn':
                direction = -1 if self.color == 'white' else 1
                # Forward moves
                if board.is_empty((x, y + direction)):
                    moves.append((x, y + direction))
                    if (y == 6 and self.color == 'white') or (y == 1 and self.color == 'black'):
                        if board.is_empty((x, y + 2*direction)):
                            moves.append((x, y + 2*direction))
                # Captures
                for dx in [-1, 1]:
                    if 0 <= x + dx < 8 and board.get_piece_at((x + dx, y + direction)):
                        moves.append((x + dx, y + direction))
            # Rook movement (horizontal/vertical)
            elif self.type == 'rook':
                directions = [(1,0), (-1,0), (0,1), (0,-1)]
                for dx, dy in directions:
                    for i in range(1, 8):
                        new_x = x + dx * i
                        new_y = y + dy * i
                        if 0 <= new_x < 8 and 0 <= new_y < 8:
                            piece = board.get_piece_at((new_x, new_y))
                            if not piece:
                                moves.append((new_x, new_y))
                            else:
                                if piece.color != self.color:
                                    moves.append((new_x, new_y))
                                break
                        else:
                            break
            # Knight movement (L-shapes)
            elif self.type == 'knight':
                jumps = [(2,1), (2,-1), (-2,1), (-2,-1),
                        (1,2), (1,-2), (-1,2), (-1,-2)]
                for dx, dy in jumps:
                    new_x = x + dx
                    new_y = y + dy
                    if 0 <= new_x < 8 and 0 <= new_y < 8:
                        piece = board.get_piece_at((new_x, new_y))
                        if not piece or piece.color != self.color:
                            moves.append((new_x, new_y))
            # Bishop movement (diagonal)
            elif self.type == 'bishop':
                directions = [(1,1), (1,-1), (-1,1), (-1,-1)]
                for dx, dy in directions:
                    for i in range(1, 8):
                        new_x = x + dx * i
                        new_y = y + dy * i
                        if 0 <= new_x < 8 and 0 <= new_y < 8:
                            piece = board.get_piece_at((new_x, new_y))
                            if not piece:
                                moves.append((new_x, new_y))
                            else:
                                if piece.color != self.color:
                                    moves.append((new_x, new_y))
                                break
                        else:
                            break
            # Queen movement (rook + bishop)
            elif self.type == 'queen':
                # Combine rook and bishop directions
                directions = [(1,0), (-1,0), (0,1), (0,-1),
                            (1,1), (1,-1), (-1,1), (-1,-1)]
                for dx, dy in directions:
                    for i in range(1, 8):
                        new_x = x + dx * i
                        new_y = y + dy * i
                        if 0 <= new_x < 8 and 0 <= new_y < 8:
                            piece = board.get_piece_at((new_x, new_y))
                            if not piece:
                                moves.append((new_x, new_y))
                            else:
                                if piece.color != self.color:
                                    moves.append((new_x, new_y))
                                break
                        else:
                            break
            # King movement (one square any direction)
            elif self.type == 'king':
                directions = [(1,0), (-1,0), (0,1), (0,-1),
                            (1,1), (1,-1), (-1,1), (-1,-1)]
                for dx, dy in directions:
                    new_x = x + dx
                    new_y = y + dy
                    if 0 <= new_x < 8 and 0 <= new_y < 8:
                        piece = board.get_piece_at((new_x, new_y))
                        if not piece or piece.color != self.color:
                            moves.append((new_x, new_y))
            return moves
    class Board:
        def __init__(self):
            self.pieces: List[Piece] = []
            self.selected_piece: Optional[Piece] = None
            self.current_turn = 'white'
            self.init_pieces()
        def init_pieces(self):
            # Initialize pawns
            for x in range(8):
                self.pieces.append(Piece('black', 'pawn', (x, 1)))
                self.pieces.append(Piece('white', 'pawn', (x, 6)))
            # Initialize other pieces
            back_row = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
            for i, piece_type in enumerate(back_row):
                self.pieces.append(Piece('black', piece_type, (i, 0)))
                self.pieces.append(Piece('white', piece_type, (i, 7)))
        def get_piece_at(self, pos: Tuple[int, int]) -> Optional[Piece]:
            for piece in self.pieces:
                if piece.position == pos:
                    return piece
            return None
        def is_empty(self, pos: Tuple[int, int]) -> bool:
            return self.get_piece_at(pos) is None
        def move_piece(self, piece: Piece, new_pos: Tuple[int, int]) -> bool:
            captured = self.get_piece_at(new_pos)
            original_pos = piece.position
            # Make the move temporarily
            piece.position = new_pos
            if captured:
                self.pieces.remove(captured)
            # Check if move leaves own king in check
            if self.is_in_check(piece.color):
                # Revert the move if invalid
                piece.position = original_pos
                if captured:
                    self.pieces.append(captured)
                return False
            self.current_turn = 'black' if self.current_turn == 'white' else 'white'
            # Check for checkmate
            if self.is_checkmate('black' if piece.color == 'white' else 'white'):
                self.handle_checkmate(piece.color)
                return True
            return True
        def get_king_position(self, color: str) -> Tuple[int, int]:
            for piece in self.pieces:
                if piece.type == 'king' and piece.color == color:
                    return piece.position
            return (-1, -1)  # Should never happen
        def is_in_check(self, color: str) -> bool:
            king_pos = self.get_king_position(color)
            # Check if any opponent piece can attack the king
            for piece in self.pieces:
                if piece.color != color and king_pos in piece.valid_moves(self):
                    return True
            return False
        def is_checkmate(self, color: str) -> bool:
            if not self.is_in_check(color):
                return False
            # Check if any move can escape check
            for piece in self.pieces:
                if piece.color == color:
                    original_pos = piece.position
                    for move in piece.valid_moves(self):
                        # Try the move
                        captured = self.get_piece_at(move)
                        piece.position = move
                        if captured:
                            self.pieces.remove(captured)
                        if not self.is_in_check(color):
                            # Revert and return not checkmate
                            piece.position = original_pos
                            if captured:
                                self.pieces.append(captured)
                            return False
                        # Revert the move
                        piece.position = original_pos
                        if captured:
                            self.pieces.append(captured)
            return True
        def handle_checkmate(self, winning_color: str):
            # Display the checkmate message
            result = f"{winning_color.capitalize()} wins by checkmate!"
            pygame.display.set_caption("Checkmate!")
            pygame.time.delay(500)  # Small delay to ensure the last move is visible
            # Show the result message box
            show_message_box("Checkmate!", result)
            # Ask if the user wants to play again
            play_again = ask_yes_no("Play Again?", "Do you want to play another game?")
            if play_again:
                self.reset()
            else:
                pygame.quit()
                sys.exit()
        def reset(self):
            self.pieces = []
            self.selected_piece = None
            self.current_turn = 'white'
            self.init_pieces()
    def draw_board(screen, board: Board):
        for row in range(8):
            for col in range(8):
                color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
                pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        # Draw move highlights
        if board.selected_piece:
            # Highlight selected piece
            x, y = board.selected_piece.position
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            s.fill((*HIGHLIGHT_COLOR[:3], 128))
            screen.blit(s, (x * SQUARE_SIZE, y * SQUARE_SIZE))
            # Highlight valid moves
            moves = board.selected_piece.valid_moves(board)
            for move_x, move_y in moves:
                s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                s.fill((*HIGHLIGHT_COLOR[:3], 80))
                screen.blit(s, (move_x * SQUARE_SIZE, move_y * SQUARE_SIZE))
        # Draw pieces
        for piece in board.pieces:
            x, y = piece.position
            screen.blit(piece.image, (x * SQUARE_SIZE, y * SQUARE_SIZE))
    def show_message_box(title: str, message: str):
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        messagebox.showinfo(title, message)
        root.destroy()
    def ask_yes_no(title: str, message: str) -> bool:
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        response = messagebox.askyesno(title, message)
        root.destroy()
        return response
    def main():
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess Game")
        clock = pygame.time.Clock()
        board = Board()
        try:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = pygame.mouse.get_pos()
                        col = x // SQUARE_SIZE
                        row = y // SQUARE_SIZE
                        clicked_piece = board.get_piece_at((col, row))
                        if clicked_piece and clicked_piece.color == board.current_turn:
                            board.selected_piece = clicked_piece
                        elif board.selected_piece:
                            if (col, row) in board.selected_piece.valid_moves(board):
                                board.move_piece(board.selected_piece, (col, row))
                            board.selected_piece = None
                screen.fill(white)
                draw_board(screen, board)
                pygame.display.flip()
                clock.tick(FPS)
        except Exception as e:
            print(f"An error occurred: {e}")
            pygame.quit()
            sys.exit()
    if __name__ == "__main__":
        main()
