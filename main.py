#!/usr/bin/env python3
"""
HyperChess
- Players must win 8 boards in a row to win the overall game.

Rules:
- Start in the middle board (d4)
- After making a move, the next player must play on the board corresponding to 
  the square where the piece was moved
- If a board is already won, play on any available board
- Win a board by capturing the opponent's king
- Win the game by getting 8 boards in a row
"""

import sys
import os


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ui import UltimateChessUI

def main():
    """Main entry point for HyperChess"""
    print("Welcome to HyperChess!")
    print("Rules:")
    print("- Start in the middle board (d4)")
    print("- After moving a piece, the next player plays on the board corresponding to that square")
    print("- If a board is already won, play on any available board")
    print("- Win a board by capturing the opponent's king")
    print("- Win the game by getting 8 boards in a row!")
    print("\nPress R to reset the game at any time.")
    print("Click on a piece to select it, then click on a valid move.")
    print("\nStarting game...")
    
    # run :)
    game_ui = UltimateChessUI()
    game_ui.run()

if __name__ == "__main__":
    main()
