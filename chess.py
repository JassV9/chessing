from enum import Enum
from typing import List, Tuple, Optional
import tkinter as tk
from tkinter import messagebox
from stockfish import Stockfish
import threading
import time
import os

class PieceType(Enum):
    PAWN = 'p'
    ROOK = 'r'
    KNIGHT = 'n'
    BISHOP = 'b'
    QUEEN = 'q'
    KING = 'k'

class Color(Enum):
    WHITE = 'w'
    BLACK = 'b'

class Piece:
    def __init__(self, color: Color, piece_type: PieceType):
        self.color = color
        self.type = piece_type
        self.has_moved = False

    def __str__(self):
        return f"{self.color.value}{self.type.value}"

class ChessBoard:
    def __init__(self):
        self.board = self.initialize_board()
        self.current_player = Color.WHITE
        self.move_history = []
        self.last_move = None  # For en passant
        self.white_king_pos = (7, 4)
        self.black_king_pos = (0, 4)

    def initialize_board(self) -> List[List[Optional[Piece]]]:
        board = [[None for _ in range(8)] for _ in range(8)]
        
        # Set up pawns
        for col in range(8):
            board[1][col] = Piece(Color.BLACK, PieceType.PAWN)
            board[6][col] = Piece(Color.WHITE, PieceType.PAWN)
        
        # Set up other pieces
        piece_order = [
            PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN,
            PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK
        ]
        
        for col in range(8):
            board[0][col] = Piece(Color.BLACK, piece_order[col])
            board[7][col] = Piece(Color.WHITE, piece_order[col])
        
        return board

    def display_board(self):
        print('   a b c d e f g h')
        print('  ─────────────────')
        for row in range(8):
            print(f'{8-row} │', end=' ')
            for col in range(8):
                piece = self.board[row][col]
                if piece is None:
                    print('.', end=' ')
                else:
                    print(piece.type.value, end=' ')
            print(f'│ {8-row}')
        print('  ─────────────────')
        print('   a b c d e f g h')

    def get_piece_moves(self, row: int, col: int, checking_check: bool = False) -> List[Tuple[int, int]]:
        piece = self.board[row][col]
        if piece is None:
            return []

        moves = []
        if piece.type == PieceType.PAWN:
            moves.extend(self._get_pawn_moves(row, col))
        elif piece.type == PieceType.ROOK:
            moves.extend(self._get_rook_moves(row, col))
        elif piece.type == PieceType.KNIGHT:
            moves.extend(self._get_knight_moves(row, col))
        elif piece.type == PieceType.BISHOP:
            moves.extend(self._get_bishop_moves(row, col))
        elif piece.type == PieceType.QUEEN:
            moves.extend(self._get_rook_moves(row, col))
            moves.extend(self._get_bishop_moves(row, col))
        elif piece.type == PieceType.KING:
            moves.extend(self._get_king_moves(row, col, checking_check))

        # Only check for moves causing check if we're not already checking for check
        if not checking_check:
            return [move for move in moves if not self._move_causes_check(row, col, move[0], move[1])]
        return moves

    def _get_pawn_moves(self, row: int, col: int) -> List[Tuple[int, int]]:
        moves = []
        piece = self.board[row][col]
        direction = 1 if piece.color == Color.BLACK else -1

        # Forward move
        if 0 <= row + direction < 8 and self.board[row + direction][col] is None:
            moves.append((row + direction, col))
            # Double move from starting position
            if ((piece.color == Color.WHITE and row == 6) or 
                (piece.color == Color.BLACK and row == 1)):
                if self.board[row + 2*direction][col] is None:
                    moves.append((row + 2*direction, col))

        # Captures
        for dcol in [-1, 1]:
            if 0 <= col + dcol < 8 and 0 <= row + direction < 8:
                target = self.board[row + direction][col + dcol]
                if target and target.color != piece.color:
                    moves.append((row + direction, col + dcol))

        # En passant
        if self.last_move:
            last_piece = self.board[self.last_move[2]][self.last_move[3]]
            if (last_piece and last_piece.type == PieceType.PAWN and 
                abs(self.last_move[0] - self.last_move[2]) == 2 and
                row == self.last_move[2] and
                abs(col - self.last_move[3]) == 1):
                moves.append((row + direction, self.last_move[3]))

        return moves

    def _get_rook_moves(self, row: int, col: int) -> List[Tuple[int, int]]:
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        piece = self.board[row][col]

        for drow, dcol in directions:
            current_row, current_col = row + drow, col + dcol
            while 0 <= current_row < 8 and 0 <= current_col < 8:
                target = self.board[current_row][current_col]
                if target is None:
                    moves.append((current_row, current_col))
                elif target.color != piece.color:
                    moves.append((current_row, current_col))
                    break
                else:
                    break
                current_row += drow
                current_col += dcol

        return moves

    def _get_knight_moves(self, row: int, col: int) -> List[Tuple[int, int]]:
        moves = []
        piece = self.board[row][col]
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]

        for drow, dcol in knight_moves:
            new_row, new_col = row + drow, col + dcol
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = self.board[new_row][new_col]
                if target is None or target.color != piece.color:
                    moves.append((new_row, new_col))

        return moves

    def _get_bishop_moves(self, row: int, col: int) -> List[Tuple[int, int]]:
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        piece = self.board[row][col]

        for drow, dcol in directions:
            current_row, current_col = row + drow, col + dcol
            while 0 <= current_row < 8 and 0 <= current_col < 8:
                target = self.board[current_row][current_col]
                if target is None:
                    moves.append((current_row, current_col))
                elif target.color != piece.color:
                    moves.append((current_row, current_col))
                    break
                else:
                    break
                current_row += drow
                current_col += dcol

        return moves

    def _get_king_moves(self, row: int, col: int, checking_check: bool = False) -> List[Tuple[int, int]]:
        moves = []
        piece = self.board[row][col]
        
        # Normal moves
        for drow in [-1, 0, 1]:
            for dcol in [-1, 0, 1]:
                if drow == 0 and dcol == 0:
                    continue
                new_row, new_col = row + drow, col + dcol
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target = self.board[new_row][new_col]
                    if target is None or target.color != piece.color:
                        moves.append((new_row, new_col))

        # Only check castling if we're not in the check-detection phase
        if not checking_check and not piece.has_moved:
            # Kingside castling
            if (self.board[row][7] and 
                self.board[row][7].type == PieceType.ROOK and 
                not self.board[row][7].has_moved and
                all(self.board[row][c] is None for c in range(5, 7)) and
                not self.is_in_check(piece.color) and
                not any(self.is_square_attacked(row, c, piece.color) for c in range(5, 7))):
                moves.append((row, 6))
            
            # Queenside castling
            if (self.board[row][0] and 
                self.board[row][0].type == PieceType.ROOK and 
                not self.board[row][0].has_moved and
                all(self.board[row][c] is None for c in range(1, 4)) and
                not self.is_in_check(piece.color) and
                not any(self.is_square_attacked(row, c, piece.color) for c in range(2, 4))):
                moves.append((row, 2))

        return moves

    def _move_causes_check(self, start_row: int, start_col: int, end_row: int, end_col: int) -> bool:
        # Make temporary move
        piece = self.board[start_row][start_col]
        captured_piece = self.board[end_row][end_col]
        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = None

        # Store original king position
        original_king_pos = None
        if piece.type == PieceType.KING:
            if piece.color == Color.WHITE:
                original_king_pos = self.white_king_pos
                self.white_king_pos = (end_row, end_col)
            else:
                original_king_pos = self.black_king_pos
                self.black_king_pos = (end_row, end_col)

        # Check if the move results in check
        in_check = self.is_in_check(piece.color)

        # Undo move
        self.board[start_row][start_col] = piece
        self.board[end_row][end_col] = captured_piece
        
        # Restore king position if king was moved
        if original_king_pos:
            if piece.color == Color.WHITE:
                self.white_king_pos = original_king_pos
            else:
                self.black_king_pos = original_king_pos

        return in_check

    def is_in_check(self, color: Color) -> bool:
        king_pos = self.white_king_pos if color == Color.WHITE else self.black_king_pos
        return self.is_square_attacked(king_pos[0], king_pos[1], color)

    def is_square_attacked(self, row: int, col: int, color: Color) -> bool:
        # Check for attacks from all opposing pieces
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece.color != color:
                    # Pass checking_check=True to avoid infinite recursion
                    moves = self.get_piece_moves(r, c, checking_check=True)
                    if (row, col) in moves:
                        return True
        return False

    def is_checkmate(self, color: Color) -> bool:
        if not self.is_in_check(color):
            return False

        # Check if any move can get out of check
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    moves = self.get_piece_moves(row, col)
                    if moves:
                        return False
        return True

    def is_stalemate(self, color: Color) -> bool:
        if self.is_in_check(color):
            return False

        # Check if any legal moves are available
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    moves = self.get_piece_moves(row, col)
                    if moves:
                        return False
        return True

    def make_move(self, start: str, end: str) -> bool:
        try:
            # Convert chess notation to array indices
            start_col = ord(start[0].lower()) - ord('a')
            start_row = 8 - int(start[1])
            end_col = ord(end[0].lower()) - ord('a')
            end_row = 8 - int(end[1])

            # Validate input coordinates
            if not (0 <= start_row < 8 and 0 <= start_col < 8 and 
                    0 <= end_row < 8 and 0 <= end_col < 8):
                return False

            piece = self.board[start_row][start_col]
            if not piece or piece.color != self.current_player:
                return False

            valid_moves = self.get_piece_moves(start_row, start_col)
            if (end_row, end_col) not in valid_moves:
                return False

            # Handle special moves
            if piece.type == PieceType.PAWN:
                # En passant
                if (end_col != start_col and 
                    self.board[end_row][end_col] is None):
                    self.board[start_row][end_col] = None  # Capture the passed pawn

                # Promotion (automatically to Queen)
                if end_row in [0, 7]:
                    piece = Piece(piece.color, PieceType.QUEEN)

            # Handle castling
            if piece.type == PieceType.KING and abs(end_col - start_col) == 2:
                # Kingside castling
                if end_col == 6:
                    rook = self.board[start_row][7]
                    self.board[start_row][7] = None
                    self.board[start_row][5] = rook
                    if rook:
                        rook.has_moved = True
                # Queenside castling
                elif end_col == 2:
                    rook = self.board[start_row][0]
                    self.board[start_row][0] = None
                    self.board[start_row][3] = rook
                    if rook:
                        rook.has_moved = True

            # Make the move
            self.board[end_row][end_col] = piece
            self.board[start_row][start_col] = None
            piece.has_moved = True

            # Update king position
            if piece.type == PieceType.KING:
                if piece.color == Color.WHITE:
                    self.white_king_pos = (end_row, end_col)
                else:
                    self.black_king_pos = (end_row, end_col)

            # Record move for en passant
            self.last_move = (start_row, start_col, end_row, end_col)
            self.move_history.append((start, end))

            # Switch players
            self.current_player = Color.BLACK if self.current_player == Color.WHITE else Color.WHITE
            return True
        
        except (IndexError, ValueError):
            return False

class ChessGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Chess")
        self.game = ChessBoard()
        self.selected_square = None
        self.buttons = [[None for _ in range(8)] for _ in range(8)]
        self.vs_ai = False
        self.self_play = False
        self.stockfish = None
        
        # Use the exact path for your Stockfish executable
        stockfish_path = r"C:\Users\jason\Downloads\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe"
        
        try:
            if not os.path.exists(stockfish_path):
                print(f"Stockfish not found at: {os.path.abspath(stockfish_path)}")
                raise FileNotFoundError(f"Stockfish executable not found at: {stockfish_path}")
                
            self.stockfish = Stockfish(path=stockfish_path)
            self.stockfish.set_skill_level(20)
            self.stockfish.set_depth(15)
            print(f"Successfully initialized Stockfish at: {stockfish_path}")
        except Exception as e:
            print(f"Error initializing Stockfish: {e}")
            messagebox.showwarning("Stockfish Error", 
                f"Error initializing Stockfish: {e}\n\n"
                f"Please ensure Stockfish is installed at:\n{os.path.abspath(stockfish_path)}")
            
        self.setup_board()
        self.setup_controls()
        self.setup_evaluation_display()

    def setup_controls(self):
        control_frame = tk.Frame(self.window)
        control_frame.grid(row=8, column=0, columnspan=8)
        
        self.ai_button = tk.Button(control_frame, text="VS Player", command=self.toggle_ai_mode)
        self.ai_button.pack(pady=5)
        
        self.self_play_button = tk.Button(control_frame, text="Self Play", command=self.toggle_self_play)
        self.self_play_button.pack(pady=5)
        
        self.restart_button = tk.Button(control_frame, text="Restart", command=self.restart_game)
        self.restart_button.pack(pady=5)

    def restart_game(self):
        self.game = ChessBoard()
        self.selected_square = None
        if self.stockfish:
            self.stockfish.set_position([])
        self.update_display()
        if self.self_play:
            self.start_self_play()

    def toggle_self_play(self):
        if not self.stockfish:
            messagebox.showerror("Error", 
                "Stockfish is not available.\n\n"
                "Please ensure the Stockfish executable is in the correct location.")
            return
            
        self.self_play = not self.self_play
        self.vs_ai = False
        self.ai_button.config(text="VS Player")
        self.self_play_button.config(text="Stop Self Play" if self.self_play else "Self Play")
        
        if self.self_play:
            self.restart_game()
        else:
            self.restart_game()

    def start_self_play(self):
        if not self.self_play:
            return
        
        def play_game():
            while self.self_play and not self.game.is_checkmate(self.game.current_player) and not self.game.is_stalemate(self.game.current_player):
                self.make_stockfish_move()
                time.sleep(1)  # Delay between moves
                self.window.update()
                print(f"Self-play move made, history: {self.game.move_history}")  # Debug print

        thread = threading.Thread(target=play_game)
        thread.daemon = True
        thread.start()

    def toggle_ai_mode(self):
        if not self.stockfish:
            messagebox.showerror("Error", 
                "Stockfish is not available.\n\n"
                "Please ensure the Stockfish executable is in the correct location.")
            return
            
        self.vs_ai = not self.vs_ai
        self.self_play = False
        self.self_play_button.config(text="Self Play")
        self.ai_button.config(text="VS Stockfish" if not self.vs_ai else "VS Player")
        if self.vs_ai and self.game.current_player == Color.BLACK:
            self.make_stockfish_move()

    def get_fen_position(self):
        # Convert current board state to FEN notation
        fen = []
        empty = 0
        
        for row in range(8):
            for col in range(8):
                piece = self.game.board[row][col]
                if piece is None:
                    empty += 1
                else:
                    if empty > 0:
                        fen.append(str(empty))
                        empty = 0
                    symbol = piece.type.value
                    fen.append(symbol.upper() if piece.color == Color.WHITE else symbol.lower())
            if empty > 0:
                fen.append(str(empty))
                empty = 0
            if row < 7:
                fen.append('/')
        
        # Add current player
        fen.append(' w ' if self.game.current_player == Color.WHITE else ' b ')
        
        return ''.join(fen)

    def setup_evaluation_display(self):
        # Create canvas for evaluation bar
        self.eval_canvas = tk.Canvas(self.window, width=30, height=400, bg='gray')
        self.eval_canvas.grid(row=0, column=8, rowspan=8, padx=5)
        
        # Create initial evaluation bar (neutral position - equal parts black and white)
        self.eval_bar_black = self.eval_canvas.create_rectangle(
            0, 0, 30, 200,  # Top half
            fill='black'
        )
        self.eval_bar_white = self.eval_canvas.create_rectangle(
            0, 200, 30, 400,  # Bottom half
            fill='white'
        )
        
        self.eval_text = self.eval_canvas.create_text(
            15, 10,  # Position at top of bar
            text="0.0",
            fill='white'  # White text for better visibility
        )
        self.update_evaluation()

    def update_evaluation(self):
        if not self.stockfish:
            return
            
        try:
            self.stockfish.set_position([move[0] + move[1] for move in self.game.move_history])
            eval = self.stockfish.get_evaluation()
            
            # Convert evaluation to a visual representation
            max_height = 400  # Total height of canvas
            middle = max_height / 2
            
            if eval['type'] == 'cp':
                score = eval['value'] / 100.0  # Convert centipawns to pawns
                
                # Use a linear mapping for scores between -5 and 5
                normalized_score = max(min(score, 5), -5)  # Clamp between -5 and 5
                
                # Calculate the sizes of white and black sections
                # Positive score means white advantage (white section grows)
                white_height = middle * (1 + normalized_score / 5)
                
                # Create two rectangles: black on top, white on bottom
                self.eval_canvas.delete(self.eval_bar_black)  # Remove old black section
                self.eval_canvas.delete(self.eval_bar_white)  # Remove old white section
                
                # Create black section (top)
                self.eval_bar_black = self.eval_canvas.create_rectangle(
                    0, 0, 30, max_height - white_height,
                    fill='black'
                )
                
                # Create white section (bottom)
                self.eval_bar_white = self.eval_canvas.create_rectangle(
                    0, max_height - white_height, 30, max_height,
                    fill='white'
                )
                
                # Update text
                text = f"+{abs(score):.1f}" if score > 0 else f"{score:.1f}"
                self.eval_canvas.itemconfig(self.eval_text, text=text)
                
            else:  # Mate
                score = eval['value']
                self.eval_canvas.delete(self.eval_bar_black)  # Remove old black section
                self.eval_canvas.delete(self.eval_bar_white)  # Remove old white section
                
                if score > 0:  # White is winning
                    # Fill entire bar with white
                    self.eval_bar_white = self.eval_canvas.create_rectangle(
                        0, 0, 30, max_height,
                        fill='white'
                    )
                else:  # Black is winning
                    # Fill entire bar with black
                    self.eval_bar_black = self.eval_canvas.create_rectangle(
                        0, 0, 30, max_height,
                        fill='black'
                    )
                self.eval_canvas.itemconfig(self.eval_text, text=f"M{abs(score)}")
                
        except Exception as e:
            print(f"Error getting evaluation: {e}")

    def make_stockfish_move(self):
        if not self.stockfish:
            print("Stockfish not initialized")
            return
            
        # Update Stockfish with current position
        try:
            self.stockfish.set_position([move[0] + move[1] for move in self.game.move_history])
        except Exception as e:
            print(f"Error setting position: {e}")
            return

        # Get best move from Stockfish
        try:
            best_move = self.stockfish.get_best_move()
            if best_move:
                start = best_move[:2]
                end = best_move[2:4]
                print(f"Stockfish move: {start} to {end}")  # Debug print
                
                if self.game.make_move(start, end):
                    self.update_display()
                    self.update_evaluation()  # Update evaluation after move
                    self.check_game_state()
                    print(f"Current position after move: {self.game.move_history}")  # Debug print
        except Exception as e:
            print(f"Error getting best move: {e}")

    def setup_board(self):
        colors = ['white', 'gray']
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                btn = tk.Button(self.window, width=5, height=2, bg=color,
                              command=lambda r=row, c=col: self.square_clicked(r, c))
                btn.grid(row=row, column=col)
                self.buttons[row][col] = btn
        self.update_display()

    def update_display(self):
        piece_symbols = {
            'wp': '♙', 'wr': '♖', 'wn': '♘', 'wb': '♗', 'wq': '♕', 'wk': '♔',
            'bp': '♟', 'br': '♜', 'bn': '♞', 'bb': '♝', 'bq': '♛', 'bk': '♚'
        }
        
        for row in range(8):
            for col in range(8):
                piece = self.game.board[row][col]
                text = ''
                if piece:
                    text = piece_symbols[str(piece)]
                self.buttons[row][col].config(text=text, font=('Arial', 20))

    def square_clicked(self, row: int, col: int):
        if self.self_play:
            return
            
        # If it's AI's turn (Black) and VS AI mode is on, ignore clicks
        if self.vs_ai and self.game.current_player == Color.BLACK:
            return

        if self.selected_square is None:
            piece = self.game.board[row][col]
            if piece and piece.color == self.game.current_player:
                self.selected_square = (row, col)
                self.buttons[row][col].config(bg='yellow')
        else:
            start_row, start_col = self.selected_square
            start = f"{chr(start_col + ord('a'))}{8-start_row}"
            end = f"{chr(col + ord('a'))}{8-row}"
            
            if self.game.make_move(start, end):
                self.update_display()
                self.update_evaluation()  # Update evaluation after move
                self.check_game_state()
                print(f"Player move: {start} to {end}")  # Debug print
                
                if self.vs_ai and self.game.current_player == Color.BLACK:
                    self.window.after(500, self.make_stockfish_move)
            
            # Reset selection
            self.buttons[start_row][start_col].config(bg='white' if (start_row + start_col) % 2 == 0 else 'gray')
            self.selected_square = None

    def check_game_state(self):
        if self.game.is_checkmate(self.game.current_player):
            winner = "Black" if self.game.current_player == Color.WHITE else "White"
            messagebox.showinfo("Game Over", f"Checkmate! {winner} wins!")
            if self.self_play:
                self.self_play = False
                self.self_play_button.config(text="Self Play")
        elif self.game.is_stalemate(self.game.current_player):
            messagebox.showinfo("Game Over", "Stalemate! The game is a draw.")
            if self.self_play:
                self.self_play = False
                self.self_play_button.config(text="Self Play")
        elif self.game.is_in_check(self.game.current_player):
            if not self.self_play:  # Don't show check messages during self-play
                messagebox.showinfo("Check", f"{self.game.current_player.value} is in check!")

    def run(self):
        self.window.mainloop()

def main():
    gui = ChessGUI()
    gui.run()

if __name__ == "__main__":
    main() 