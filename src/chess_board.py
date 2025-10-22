import pygame
from typing import List, Tuple, Optional, Dict
from src.pieces import Piece, PieceType, Color

class ChessBoard:
    def __init__(self):
        self.board: List[List[Optional[Piece]]] = [[None for _ in range(8)] for _ in range(8)]
        self.winner: Optional[Color] = None
        self.is_won = False
        self._setup_initial_pieces()
    
    def _setup_initial_pieces(self):
        """Set up the initial chess pieces"""
        # Black pieces (top)
        self.board[0] = [
            Piece(PieceType.ROOK, Color.BLACK, 0, 0),
            Piece(PieceType.KNIGHT, Color.BLACK, 0, 1),
            Piece(PieceType.BISHOP, Color.BLACK, 0, 2),
            Piece(PieceType.QUEEN, Color.BLACK, 0, 3),
            Piece(PieceType.KING, Color.BLACK, 0, 4),
            Piece(PieceType.BISHOP, Color.BLACK, 0, 5),
            Piece(PieceType.KNIGHT, Color.BLACK, 0, 6),
            Piece(PieceType.ROOK, Color.BLACK, 0, 7),
        ]
        
        # black pawns
        for col in range(8):
            self.board[1][col] = Piece(PieceType.PAWN, Color.BLACK, 1, col)
        
        # white pieces (bottom)
        self.board[7] = [
            Piece(PieceType.ROOK, Color.WHITE, 7, 0),
            Piece(PieceType.KNIGHT, Color.WHITE, 7, 1),
            Piece(PieceType.BISHOP, Color.WHITE, 7, 2),
            Piece(PieceType.QUEEN, Color.WHITE, 7, 3),
            Piece(PieceType.KING, Color.WHITE, 7, 4),
            Piece(PieceType.BISHOP, Color.WHITE, 7, 5),
            Piece(PieceType.KNIGHT, Color.WHITE, 7, 6),
            Piece(PieceType.ROOK, Color.WHITE, 7, 7),
        ]
        
        # white pawns
        for col in range(8):
            self.board[6][col] = Piece(PieceType.PAWN, Color.WHITE, 6, col)
    
    def get_piece(self, row: int, col: int) -> Optional[Piece]:

        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None
    
    def set_piece(self, row: int, col: int, piece: Optional[Piece]):

        if 0 <= row < 8 and 0 <= col < 8:
            self.board[row][col] = piece
            if piece:
                piece.row = row
                piece.col = col
    
    def move_piece(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:

        piece = self.get_piece(from_row, from_col)
        if piece is None:
            return False
        
        # valid??
        valid_moves = piece.get_valid_moves(self)
        if (to_row, to_col) not in valid_moves:
            return False
        

        if self._would_be_in_check(piece, from_row, from_col, to_row, to_col):
            return False
        

        captured_piece = self.get_piece(to_row, to_col)
        self.set_piece(from_row, from_col, None)
        self.set_piece(to_row, to_col, piece)
        piece.move_to(to_row, to_col)
        

        if captured_piece and captured_piece.piece_type == PieceType.KING:
            self.winner = piece.color
            self.is_won = True
        
        return True
    
    def _would_be_in_check(self, piece: Piece, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:

        original_piece = self.get_piece(to_row, to_col)
        self.set_piece(from_row, from_col, None)
        self.set_piece(to_row, to_col, piece)
        
 
        king_pos = self._find_king(piece.color)
        in_check = self._is_in_check(king_pos[0], king_pos[1], piece.color)
        
        # Restore the board
        self.set_piece(from_row, from_col, piece)
        self.set_piece(to_row, to_col, original_piece)
        
        return in_check
    
    def _find_king(self, color: Color) -> Tuple[int, int]:

        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.piece_type == PieceType.KING and piece.color == color:
                    return (row, col)
        return (-1, -1)  # should never return this if game is valid
    
    def _is_in_check(self, king_row: int, king_col: int, king_color: Color) -> bool:

        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.color != king_color:
                    valid_moves = piece.get_valid_moves(self)
                    if (king_row, king_col) in valid_moves:
                        return True
        return False
    
    def get_all_pieces(self, color: Color) -> List[Piece]:

        pieces = []
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.color == color:
                    pieces.append(piece)
        return pieces
    
    def get_valid_moves_for_color(self, color: Color) -> List[Tuple[int, int, int, int]]:

        moves = []
        pieces = self.get_all_pieces(color)
        
        for piece in pieces:
            piece_moves = piece.get_valid_moves(self)
            for to_row, to_col in piece_moves:
                if not self._would_be_in_check(piece, piece.row, piece.col, to_row, to_col):
                    moves.append((piece.row, piece.col, to_row, to_col))
        
        return moves
    
    def is_checkmate(self, color: Color) -> bool:

        king_pos = self._find_king(color)
        if king_pos == (-1, -1):
            return True
        
       
        if not self._is_in_check(king_pos[0], king_pos[1], color):
            return False
        
       
        valid_moves = self.get_valid_moves_for_color(color)
        return len(valid_moves) == 0
    
    def is_stalemate(self, color: Color) -> bool:
        """Check if the given color is in stalemate"""
        king_pos = self._find_king(color)
        if king_pos == (-1, -1):
            return False
        
        
        if self._is_in_check(king_pos[0], king_pos[1], color):
            return False
        
       
        valid_moves = self.get_valid_moves_for_color(color)
        return len(valid_moves) == 0
    
    def copy(self) -> 'ChessBoard':

        new_board = ChessBoard()
        new_board.board = [[None for _ in range(8)] for _ in range(8)]
        new_board.winner = self.winner
        new_board.is_won = self.is_won
        
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece:
                    new_board.set_piece(row, col, piece.copy())
        
        return new_board
    
    def get_board_state(self) -> Dict:

        return {
            'board': self.board,
            'winner': self.winner,
            'is_won': self.is_won
        }
