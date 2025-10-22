import random
from typing import List, Tuple, Optional
from src.pieces import Color, PieceType
from src.chess_board import ChessBoard

class ChessAI:
    def __init__(self, color: Color, difficulty: str = "medium"):
        self.color = color
        self.difficulty = difficulty
        

        self.piece_values = {
            PieceType.PAWN: 1,
            PieceType.KNIGHT: 3,
            PieceType.BISHOP: 3,
            PieceType.ROOK: 5,
            PieceType.QUEEN: 9,
            PieceType.KING: 100
        }
    
    def get_move(self, board: ChessBoard) -> Optional[Tuple[int, int, int, int]]:

        valid_moves = board.get_valid_moves_for_color(self.color)
        
        if not valid_moves:
            return None
        
        if self.difficulty == "easy":
            return self._get_random_move(valid_moves)
        elif self.difficulty == "medium":
            return self._get_medium_move(board, valid_moves)
        else:  # hard
            return self._get_hard_move(board, valid_moves)
    
    def _get_random_move(self, valid_moves: List[Tuple[int, int, int, int]]) -> Tuple[int, int, int, int]:

        return random.choice(valid_moves)
    
    def _get_medium_move(self, board: ChessBoard, valid_moves: List[Tuple[int, int, int, int]]) -> Tuple[int, int, int, int]:

        best_moves = []
        best_score = float('-inf')
        
        for move in valid_moves:
            from_row, from_col, to_row, to_col = move
            piece = board.get_piece(from_row, from_col)
            target_piece = board.get_piece(to_row, to_col)
            
            score = 0
            

            if target_piece:
                score += self.piece_values.get(target_piece.piece_type, 0) * 10
            

            center_distance = abs(to_row - 3.5) + abs(to_col - 3.5)
            score += (7 - center_distance) * 0.5
            

            if piece and piece.piece_type == PieceType.PAWN:
                if self.color == Color.WHITE and to_row < from_row:
                    score += 1
                elif self.color == Color.BLACK and to_row > from_row:
                    score += 1
            

            if self._is_square_attacked(board, to_row, to_col, self.color):
                score -= 5
            
            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
        
        return random.choice(best_moves)
    
    def _get_hard_move(self, board: ChessBoard, valid_moves: List[Tuple[int, int, int, int]]) -> Tuple[int, int, int, int]:

        best_move = None
        best_score = float('-inf')
        
        for move in valid_moves:
            # make move
            from_row, from_col, to_row, to_col = move
            original_piece = board.get_piece(to_row, to_col)
            moving_piece = board.get_piece(from_row, from_col)
            
            board.set_piece(from_row, from_col, None)
            board.set_piece(to_row, to_col, moving_piece)
            if moving_piece:
                moving_piece.move_to(to_row, to_col)
            
            # eval position
            score = self._minimax(board, 2, False, float('-inf'), float('inf'))
            
            # undo
            board.set_piece(from_row, from_col, moving_piece)
            board.set_piece(to_row, to_col, original_piece)
            if moving_piece:
                moving_piece.move_to(from_row, from_col)
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move if best_move else random.choice(valid_moves)
    
    def _minimax(self, board: ChessBoard, depth: int, maximizing: bool, alpha: float, beta: float) -> float:

        if depth == 0:
            return self._evaluate_position(board)
        
        if maximizing:
            max_eval = float('-inf')
            valid_moves = board.get_valid_moves_for_color(self.color)
            
            for move in valid_moves:
                from_row, from_col, to_row, to_col = move
                original_piece = board.get_piece(to_row, to_col)
                moving_piece = board.get_piece(from_row, from_col)
                
                # move
                board.set_piece(from_row, from_col, None)
                board.set_piece(to_row, to_col, moving_piece)
                if moving_piece:
                    moving_piece.move_to(to_row, to_col)
                
                eval_score = self._minimax(board, depth - 1, False, alpha, beta)
                
                # undo move
                board.set_piece(from_row, from_col, moving_piece)
                board.set_piece(to_row, to_col, original_piece)
                if moving_piece:
                    moving_piece.move_to(from_row, from_col)
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break
            
            return max_eval
        else:
            min_eval = float('inf')
            opponent_color = Color.BLACK if self.color == Color.WHITE else Color.WHITE
            valid_moves = board.get_valid_moves_for_color(opponent_color)
            
            for move in valid_moves:
                from_row, from_col, to_row, to_col = move
                original_piece = board.get_piece(to_row, to_col)
                moving_piece = board.get_piece(from_row, from_col)
                
                # move
                board.set_piece(from_row, from_col, None)
                board.set_piece(to_row, to_col, moving_piece)
                if moving_piece:
                    moving_piece.move_to(to_row, to_col)
                
                eval_score = self._minimax(board, depth - 1, True, alpha, beta)
                
                # uundo move
                board.set_piece(from_row, from_col, moving_piece)
                board.set_piece(to_row, to_col, original_piece)
                if moving_piece:
                    moving_piece.move_to(from_row, from_col)
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break
            
            return min_eval
    
    def _evaluate_position(self, board: ChessBoard) -> float:

        score = 0
        
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece:
                    piece_value = self.piece_values.get(piece.piece_type, 0)
                    
                    if piece.color == self.color:
                        score += piece_value
                    else:
                        score -= piece_value
        
        return score
    
    def _is_square_attacked(self, board: ChessBoard, row: int, col: int, by_color: Color) -> bool:

        for r in range(8):
            for c in range(8):
                piece = board.get_piece(r, c)
                if piece and piece.color == by_color:
                    valid_moves = piece.get_valid_moves(board)
                    if (row, col) in valid_moves:
                        return True
        return False
