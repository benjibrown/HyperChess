import pygame
import random
from typing import List, Tuple, Optional, Dict
from src.chess_board import ChessBoard
from src.pieces import Color
from src.chess_ai import ChessAI

class UltimateChessBoard:
    def __init__(self, game_mode: str = "2player", ai_difficulty: str = "medium"):
        # Create 8x8 grid of chess boards
        self.boards: List[List[ChessBoard]] = []
        for row in range(8):
            board_row = []
            for col in range(8):
                board_row.append(ChessBoard())
            self.boards.append(board_row)
        
        # Game state
        self.current_player = Color.WHITE
        self.current_board = (3, 3)  # Start in the middle board (d4)
        self.game_over = False
        self.winner: Optional[Color] = None
        
        # Game mode settings
        self.game_mode = game_mode  # "2player" or "vs_cpu"
        self.ai_difficulty = ai_difficulty
        self.ai = ChessAI(Color.BLACK, ai_difficulty) if game_mode == "vs_cpu" else None
        
        # Track which boards are won
        self.won_boards: List[List[Optional[Color]]] = [[None for _ in range(8)] for _ in range(8)]
        
        # Track the sequence of moves for determining next board
        # Each entry: (board_row, board_col, from_row, from_col, to_row, to_col)
        self.move_history: List[Tuple[int, int, int, int, int, int]] = []

        # Dual-move system: track moves per board
        self.moves_on_current_board = 0
        self.max_moves_per_board = 2
    
    def get_current_board(self) -> ChessBoard:
        """Get the currently active board"""
        row, col = self.current_board
        return self.boards[row][col]
    
    def make_move(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Make a move on the current board"""
        current_board = self.get_current_board()
        
        # Check if current board is already won
        if current_board.is_won:
            return False
        
        # Try to make the move
        if not current_board.move_piece(from_row, from_col, to_row, to_col):
            return False
        
        # Record the move with both source and destination so UI can animate exactly
        board_row, board_col = self.current_board
        self.move_history.append((board_row, board_col, from_row, from_col, to_row, to_col))
        self.moves_on_current_board += 1
        
        # Check if this board is now won
        if current_board.is_won:
            self.won_boards[board_row][board_col] = current_board.winner
            # Check if this creates a win in the ultimate board (only if winner is set)
            if current_board.winner is not None and self._check_ultimate_win(board_row, board_col, current_board.winner):
                self.game_over = True
                self.winner = current_board.winner
                return True
        
        # Determine next board based on dual-move system
        if self.moves_on_current_board >= self.max_moves_per_board:
            # Switch to the board corresponding to the last move
            self._determine_next_board(to_row, to_col)
            self.moves_on_current_board = 0
        else:
            # Stay on current board for second move
            pass
        
        # Switch players
        self.current_player = Color.BLACK if self.current_player == Color.WHITE else Color.WHITE
        
        return True
    
    def _determine_next_board(self, piece_row: int, piece_col: int):
        """Determine which board to play on next based on the piece position"""
        # Convert chess notation to board coordinates
        board_row = piece_row
        board_col = piece_col
        
        # Check if the target board is won
        if self.won_boards[board_row][board_col] is not None:
            # Find a random available board
            available_boards = []
            for r in range(8):
                for c in range(8):
                    if self.won_boards[r][c] is None:
                        available_boards.append((r, c))
            
            if available_boards:
                self.current_board = random.choice(available_boards)
            else:
                # All boards are won, game should be over
                self.game_over = True
        else:
            self.current_board = (board_row, board_col)
    
    def _check_ultimate_win(self, board_row: int, board_col: int, winner: Color) -> bool:
        """Check if winning this board creates a win in the ultimate game"""
        # Check horizontal line
        count = 1
        # Check left
        for c in range(board_col - 1, -1, -1):
            if self.won_boards[board_row][c] == winner:
                count += 1
            else:
                break
        # Check right
        for c in range(board_col + 1, 8):
            if self.won_boards[board_row][c] == winner:
                count += 1
            else:
                break
        
        if count >= 8:
            return True
        
        # Check vertical line
        count = 1
        # Check up
        for r in range(board_row - 1, -1, -1):
            if self.won_boards[r][board_col] == winner:
                count += 1
            else:
                break
        # Check down
        for r in range(board_row + 1, 8):
            if self.won_boards[r][board_col] == winner:
                count += 1
            else:
                break
        
        if count >= 8:
            return True
        
        # Check diagonal (top-left to bottom-right)
        count = 1
        # Check top-left
        r, c = board_row - 1, board_col - 1
        while r >= 0 and c >= 0:
            if self.won_boards[r][c] == winner:
                count += 1
                r -= 1
                c -= 1
            else:
                break
        # Check bottom-right
        r, c = board_row + 1, board_col + 1
        while r < 8 and c < 8:
            if self.won_boards[r][c] == winner:
                count += 1
                r += 1
                c += 1
            else:
                break
        
        if count >= 8:
            return True
        
        # Check diagonal (top-right to bottom-left)
        count = 1
        # Check top-right
        r, c = board_row - 1, board_col + 1
        while r >= 0 and c < 8:
            if self.won_boards[r][c] == winner:
                count += 1
                r -= 1
                c += 1
            else:
                break
        # Check bottom-left
        r, c = board_row + 1, board_col - 1
        while r < 8 and c >= 0:
            if self.won_boards[r][c] == winner:
                count += 1
                r += 1
                c -= 1
            else:
                break
        
        if count >= 8:
            return True
        
        return False
    
    def get_valid_moves(self) -> List[Tuple[int, int, int, int]]:
        """Get all valid moves for the current player on the current board"""
        current_board = self.get_current_board()
        
        if current_board.is_won:
            return []
        
        return current_board.get_valid_moves_for_color(self.current_player)
    
    def get_board_position(self, board_row: int, board_col: int) -> Tuple[int, int]:
        """Convert board coordinates to screen position"""
        # This will be used by the UI to position boards
        board_size = 80  # Size of each individual board
        spacing = 10     # Space between boards
        
        x = board_col * (board_size + spacing)
        y = board_row * (board_size + spacing)
        
        return (x, y)
    
    def get_current_board_position(self) -> Tuple[int, int]:
        """Get the screen position of the current active board"""
        board_row, board_col = self.current_board
        return self.get_board_position(board_row, board_col)
    
    def is_board_won(self, board_row: int, board_col: int) -> bool:
        """Check if a specific board is won"""
        return self.won_boards[board_row][board_col] is not None
    
    def get_board_winner(self, board_row: int, board_col: int) -> Optional[Color]:
        """Get the winner of a specific board"""
        return self.won_boards[board_row][board_col]
    
    def get_game_state(self) -> Dict:
        """Get the current game state"""
        return {
            'current_player': self.current_player,
            'current_board': self.current_board,
            'game_over': self.game_over,
            'winner': self.winner,
            'won_boards': self.won_boards,
            'move_history': self.move_history
        }
    
    def reset_game(self):
        """Reset the game to initial state"""
        # Reset all boards
        for row in range(8):
            for col in range(8):
                self.boards[row][col] = ChessBoard()
        
        # Reset game state
        self.current_player = Color.WHITE
        self.current_board = (3, 3)
        self.game_over = False
        self.winner = None
        self.won_boards = [[None for _ in range(8)] for _ in range(8)]
        self.move_history = []
        self.moves_on_current_board = 0
    
    def set_game_mode(self, game_mode: str, ai_difficulty: str = "medium"):
        """Set the game mode and AI difficulty"""
        self.game_mode = game_mode
        self.ai_difficulty = ai_difficulty
        if game_mode == "vs_cpu":
            self.ai = ChessAI(Color.BLACK, ai_difficulty)
        else:
            self.ai = None
    
    def is_ai_turn(self) -> bool:
        """Check if it's the AI's turn"""
        return (self.game_mode == "vs_cpu" and 
                self.current_player == Color.BLACK and 
                self.ai is not None)
    
    def get_ai_move(self) -> Optional[Tuple[int, int, int, int]]:
        """Get the AI's move"""
        if not self.is_ai_turn():
            return None
        
        current_board = self.get_current_board()
        return self.ai.get_move(current_board) if self.ai is not None else None
    
    def make_ai_move(self) -> bool:
        """Make the AI's move"""
        if not self.is_ai_turn():
            return False
        
        ai_move = self.get_ai_move()
        if ai_move is None:
            return False
        
        from_row, from_col, to_row, to_col = ai_move
        return self.make_move(from_row, from_col, to_row, to_col)
    
    def get_board_coordinates_from_position(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """Convert screen position to board coordinates"""
        board_size = 80
        spacing = 10
        
        board_col = x // (board_size + spacing)
        board_row = y // (board_size + spacing)
        
        if 0 <= board_row < 8 and 0 <= board_col < 8:
            return (board_row, board_col)
        
        return None
    
    def get_piece_coordinates_from_position(self, x: int, y: int, board_row: int, board_col: int) -> Optional[Tuple[int, int]]:
        """Convert screen position to piece coordinates within a board"""
        board_size = 80
        spacing = 10
        
        # Get the board's screen position
        board_x, board_y = self.get_board_position(board_row, board_col)
        
        # Calculate relative position within the board
        rel_x = x - board_x
        rel_y = y - board_y
        
        # Convert to piece coordinates
        piece_col = rel_x // (board_size // 8)
        piece_row = rel_y // (board_size // 8)
        
        if 0 <= piece_row < 8 and 0 <= piece_col < 8:
            return (piece_row, piece_col)
        
        return None
