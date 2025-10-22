import pygame
from typing import Tuple
from src.pieces import Piece, PieceType, Color

class PieceRenderer:
    def __init__(self):
        self.piece_colors = {
            Color.WHITE: (255, 255, 255),
            Color.BLACK: (50, 50, 50)
        }
        self.outline_color = (0, 0, 0)
        self.outline_width = 2

        
        self.shadow_offset = (4, 6)
    
    def draw_piece(self, screen: pygame.Surface, piece: Piece, x: int, y: int, size: int):

        if piece.color == Color.WHITE:
            fill_color = (245, 245, 245)
            outline_color = (30, 30, 30)
        else:
            fill_color = (40, 40, 40)
            outline_color = (200, 200, 200)
        
        center_x = x + size // 2
        center_y = y + size // 2
        radius = size // 3

      
        shadow_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 100), (self.shadow_offset[0], self.shadow_offset[1], size - self.shadow_offset[0]*2, size // 3))
        screen.blit(shadow_surf, (x, y))

        
        grad_steps = 3
        for i in range(grad_steps, 0, -1):
            step_radius = int(radius * (i / grad_steps))
            shade = tuple(max(0, min(255, int(fill_color[j] * (0.9 + 0.1 * (i / grad_steps))))) for j in range(3))
            pygame.draw.circle(screen, shade, (center_x, center_y), step_radius)
        
        if piece.piece_type == PieceType.PAWN:
            self._draw_pawn(screen, center_x, center_y, radius, fill_color, outline_color)
        elif piece.piece_type == PieceType.ROOK:
            self._draw_rook(screen, center_x, center_y, radius, fill_color, outline_color)
        elif piece.piece_type == PieceType.KNIGHT:
            self._draw_knight(screen, center_x, center_y, radius, fill_color, outline_color)
        elif piece.piece_type == PieceType.BISHOP:
            self._draw_bishop(screen, center_x, center_y, radius, fill_color, outline_color)
        elif piece.piece_type == PieceType.QUEEN:
            self._draw_queen(screen, center_x, center_y, radius, fill_color, outline_color)
        elif piece.piece_type == PieceType.KING:
            self._draw_king(screen, center_x, center_y, radius, fill_color, outline_color)
    
    def _draw_pawn(self, screen: pygame.Surface, x: int, y: int, radius: int, fill_color: Tuple[int, int, int], outline_color: Tuple[int, int, int]):
        """Draw a pawn"""
        pygame.draw.circle(screen, outline_color, (x, y), radius, self.outline_width)
        
       
        head_radius = radius // 2
        pygame.draw.circle(screen, fill_color, (x, y - radius // 2), head_radius)
        pygame.draw.circle(screen, outline_color, (x, y - radius // 2), head_radius, self.outline_width)
    
    def _draw_rook(self, screen: pygame.Surface, x: int, y: int, radius: int, fill_color: Tuple[int, int, int], outline_color: Tuple[int, int, int]):

        rect = pygame.Rect(x - radius, y - radius // 2, radius * 2, radius)
        pygame.draw.rect(screen, fill_color, rect)
        pygame.draw.rect(screen, outline_color, rect, self.outline_width)
        
    
        battlement_height = radius // 3
        for i in range(3):
            battlement_x = x - radius + (i * radius)
            battlement_rect = pygame.Rect(battlement_x, y - radius // 2 - battlement_height, radius // 2, battlement_height)
            pygame.draw.rect(screen, fill_color, battlement_rect)
            pygame.draw.rect(screen, outline_color, battlement_rect, self.outline_width)
    
    def _draw_knight(self, screen: pygame.Surface, x: int, y: int, radius: int, fill_color: Tuple[int, int, int], outline_color: Tuple[int, int, int]):

        pygame.draw.circle(screen, outline_color, (x, y), radius, self.outline_width)
        
        # head
        head_points = [
            (x + radius // 2, y - radius // 2),
            (x + radius, y),
            (x + radius // 2, y + radius // 2),
            (x, y)
        ]
        pygame.draw.polygon(screen, fill_color, head_points)
        pygame.draw.polygon(screen, outline_color, head_points, self.outline_width)
    
    def _draw_bishop(self, screen: pygame.Surface, x: int, y: int, radius: int, fill_color: Tuple[int, int, int], outline_color: Tuple[int, int, int]):

        pygame.draw.circle(screen, outline_color, (x, y), radius, self.outline_width)


        mitre_height = radius // 2
        mitre_points = [
            (x - radius // 2, y - radius // 2),
            (x + radius // 2, y - radius // 2),
            (x, y - radius // 2 - mitre_height)
        ]
        pygame.draw.polygon(screen, fill_color, mitre_points)
        pygame.draw.polygon(screen, outline_color, mitre_points, self.outline_width)

 
        cross_size = radius // 4
        pygame.draw.line(screen, outline_color, 
                        (x - cross_size, y - radius // 2 - mitre_height // 2),
                        (x + cross_size, y - radius // 2 - mitre_height // 2), self.outline_width)
        pygame.draw.line(screen, outline_color,
                        (x, y - radius // 2 - mitre_height // 2 - cross_size),
                        (x, y - radius // 2 - mitre_height // 2 + cross_size), self.outline_width)
    
    def _draw_queen(self, screen: pygame.Surface, x: int, y: int, radius: int, fill_color: Tuple[int, int, int], outline_color: Tuple[int, int, int]):
        """Draw a queen"""

        pygame.draw.circle(screen, outline_color, (x, y), radius, self.outline_width)
        

        crown_height = radius // 2
        crown_points = [
            (x - radius // 2, y - radius // 2),
            (x - radius // 4, y - radius // 2 - crown_height),
            (x, y - radius // 2),
            (x + radius // 4, y - radius // 2 - crown_height),
            (x + radius // 2, y - radius // 2)
        ]
        pygame.draw.polygon(screen, fill_color, crown_points)
        pygame.draw.polygon(screen, outline_color, crown_points, self.outline_width)
        

        jewel_radius = radius // 8
        pygame.draw.circle(screen, outline_color, (x - radius // 4, y - radius // 2 - crown_height // 2), jewel_radius)
        pygame.draw.circle(screen, outline_color, (x + radius // 4, y - radius // 2 - crown_height // 2), jewel_radius)
    
    def _draw_king(self, screen: pygame.Surface, x: int, y: int, radius: int, fill_color: Tuple[int, int, int], outline_color: Tuple[int, int, int]):
        """Draw a king"""

        pygame.draw.circle(screen, outline_color, (x, y), radius, self.outline_width)
        
        
   
        crown_height = radius // 2
        crown_points = [
            (x - radius // 2, y - radius // 2),
            (x - radius // 4, y - radius // 2 - crown_height),
            (x, y - radius // 2 - crown_height // 2),
            (x + radius // 4, y - radius // 2 - crown_height),
            (x + radius // 2, y - radius // 2)
        ]
        pygame.draw.polygon(screen, fill_color, crown_points)
        pygame.draw.polygon(screen, outline_color, crown_points, self.outline_width)
        
      
        cross_size = radius // 3
        pygame.draw.line(screen, outline_color,
                        (x - cross_size // 2, y - radius // 2 - crown_height),
                        (x + cross_size // 2, y - radius // 2 - crown_height), self.outline_width)
        pygame.draw.line(screen, outline_color,
                        (x, y - radius // 2 - crown_height - cross_size),
                        (x, y - radius // 2 - crown_height), self.outline_width)
