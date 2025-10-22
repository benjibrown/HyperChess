#!/usr/bin/env python3


import pygame
import sys
import os

# Add the chess directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.pieces import Piece, PieceType, Color
from src.piece_renderer import PieceRenderer

def preview_pieces():
    """Show a preview of all chess pieces"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Chess Piece Preview")
    
    piece_renderer = PieceRenderer()
    
    # Colors
    LIGHT_BROWN = (240, 217, 181)
    DARK_BROWN = (181, 136, 99)
    BLACK = (0, 0, 0)
    
    # Create all pieces
    pieces = [
        # White pieces
        Piece(PieceType.PAWN, Color.WHITE, 0, 0),
        Piece(PieceType.ROOK, Color.WHITE, 0, 1),
        Piece(PieceType.KNIGHT, Color.WHITE, 0, 2),
        Piece(PieceType.BISHOP, Color.WHITE, 0, 3),
        Piece(PieceType.QUEEN, Color.WHITE, 0, 4),
        Piece(PieceType.KING, Color.WHITE, 0, 5),
        
        # Black pieces
        Piece(PieceType.PAWN, Color.BLACK, 1, 0),
        Piece(PieceType.ROOK, Color.BLACK, 1, 1),
        Piece(PieceType.KNIGHT, Color.BLACK, 1, 2),
        Piece(PieceType.BISHOP, Color.BLACK, 1, 3),
        Piece(PieceType.QUEEN, Color.BLACK, 1, 4),
        Piece(PieceType.KING, Color.BLACK, 1, 5),
    ]
    
    piece_names = [
        "Pawn", "Rook", "Knight", "Bishop", "Queen", "King",
        "Pawn", "Rook", "Knight", "Bishop", "Queen", "King"
    ]
    
    colors = ["White", "White", "White", "White", "White", "White",
              "Black", "Black", "Black", "Black", "Black", "Black"]
    
    font = pygame.font.Font(None, 24)
    title_font = pygame.font.Font(None, 36)
    
    running = True
    clock = pygame.time.Clock()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        screen.fill((255, 255, 255))
        
        # Draw title
        title_text = title_font.render("Chess Piece Preview", True, BLACK)
        screen.blit(title_text, (300, 50))
        
        # Draw pieces
        piece_size = 80
        start_x = 100
        start_y = 150
        
        for i, piece in enumerate(pieces):
            x = start_x + (i % 6) * 100
            y = start_y + (i // 6) * 150
            
            # Draw background square
            square_color = LIGHT_BROWN if (i % 6 + i // 6) % 2 == 0 else DARK_BROWN
            pygame.draw.rect(screen, square_color, (x, y, piece_size, piece_size))
            pygame.draw.rect(screen, BLACK, (x, y, piece_size, piece_size), 2)
            
            # Draw piece
            piece_renderer.draw_piece(screen, piece, x, y, piece_size)
            
            # Draw piece name
            name_text = font.render(piece_names[i], True, BLACK)
            screen.blit(name_text, (x, y + piece_size + 5))
            
            # Draw color
            color_text = font.render(colors[i], True, BLACK)
            screen.blit(color_text, (x, y + piece_size + 25))
        
        # Draw instructions
        instructions = [
            "These are the chess pieces used in Ultimate Chess",
            "Press ESC to close this preview",
            "The pieces are drawn using pygame graphics (no images needed!)"
        ]
        
        y_offset = 500
        for instruction in instructions:
            text = font.render(instruction, True, BLACK)
            screen.blit(text, (50, y_offset))
            y_offset += 25
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    preview_pieces()
