from enum import Enum
from typing import List, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.chess_board import ChessBoard

class PieceType(Enum):
    PAWN = "pawn"
    ROOK = "rook"
    KNIGHT = "knight"
    BISHOP = "bishop"
    QUEEN = "queen"
    KING = "king"

class Color(Enum):
    WHITE = "white"
    BLACK = "black"

class Piece:
    def __init__(self, piece_type: PieceType, color: Color, row: int, col: int):
        self.piece_type = piece_type
        self.color = color
        self.row = row
        self.col = col
        self.has_moved = False
        
    def get_symbol(self) -> str:

        symbols = {
            (PieceType.PAWN, Color.WHITE): "P",
            (PieceType.ROOK, Color.WHITE): "R",
            (PieceType.KNIGHT, Color.WHITE): "N",
            (PieceType.BISHOP, Color.WHITE): "B",
            (PieceType.QUEEN, Color.WHITE): "Q",
            (PieceType.KING, Color.WHITE): "K",
            (PieceType.PAWN, Color.BLACK): "p",
            (PieceType.ROOK, Color.BLACK): "r",
            (PieceType.KNIGHT, Color.BLACK): "n",
            (PieceType.BISHOP, Color.BLACK): "b",
            (PieceType.QUEEN, Color.BLACK): "q",
            (PieceType.KING, Color.BLACK): "k",
        }
        return symbols.get((self.piece_type, self.color), "?")
    
    def get_valid_moves(self, board: 'ChessBoard') -> List[Tuple[int, int]]:

        moves = []
        
        if self.piece_type == PieceType.PAWN:
            moves = self._get_pawn_moves(board)
        elif self.piece_type == PieceType.ROOK:
            moves = self._get_rook_moves(board)
        elif self.piece_type == PieceType.KNIGHT:
            moves = self._get_knight_moves(board)
        elif self.piece_type == PieceType.BISHOP:
            moves = self._get_bishop_moves(board)
        elif self.piece_type == PieceType.QUEEN:
            moves = self._get_queen_moves(board)
        elif self.piece_type == PieceType.KING:
            moves = self._get_king_moves(board)
            
        return moves
    
    def _get_pawn_moves(self, board: 'ChessBoard') -> List[Tuple[int, int]]:
        moves = []
        direction = -1 if self.color == Color.WHITE else 1
        start_row = 6 if self.color == Color.WHITE else 1
        
        
        new_row = self.row + direction
        if 0 <= new_row < 8 and board.get_piece(new_row, self.col) is None:
            moves.append((new_row, self.col))
            
          
            if self.row == start_row:
                new_row = self.row + 2 * direction
                if 0 <= new_row < 8 and board.get_piece(new_row, self.col) is None:
                    moves.append((new_row, self.col))
        
      
        for col_offset in [-1, 1]:
            new_col = self.col + col_offset
            new_row = self.row + direction
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                piece = board.get_piece(new_row, new_col)
                if piece is not None and piece.color != self.color:
                    moves.append((new_row, new_col))
        
        return moves
    
    def _get_rook_moves(self, board: 'ChessBoard') -> List[Tuple[int, int]]:
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row = self.row + dr * i
                new_col = self.col + dc * i
                
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                    
                piece = board.get_piece(new_row, new_col)
                if piece is None:
                    moves.append((new_row, new_col))
                elif piece.color != self.color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        return moves
    
    def _get_knight_moves(self, board: 'ChessBoard') -> List[Tuple[int, int]]:
        moves = []
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1)]
        
        for dr, dc in knight_moves:
            new_row = self.row + dr
            new_col = self.col + dc
            
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                piece = board.get_piece(new_row, new_col)
                if piece is None or piece.color != self.color:
                    moves.append((new_row, new_col))
        
        return moves
    
    def _get_bishop_moves(self, board: 'ChessBoard') -> List[Tuple[int, int]]:
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row = self.row + dr * i
                new_col = self.col + dc * i
                
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                    
                piece = board.get_piece(new_row, new_col)
                if piece is None:
                    moves.append((new_row, new_col))
                elif piece.color != self.color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        return moves
    
    def _get_queen_moves(self, board: 'ChessBoard') -> List[Tuple[int, int]]:

        return self._get_rook_moves(board) + self._get_bishop_moves(board)
    
    def _get_king_moves(self, board: 'ChessBoard') -> List[Tuple[int, int]]:
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0),
                     (1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for dr, dc in directions:
            new_row = self.row + dr
            new_col = self.col + dc
            
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                piece = board.get_piece(new_row, new_col)
                if piece is None or piece.color != self.color:
                    moves.append((new_row, new_col))
        
        return moves
    
    def move_to(self, row: int, col: int):

        self.row = row
        self.col = col
        self.has_moved = True
    
    def copy(self) -> 'Piece':
        new_piece = Piece(self.piece_type, self.color, self.row, self.col)
        new_piece.has_moved = self.has_moved
        return new_piece
