import pygame
import sys
import time
import math
from typing import Optional, Tuple
from src.ultimate_chess_board import UltimateChessBoard
from src.pieces import Color, PieceType, Piece
from src.piece_renderer import PieceRenderer

class UltimateChessUI:
    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        pygame.init()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Ultimate Chess")
        
        # colours
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.LIGHT_BROWN = (240, 217, 181)
        self.DARK_BROWN = (181, 136, 99)
        self.HIGHLIGHT = (255, 255, 0)
        self.CURRENT_BOARD_HIGHLIGHT = (0, 255, 0)
        self.WON_BOARD_HIGHLIGHT = (255, 0, 0)
        self.MOVE_HIGHLIGHT = (0, 255, 255)
        self.BUTTON_COLOR = (100, 100, 100)
        self.BUTTON_HOVER = (150, 150, 150)
        self.MENU_BG = (50, 50, 50)
        self.TRANSITION_COLOR = (255, 255, 255)
        
        # board settings
        self.board_size = 60 
        self.spacing = 8
        self.piece_size = 6
        
        # Zoom settings
        self.zoom_level = 0  
        self.zoomed_board_size = 400
        self.zoomed_piece_size = 40
        
        # Game state
        self.game = UltimateChessBoard()
        self.selected_piece: Optional[Tuple[int, int]] = None
        self.valid_moves: list = []
        self.show_menu = True
        self.game_mode = "2player"
        self.ai_difficulty = "medium"
        # UI / debug flags
        self.debug_mode = False
        # menu open animation
        self.menu_open_start = 0
        self.menu_open_duration = 450
        
        # animation and transition state
        self.transition_alpha = 0
        self.transition_duration = 500  
        self.transition_start_time = 0
        self.is_transitioning = False
        self.transition_type = "board_change"  #
        
        self.transition_pre_surf = None
        self.transition_post_surf = None
        
        # timing for luh ai
        self.ai_move_timer = 0
        self.ai_move_delay = 2000  
        self.ai_thinking_text = ""
        self.ai_thinking_timer = 0


        self.pending_board_swap = False
        self.post_move_delay = 800  
        self.pending_swap_start_time = 0
        
        # make the ui nice
        self.board_pulse_alpha = 0
        self.board_pulse_direction = 1
        self.last_board_change_time = 0


        self.animating_piece = None  
        self.animation_duration = 300  
        self.animation_start_time = 0
        
        
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 16)
        self.large_font = pygame.font.Font(None, 36)
        self.bold_font = pygame.font.Font(None, 28)
        

        self.piece_renderer = PieceRenderer()

        # Menu button rects (filled during draw_menu)
        self._menu_buttons = {}
        # Menu layout constants and state
        self.MENU_BUTTON_WIDTH = 360
        self.MENU_BUTTON_HEIGHT = 56
        self.MENU_BUTTON_GAP = 18
        self.MENU_TOP_Y = 200
        self.menu_items = ["2 Players", "VS CPU"]
        self.menu_selected = 0
        self.menu_press_start = 0
        self.menu_press_duration = 160

        # Keybinds panel state
        self.show_keybinds = False
        self.keybinds_rect = pygame.Rect(12, 12, 340, 240)
        self.keybinds_toggle_rect = pygame.Rect(12, 12, 44, 30)
        self.keybinds_hover = False
        # Keybinds animation (slide in/out)
        self.keybinds_anim_start = 0
        self.keybinds_anim_duration = 300
        # Piece legend state
        self.show_piece_legend = False


        # IMPLEMENT LATER !!!
        self.snd_hover = None
        self.snd_click = None
        try:
            pygame.mixer.init()
            try:
                self.snd_hover = pygame.mixer.Sound('assets/sounds/hover.wav')
            except Exception:
                self.snd_hover = None
            try:
                self.snd_click = pygame.mixer.Sound('assets/sounds/click.wav')
            except Exception:
                self.snd_click = None
        except Exception:

            self.snd_hover = None
            self.snd_click = None


        total_width = 8 * self.board_size + 7 * self.spacing
        total_height = 8 * self.board_size + 7 * self.spacing
        self.offset_x = (screen_width - total_width) // 2
        self.offset_y = (screen_height - total_height) // 2
    
    def run(self):


        self.run_splash()

        clock = pygame.time.Clock()
        running = True
        
        while running:
            dt = clock.tick(60)
            current_time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:

                    if self.show_menu:
                       
                        if event.key == pygame.K_1:
                            self.game_mode = "2player"
                            self.start_game()
                            continue
                        elif event.key == pygame.K_2:
                            self.game_mode = "vs_cpu"
                            self.show_difficulty_menu = True
                            continue
                        # Arrow navigation for menu
                        elif event.key == pygame.K_UP:
                            self.menu_selected = (self.menu_selected - 1) % len(self.menu_items)
                            if self.snd_hover:
                                try:
                                    self.snd_hover.play()
                                except Exception:
                                    pass
                            continue
                        elif event.key == pygame.K_DOWN:
                            self.menu_selected = (self.menu_selected + 1) % len(self.menu_items)
                            if self.snd_hover:
                                try:
                                    self.snd_hover.play()
                                except Exception:
                                    pass
                            continue
                        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                            # Activate selected menu item
                            self.menu_press_start = pygame.time.get_ticks()
                            if self.snd_click:
                                try:
                                    self.snd_click.play()
                                except Exception:
                                    pass
                            if self.menu_selected == 0:
                                self.game_mode = "2player"
                                self.start_game()
                                continue
                            elif self.menu_selected == 1:
                                self.game_mode = "vs_cpu"
                                self.show_difficulty_menu = True
                                continue

                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_z:
                        self.toggle_zoom()
                    elif event.key == pygame.K_m:
                        self.show_menu = True
                        self.menu_open_start = pygame.time.get_ticks()
                    elif event.key == pygame.K_ESCAPE:
                        if self.zoom_level == 1:
                            self.zoom_level = 0
                        else:
                            running = False
                    elif event.key == pygame.K_k:
                        # Toggle keybinds panel
                        self.show_keybinds = not self.show_keybinds
                        self.keybinds_anim_start = pygame.time.get_ticks()
                    elif event.key == pygame.K_u:
                        # Toggle debug mode (F12)
                        self.debug_mode = not self.debug_mode
                    
                    elif event.key == pygame.K_p:
                        # Toggle piece legend inside keybinds
                        self.show_piece_legend = not self.show_piece_legend
                    elif event.key == pygame.K_d:
                        # DEBUG: instantly mark the current board as won by the current player (only in debug mode)
                        if getattr(self, 'debug_mode', False):
                            cb_row, cb_col = self.game.current_board
                            current_board = self.game.get_current_board()
                            if not current_board.is_won:
                                current_board.is_won = True
                                current_board.winner = self.game.current_player
                                # record in won_boards
                                try:
                                    self.game.won_boards[cb_row][cb_col] = current_board.winner
                                except Exception:
                                    pass
                                # check for ultimate win
                                try:
                                    if self.game._check_ultimate_win(cb_row, cb_col, current_board.winner):
                                        self.game.game_over = True
                                        self.game.winner = current_board.winner
                                except Exception:
                                    pass
                                # capture and show transition so user can see it
                                pre = self.screen.copy()
                                # draw updated state
                                self.draw()
                                post = self.screen.copy()
                                self.start_transition("board_change", pre_surf=pre, post_surf=post)
            
            # Update animations and transitions
            self.update_animations(dt, current_time)
            
            # Handle AI moves
            if self.game.is_ai_turn() and not self.game.game_over and not self.is_transitioning:
                self.handle_ai_move(dt, current_time)
            
            self.draw()
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

    def run_splash(self):
        """Display a retro splash / loading screen titled HYPERCHESS"""
        splash_time = 2200  # milliseconds total
        start = pygame.time.get_ticks()
        loading_progress = 0
        import random
        stars = [[(random.randint(0, self.screen_width), random.randint(0, self.screen_height)), random.random() * 0.8 + 0.2] for _ in range(40)]

        while pygame.time.get_ticks() - start < splash_time:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            t = (pygame.time.get_ticks() - start) / splash_time
            loading_progress = int(t * 100)

            # draw frame
            self.screen.fill((10, 10, 30))

            # animated stars
            for i, s in enumerate(stars):
                x, y = s[0]
                brightness = s[1]
                # twinkle
                b = int(155 + 100 * math.sin((pygame.time.get_ticks() / 300.0) + i))
                col = (b, b, b)
                pygame.draw.circle(self.screen, col, (x, y), 1)

            # scanlines
            for y in range(0, self.screen_height, 4):
                line = pygame.Surface((self.screen_width, 2), pygame.SRCALPHA)
                line.fill((255, 255, 255, 6))
                self.screen.blit(line, (0, y))

            # Pixelated title: render at low resolution then scale up nearest-neighbor
            title_font = pygame.font.Font(None, 64)
            title_surf = title_font.render("HYPERCHESS", True, (50, 220, 200))
            scale = 3
            small = pygame.transform.scale(title_surf, (max(1, title_surf.get_width() // scale), max(1, title_surf.get_height() // scale)))
            pixel = pygame.transform.scale(small, (small.get_width() * scale, small.get_height() * scale))
            tx = (self.screen_width - pixel.get_width()) // 2
            ty = int(self.screen_height * 0.25)
            self.screen.blit(pixel, (tx, ty))

            # Subtitle retro
            sub_font = pygame.font.Font(None, 20)
            sub_surf = sub_font.render("A retro-future chess experience", True, (180, 220, 255))
            sub_rect = sub_surf.get_rect(center=(self.screen_width // 2, ty + pixel.get_height() + 20))
            self.screen.blit(sub_surf, sub_rect)

            # Loading bar
            bar_w = self.screen_width // 3
            bar_h = 12
            bx = (self.screen_width - bar_w) // 2
            by = int(self.screen_height * 0.75)
            pygame.draw.rect(self.screen, (60, 60, 80), (bx, by, bar_w, bar_h))
            pygame.draw.rect(self.screen, (100, 220, 200), (bx + 2, by + 2, int((bar_w - 4) * (loading_progress / 100.0)), bar_h - 4))

            pygame.display.flip()
            pygame.time.delay(30)

        # brief fade into menu
        fade_surf = self.screen.copy()
        self.start_transition("zoom", pre_surf=fade_surf, post_surf=None)
        # mark menu open animation start
        self.menu_open_start = pygame.time.get_ticks()
    
    def update_animations(self, dt: int, current_time: int):
        """Update all animations and transitions"""
        # Update transition
        if self.is_transitioning:
            elapsed = current_time - self.transition_start_time
            if elapsed >= self.transition_duration:
                self.is_transitioning = False
                self.transition_alpha = 0
            else:
                progress = elapsed / self.transition_duration
                self.transition_alpha = int(255 * (1 - abs(progress - 0.5) * 2))
        
        # Update board pulse animation
        self.board_pulse_alpha += self.board_pulse_direction * dt * 0.003
        if self.board_pulse_alpha >= 100:
            self.board_pulse_alpha = 100
            self.board_pulse_direction = -1
        elif self.board_pulse_alpha <= 0:
            self.board_pulse_alpha = 0
            self.board_pulse_direction = 1

        # If an AI just moved, wait a short post-move delay so the piece is visible
        if getattr(self, 'pending_board_swap', False):
            # If we have an animating piece, wait for animation to finish or for the post-move delay
            anim_done = True
            if self.animating_piece is not None:
                anim_done = (current_time - self.animation_start_time) >= self.animation_duration

            if anim_done and (current_time - self.pending_swap_start_time >= self.post_move_delay):
                # perform the visual board-change transition now (use captured pre/post if available)
                self.pending_board_swap = False
                self.start_transition("board_change")
                self.last_board_change_time = current_time

        # Update piece animation progress
        if self.animating_piece is not None:
            if current_time - self.animation_start_time >= self.animation_duration:
                # Animation finished
                self.animating_piece = None
    
    def handle_ai_move(self, dt: int, current_time: int):
        """Handle AI move timing and thinking animation"""
        self.ai_move_timer += dt
        
        # Update thinking text animation
        self.ai_thinking_timer += dt
        if self.ai_thinking_timer >= 500:  # Change text every 500ms
            thinking_options = ["AI is thinking...", "AI is calculating...", "AI is strategizing...", "AI is planning..."]
            self.ai_thinking_text = thinking_options[(self.ai_thinking_timer // 500) % len(thinking_options)]
        
        if self.ai_move_timer >= self.ai_move_delay:
            # Capture pre-render so we can crossfade after AI move
            pre_surf = self.screen.copy()
            # Make AI move
            if self.game.make_ai_move():
                # Render the updated board immediately to capture post state
                self.draw()
                post_surf = self.screen.copy()

                # Store surfaces for transition and start pending delay
                self.transition_pre_surf = pre_surf
                self.transition_post_surf = post_surf
                self.pending_board_swap = True
                self.pending_swap_start_time = current_time

                # If zoomed in, create an animating piece sliding from its recorded from/to coords
                if self.zoom_level == 1 and self.game.move_history:
                    board_row, board_col, from_row, from_col, to_row, to_col = self.game.move_history[-1]
                    current_board = self.game.get_current_board()
                    moved_piece = current_board.get_piece(to_row, to_col)
                    if moved_piece:
                        center_x = self.screen_width // 2
                        center_y = self.screen_height // 2
                        square_size = self.zoomed_board_size // 8
                        end_px = center_x - self.zoomed_board_size // 2 + to_col * square_size
                        end_py = center_y - self.zoomed_board_size // 2 + to_row * square_size
                        start_px = center_x - self.zoomed_board_size // 2 + from_col * square_size
                        start_py = center_y - self.zoomed_board_size // 2 + from_row * square_size
                        self.animating_piece = (moved_piece, start_px, start_py, end_px, end_py)
                        self.animation_start_time = current_time
            
            self.ai_move_timer = 0
            self.ai_thinking_timer = 0
            self.selected_piece = None
            self.valid_moves = []
    
    def start_transition(self, transition_type: str, pre_surf=None, post_surf=None):
        """Start a visual transition"""
        # Allow passing in pre/post surfaces for board-change crossfade
        if transition_type == "board_change":
            if pre_surf is not None:
                self.transition_pre_surf = pre_surf.copy()
            if post_surf is not None:
                self.transition_post_surf = post_surf.copy()

        self.is_transitioning = True
        self.transition_type = transition_type
        self.transition_start_time = pygame.time.get_ticks()
        self.transition_alpha = 255
    
    def handle_click(self, pos: Tuple[int, int]):
        """Handle mouse clicks"""
        if self.show_menu:
            self.handle_menu_click(pos)
            return
        # Check keybinds toggle (top-left) before passing clicks to game
        if hasattr(self, 'keybinds_toggle_rect') and self.keybinds_toggle_rect.collidepoint(pos):
            self.show_keybinds = not self.show_keybinds
            self.keybinds_anim_start = pygame.time.get_ticks()
            return

        # Block clicks while a post-move delay is active so the piece movement is visible
        if self.pending_board_swap:
            return

        if self.game.game_over or self.is_transitioning:
            return
        
        if self.zoom_level == 0:
            self.handle_overview_click(pos)
        else:
            self.handle_zoomed_click(pos)
    
    def handle_menu_click(self, pos: Tuple[int, int]):
        """Handle clicks on the menu"""
        x, y = pos
        # Use drawn button rects if available (guard keys to avoid KeyError)
        menu_rects = getattr(self, '_menu_buttons', None)
        if isinstance(menu_rects, dict):
            rect_2p = menu_rects.get('2_players') or menu_rects.get('2players') or menu_rects.get('2_players')
            rect_cpu = menu_rects.get('vs_cpu') or menu_rects.get('vs_cpu')
            if rect_2p and rect_2p.collidepoint((x, y)):
                self.game_mode = "2player"
                self.start_game()
                return
            if rect_cpu and rect_cpu.collidepoint((x, y)):
                self.game_mode = "vs_cpu"
                self.show_difficulty_menu = True
                return

        # Fallback coordinate checks (legacy layout)
        if 200 <= x <= 400 and 200 <= y <= 250:
            self.game_mode = "2player"
            self.start_game()
        elif 200 <= x <= 400 and 270 <= y <= 320:
            self.game_mode = "vs_cpu"
            self.show_difficulty_menu = True
            return
        
        # Difficulty buttons (if vs_cpu is selected)
        if hasattr(self, 'show_difficulty_menu') and self.show_difficulty_menu:
            if 200 <= x <= 400 and 350 <= y <= 400:
                self.ai_difficulty = "easy"
                self.start_game()
            elif 200 <= x <= 400 and 420 <= y <= 470:
                self.ai_difficulty = "medium"
                self.start_game()
            elif 200 <= x <= 400 and 490 <= y <= 540:
                self.ai_difficulty = "hard"
                self.start_game()
    
    def handle_overview_click(self, pos: Tuple[int, int]):
        """Handle clicks in overview mode"""
        # Check if clicking on a board
        board_coords = self.get_board_coordinates_from_screen(pos)
        if board_coords is None:
            return
        
        board_row, board_col = board_coords
        
        # If clicking on current board, zoom into it
        current_board_row, current_board_col = self.game.current_board
        if board_row == current_board_row and board_col == current_board_col:
            self.start_transition("zoom")
            self.zoom_level = 1
            return
        
        # If clicking on a different board, switch to it (if it's not won)
        if not self.game.is_board_won(board_row, board_col):
            pre = self.screen.copy()
            self.game.current_board = (board_row, board_col)
            # draw updated board to capture post
            self.draw()
            post = self.screen.copy()
            self.start_transition("board_change", pre, post)
            self.selected_piece = None
            self.valid_moves = []
    
    def handle_zoomed_click(self, pos: Tuple[int, int]):
        """Handle clicks in zoomed mode"""
        if self.game.is_ai_turn():
            return
        
        # Convert to piece coordinates within the current board
        piece_coords = self.get_zoomed_piece_coordinates(pos)
        if piece_coords is None:
            return
        
        piece_row, piece_col = piece_coords
        current_board = self.game.get_current_board()
        
        # If no piece is selected, try to select one
        if self.selected_piece is None:
            piece = current_board.get_piece(piece_row, piece_col)
            
            if piece and piece.color == self.game.current_player:
                self.selected_piece = (piece_row, piece_col)
                self.valid_moves = piece.get_valid_moves(current_board)
        else:
            # Try to move the selected piece
            if (piece_row, piece_col) in self.valid_moves:
                from_row, from_col = self.selected_piece
                if self.game.make_move(from_row, from_col, piece_row, piece_col):
                    # capture pre/post for smooth crossfade
                    pre = self.screen.copy()
                    # render new state
                    self.draw()
                    post = self.screen.copy()
                    self.start_transition("board_change", pre, post)
                    self.selected_piece = None
                    self.valid_moves = []
                else:
                    # Invalid move, deselect
                    self.selected_piece = None
                    self.valid_moves = []
            else:
                # Clicked on invalid square, deselect
                self.selected_piece = None
                self.valid_moves = []
    
    def start_game(self):
        """Start a new game with selected settings"""
        self.game.set_game_mode(self.game_mode, self.ai_difficulty)
        self.show_menu = False
        self.zoom_level = 0
        self.selected_piece = None
        self.valid_moves = []
        self.ai_move_timer = 0
        self.start_transition("board_change")
    
    def reset_game(self):
        """Reset the current game"""
        self.game.reset_game()
        self.selected_piece = None
        self.valid_moves = []
        self.ai_move_timer = 0
        self.start_transition("board_change")
    
    def toggle_zoom(self):
        """Toggle between overview and zoomed view"""
        self.start_transition("zoom")
        self.zoom_level = 1 - self.zoom_level
        self.selected_piece = None
        self.valid_moves = []
    
    def get_board_coordinates_from_screen(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Convert screen position to board coordinates in overview mode"""
        x, y = pos
        x -= self.offset_x
        y -= self.offset_y
        
        board_col = x // (self.board_size + self.spacing)
        board_row = y // (self.board_size + self.spacing)
        
        if 0 <= board_row < 8 and 0 <= board_col < 8:
            return (board_row, board_col)
        
        return None
    
    def get_zoomed_piece_coordinates(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Convert screen position to piece coordinates in zoomed mode"""
        x, y = pos
        
        # Calculate the center position for the zoomed board
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        # Calculate relative position from center
        rel_x = x - center_x + self.zoomed_board_size // 2
        rel_y = y - center_y + self.zoomed_board_size // 2
        
        # Convert to piece coordinates
        square_size = self.zoomed_board_size // 8
        piece_col = rel_x // square_size
        piece_row = rel_y // square_size
        
        if 0 <= piece_row < 8 and 0 <= piece_col < 8:
            return (piece_row, piece_col)
        
        return None
    
    def draw(self):
        """Draw the game"""
        # Modern subtle background: vertical gradient
        for i in range(self.screen_height):
            t = i / max(1, self.screen_height - 1)
            r = int(245 - t * 30)
            g = int(245 - t * 35)
            b = int(250 - t * 20)
            pygame.draw.line(self.screen, (r, g, b), (0, i), (self.screen_width, i))
        
        if self.show_menu:
            self.draw_menu()
        elif self.zoom_level == 0:
            self.draw_overview()
        else:
            self.draw_zoomed_view()
        
        self.draw_ui()
        self.draw_transitions()
    
    def draw_transitions(self):
        """Draw transition effects"""
        if self.is_transitioning:
            elapsed = pygame.time.get_ticks() - self.transition_start_time
            t = min(1.0, elapsed / max(1, self.transition_duration))
            if self.transition_type == "board_change" and self.transition_pre_surf and self.transition_post_surf:
                # Crossfade post over pre
                self.screen.blit(self.transition_pre_surf, (0, 0))
                post = self.transition_post_surf.copy()
                post.set_alpha(int(255 * t))
                self.screen.blit(post, (0, 0))
            else:
                # fallback: simple fade overlay
                if t >= 1.0:
                    alpha = 0
                else:
                    alpha = int(255 * (1 - abs(t - 0.5) * 2))
                overlay = pygame.Surface((self.screen_width, self.screen_height))
                overlay.set_alpha(alpha)
                overlay.fill(self.TRANSITION_COLOR)
                self.screen.blit(overlay, (0, 0))

            if elapsed >= self.transition_duration:
                self.is_transitioning = False
                # clear stored transition surfaces after finishing
                self.transition_pre_surf = None
                self.transition_post_surf = None
    
    def draw_menu(self):
        """Draw the main menu"""
        # Gradient background (retro colors)
        for i in range(self.screen_height):
            t = i / self.screen_height
            r = int(12 + t * 40)
            g = int(10 + t * 30)
            b = int(30 + t * 80)
            pygame.draw.line(self.screen, (r, g, b), (0, i), (self.screen_width, i))

        # Retro pixel title (renamed to HYPERCHESS)
        title_font = pygame.font.Font(None, 72)
        title_surf = title_font.render("HYPERCHESS", True, (40, 240, 220))
        small = pygame.transform.scale(title_surf, (max(1, title_surf.get_width()//4), max(1, title_surf.get_height()//4)))
        pixel_title = pygame.transform.scale(small, (small.get_width()*4, small.get_height()*4))
        self.screen.blit(pixel_title, ((self.screen_width - pixel_title.get_width())//2, 48))

        # Buttons
        mx, my = pygame.mouse.get_pos()

        def draw_button(x, y, w, h, text, hovered):
            color = (80, 80, 100) if not hovered else (140, 60, 120)
            pygame.draw.rect(self.screen, color, (x, y, w, h))
            pygame.draw.rect(self.screen, (255,255,255), (x, y, w, h), 2)
            txt = self.font.render(text, True, (240,240,240))
            self.screen.blit(txt, (x + (w - txt.get_width())//2, y + (h - txt.get_height())//2))

        # Layout math for centered buttons
        btn_w = self.MENU_BUTTON_WIDTH
        btn_h = self.MENU_BUTTON_HEIGHT
        gap = self.MENU_BUTTON_GAP
        start_x = (self.screen_width - btn_w) // 2
        start_y = self.MENU_TOP_Y

        # Draw menu items with keyboard focus and hover
        for idx, label in enumerate(self.menu_items):
            y = start_y + idx * (btn_h + gap)
            hovered = (start_x <= mx <= start_x + btn_w and y <= my <= y + btn_h)
            focused = (self.menu_selected == idx)
            pressed = (self.menu_press_start != 0 and pygame.time.get_ticks() - self.menu_press_start < self.menu_press_duration and focused)

            # Button color states
            if pressed:
                color = (60, 30, 80)
            elif hovered or focused:
                color = (140, 60, 120)
            else:
                color = (80, 80, 100)

            # Draw pixel-border (thick rectangle with inner fill)
            outer = pygame.Rect(start_x - 3, y - 3, btn_w + 6, btn_h + 6)
            pygame.draw.rect(self.screen, (20, 20, 30), outer)
            pygame.draw.rect(self.screen, color, (start_x, y, btn_w, btn_h))
            pygame.draw.rect(self.screen, (240, 240, 240), (start_x, y, btn_w, btn_h), 2)

            txt = self.font.render(label, True, (240, 240, 240))
            self.screen.blit(txt, (start_x + (btn_w - txt.get_width())//2, y + (btn_h - txt.get_height())//2))

            # Store rect for clicks
            self._menu_buttons[label.lower().replace(' ', '_')] = pygame.Rect(start_x, y, btn_w, btn_h)
        
        # Difficulty selection (if vs_cpu)
        if hasattr(self, 'show_difficulty_menu') and self.show_difficulty_menu:
            diff_text = self.font.render("Select Difficulty:", True, self.WHITE)
            diff_rect = diff_text.get_rect(center=(self.screen_width // 2, 330))
            self.screen.blit(diff_text, diff_rect)
            
            # Easy button
            pygame.draw.rect(self.screen, self.BUTTON_COLOR, (200, 350, 200, 50))
            pygame.draw.rect(self.screen, self.WHITE, (200, 350, 200, 50), 2)
            easy_text = self.font.render("Easy", True, self.WHITE)
            easy_rect = easy_text.get_rect(center=(300, 375))
            self.screen.blit(easy_text, easy_rect)
            
            # Medium button
            pygame.draw.rect(self.screen, self.BUTTON_COLOR, (200, 420, 200, 50))
            pygame.draw.rect(self.screen, self.WHITE, (200, 420, 200, 50), 2)
            medium_text = self.font.render("Medium", True, self.WHITE)
            medium_rect = medium_text.get_rect(center=(300, 445))
            self.screen.blit(medium_text, medium_rect)
            
            # Hard button
            pygame.draw.rect(self.screen, self.BUTTON_COLOR, (200, 490, 200, 50))
            pygame.draw.rect(self.screen, self.WHITE, (200, 490, 200, 50), 2)
            hard_text = self.font.render("Hard", True, self.WHITE)
            hard_rect = hard_text.get_rect(center=(300, 515))
            self.screen.blit(hard_text, hard_rect)
    
    def draw_overview(self):
        """Draw the overview of all boards"""
        for board_row in range(8):
            for board_col in range(8):
                self.draw_board_overview(board_row, board_col)
    
    def draw_board_overview(self, board_row: int, board_col: int):
        """Draw a single board in overview mode"""
        board = self.game.boards[board_row][board_col]
        
        # Calculate board position
        x = self.offset_x + board_col * (self.board_size + self.spacing)
        y = self.offset_y + board_row * (self.board_size + self.spacing)
        
        # Draw board background with pulse effect for current board
        color = self.LIGHT_BROWN
        pulse_effect = 0
        
        if self.game.is_board_won(board_row, board_col):
            color = self.WON_BOARD_HIGHLIGHT
        elif board_row == self.game.current_board[0] and board_col == self.game.current_board[1]:
            color = self.CURRENT_BOARD_HIGHLIGHT
            pulse_effect = int(self.board_pulse_alpha * 0.3)
        
        # Apply pulse effect
        if pulse_effect > 0:
            pulse_color = tuple(min(255, c + pulse_effect) for c in color)
            pygame.draw.rect(self.screen, pulse_color, (x, y, self.board_size, self.board_size))
        else:
            pygame.draw.rect(self.screen, color, (x, y, self.board_size, self.board_size))
        
        # Draw board squares
        square_size = self.board_size // 8
        for row in range(8):
            for col in range(8):
                square_x = x + col * square_size
                square_y = y + row * square_size
                
                # Alternate square colors
                if (row + col) % 2 == 0:
                    square_color = self.LIGHT_BROWN
                else:
                    square_color = self.DARK_BROWN
                
                pygame.draw.rect(self.screen, square_color, (square_x, square_y, square_size, square_size))
        
        # Draw pieces
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece:
                    self.draw_piece_overview(piece, x + col * square_size, y + row * square_size, square_size)
        
        # Draw board border with enhanced visibility
        border_color = self.BLACK
        border_width = 3 if board_row == self.game.current_board[0] and board_col == self.game.current_board[1] else 2
        pygame.draw.rect(self.screen, border_color, (x, y, self.board_size, self.board_size), border_width)
        
        # Draw board coordinates
        coord_text = f"{chr(ord('a') + board_col)}{8 - board_row}"
        text_surface = self.small_font.render(coord_text, True, self.BLACK)
        self.screen.blit(text_surface, (x + 2, y + 2))
        
        # Draw moves remaining indicator
        if board_row == self.game.current_board[0] and board_col == self.game.current_board[1]:
            moves_left = self.game.max_moves_per_board - self.game.moves_on_current_board
            moves_text = f"{moves_left}"
            moves_surface = self.bold_font.render(moves_text, True, self.BLACK)
            moves_rect = moves_surface.get_rect(center=(x + self.board_size - 10, y + 10))
            self.screen.blit(moves_surface, moves_rect)
    
    def draw_zoomed_view(self):
        """Draw the zoomed view of the current board"""
        current_board = self.game.get_current_board()
        
        # Calculate center position
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        # Draw board background with pulse effect
        pulse_effect = int(self.board_pulse_alpha * 0.2)
        base_color = self.LIGHT_BROWN
        pulse_color = tuple(min(255, c + pulse_effect) for c in base_color)
        
        pygame.draw.rect(self.screen, pulse_color, 
                        (center_x - self.zoomed_board_size // 2, 
                         center_y - self.zoomed_board_size // 2, 
                         self.zoomed_board_size, self.zoomed_board_size))
        
        # Draw board squares
        square_size = self.zoomed_board_size // 8
        for row in range(8):
            for col in range(8):
                square_x = center_x - self.zoomed_board_size // 2 + col * square_size
                square_y = center_y - self.zoomed_board_size // 2 + row * square_size
                
                # Alternate square colors
                if (row + col) % 2 == 0:
                    square_color = self.LIGHT_BROWN
                else:
                    square_color = self.DARK_BROWN
                
                pygame.draw.rect(self.screen, square_color, (square_x, square_y, square_size, square_size))
        
        # Draw pieces
        # If animating a piece, determine which square to skip drawing (the moving piece's dest is already on the board)
        animating_dest = None
        if self.animating_piece is not None:
            moved_piece, s_px, s_py, e_px, e_py = self.animating_piece
            # compute dest square from end_px/end_py
            animating_dest = ((e_py - (center_y - self.zoomed_board_size // 2)) // square_size,
                              (e_px - (center_x - self.zoomed_board_size // 2)) // square_size)

        for row in range(8):
            for col in range(8):
                piece = current_board.get_piece(row, col)
                if piece:
                    # Skip drawing the animated piece at its board slot; we'll draw it on top with interpolated coords
                    if animating_dest is not None and (row, col) == (int(animating_dest[0]), int(animating_dest[1])):
                        continue
                    piece_x = center_x - self.zoomed_board_size // 2 + col * square_size
                    piece_y = center_y - self.zoomed_board_size // 2 + row * square_size
                    self.draw_piece_zoomed(piece, piece_x, piece_y, square_size)
        
        # Draw valid moves if a piece is selected (pulsing/fade effect)
        if self.selected_piece is not None:
            pulse = int((1 + math.sin(pygame.time.get_ticks() / 200)) * 6)
            for move_row, move_col in self.valid_moves:
                move_x = center_x - self.zoomed_board_size // 2 + move_col * square_size
                move_y = center_y - self.zoomed_board_size // 2 + move_row * square_size
                radius = square_size // 5 + pulse // 2
                alpha = max(80, 120 - pulse * 4)
                surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, (self.MOVE_HIGHLIGHT[0], self.MOVE_HIGHLIGHT[1], self.MOVE_HIGHLIGHT[2], alpha),
                                   (radius, radius), radius)
                self.screen.blit(surf, (move_x + square_size // 2 - radius, move_y + square_size // 2 - radius))

        # Hover highlight (subtle overlay) over square under mouse
        mx, my = pygame.mouse.get_pos()
        # Calculate hover piece coords
        rel_x = mx - (center_x - self.zoomed_board_size // 2)
        rel_y = my - (center_y - self.zoomed_board_size // 2)
        hover_col = rel_x // square_size
        hover_row = rel_y // square_size
        if 0 <= hover_row < 8 and 0 <= hover_col < 8:
            hover_x = center_x - self.zoomed_board_size // 2 + hover_col * square_size
            hover_y = center_y - self.zoomed_board_size // 2 + hover_row * square_size
            hover_surf = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
            hover_surf.fill((255, 255, 255, 30))
            self.screen.blit(hover_surf, (hover_x, hover_y))
        
        # Draw board border with enhanced visibility
        pygame.draw.rect(self.screen, self.BLACK, 
                        (center_x - self.zoomed_board_size // 2, 
                         center_y - self.zoomed_board_size // 2, 
                         self.zoomed_board_size, self.zoomed_board_size), 4)

        # Draw animating piece on top if any
        if self.animating_piece is not None:
            moved_piece, s_px, s_py, e_px, e_py = self.animating_piece
            elapsed = pygame.time.get_ticks() - self.animation_start_time
            t = min(1.0, elapsed / max(1, self.animation_duration))
            cur_x = int(s_px + (e_px - s_px) * t)
            cur_y = int(s_py + (e_py - s_py) * t)
            # Draw a subtle shadow
            shadow = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
            shadow.fill((0,0,0,80))
            self.screen.blit(shadow, (cur_x, cur_y + square_size // 8))
            # Draw piece at interpolated position
            self.draw_piece_zoomed(moved_piece, cur_x, cur_y, square_size)
    
    def draw_piece_overview(self, piece, x: int, y: int, size: int):
        """Draw a chess piece in overview mode"""
        self.piece_renderer.draw_piece(self.screen, piece, x, y, size)
    
    def draw_piece_zoomed(self, piece, x: int, y: int, size: int):
        """Draw a chess piece in zoomed mode"""
        self.piece_renderer.draw_piece(self.screen, piece, x, y, size)
    
    def draw_ui(self):
        """Draw UI elements"""
        if self.show_menu:
            return

        # Top-center info box (compact)
        info_w = 380
        info_h = 64
        info_x = (self.screen_width - info_w) // 2
        info_y = 12
        info_rect = pygame.Rect(info_x, info_y, info_w, info_h)
        pygame.draw.rect(self.screen, (245, 245, 250), info_rect)
        pygame.draw.rect(self.screen, (200, 200, 210), info_rect, 2)

        # Content: current board and moves remaining
        current_board_row, current_board_col = self.game.current_board
        moves_left = self.game.max_moves_per_board - self.game.moves_on_current_board
        board_text = f"Board: {chr(ord('a') + current_board_col)}{8 - current_board_row}"
        moves_text = f"Moves left: {moves_left}"
        self.screen.blit(self.bold_font.render(board_text, True, (30, 30, 30)), (info_x + 12, info_y + 8))
        self.screen.blit(self.font.render(moves_text, True, (50, 50, 50)), (info_x + 12, info_y + 34))

        # Small keybinds toggle top-left
        toggle = self.keybinds_toggle_rect
        pygame.draw.rect(self.screen, (230,230,235), toggle)
        pygame.draw.rect(self.screen, (180,180,180), toggle, 2)
        ktxt = self.small_font.render('K', True, (40,40,40))
        self.screen.blit(ktxt, (toggle.x + (toggle.width - ktxt.get_width())//2, toggle.y + (toggle.height - ktxt.get_height())//2))

        # Draw collapsible keybinds panel if shown
        if self.show_keybinds or (self.keybinds_anim_start and pygame.time.get_ticks() - self.keybinds_anim_start < self.keybinds_anim_duration):
            kr = self.keybinds_rect.copy()
            # Slide animation: from -kr.width to kr.x
            anim_elapsed = max(0, pygame.time.get_ticks() - self.keybinds_anim_start)
            t = min(1.0, anim_elapsed / max(1, self.keybinds_anim_duration))
            # ease out
            ease = 1 - (1 - t) * (1 - t)
            off_x = int(-kr.width + (kr.x + kr.width) * ease)
            draw_x = off_x if not self.show_keybinds else int(kr.x * ease)
            kr_draw = pygame.Rect(draw_x, kr.y, kr.width, kr.height)
            pygame.draw.rect(self.screen, (250, 250, 252), kr_draw)
            pygame.draw.rect(self.screen, (190,190,200), kr_draw, 2)
            title = self.bold_font.render('Keybinds', True, (30,30,30))
            self.screen.blit(title, (kr_draw.x + 12, kr_draw.y + 8))
            kb_list = [
                '1 - Start 2 Players',
                '2 - VS CPU',
                'Z - Toggle Zoom',
                'R - Reset Game',
                'M - Main Menu',
                'K - Toggle Keybinds',
                'P - Toggle Piece Legend',
                'ESC - Exit / Zoom Out'
            ]
            yy = kr_draw.y + 40
            for line in kb_list:
                self.screen.blit(self.small_font.render(line, True, (50,50,60)), (kr_draw.x + 12, yy))
                yy += 20

            # Optional piece legend drawn as boxed icons
            if self.show_piece_legend:
                yy += 8
                legend_title = self.font.render('Piece Legend:', True, (30,30,30))
                self.screen.blit(legend_title, (kr_draw.x + 12, yy))
                yy += 24
                # draw a small box for legend
                legend_w = kr_draw.width - 24
                legend_h = 110
                legend_x = kr_draw.x + 12
                legend_y = yy
                legend_rect = pygame.Rect(legend_x, legend_y, legend_w, legend_h)
                pygame.draw.rect(self.screen, (240,240,245), legend_rect)
                pygame.draw.rect(self.screen, (180,180,190), legend_rect, 2)
                # draw piece icons and descriptions
                icon_size = 36
                pad_x = 10
                px = legend_x + 8
                py = legend_y + 8
                piece_types = [PieceType.KING, PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT, PieceType.PAWN]
                for idx, ptype in enumerate(piece_types):
                    # white piece
                    p_white = Piece(ptype, Color.WHITE, 0, 0)
                    self.piece_renderer.draw_piece(self.screen, p_white, px, py + idx * (icon_size + 4), icon_size)
                    # black piece
                    p_black = Piece(ptype, Color.BLACK, 0, 0)
                    self.piece_renderer.draw_piece(self.screen, p_black, px + icon_size + 8, py + idx * (icon_size + 4), icon_size)
                    # text
                    desc = ptype.name.title()
                    self.screen.blit(self.small_font.render(desc, True, (40,40,40)), (px + icon_size * 2 + 20, py + idx * (icon_size + 4) + icon_size // 4))

        # Draw win modal if game is over
        if self.game.game_over:
            winner = self.game.winner
            if winner is not None:
                msg = f"{winner.name.title()} wins the ultimate game!"
            else:
                msg = "Game over"
            # Darken background
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))
            # Modal box
            mw, mh = 480, 180
            mx = (self.screen_width - mw) // 2
            my = (self.screen_height - mh) // 2
            modal = pygame.Rect(mx, my, mw, mh)
            pygame.draw.rect(self.screen, (250, 250, 252), modal)
            pygame.draw.rect(self.screen, (60, 60, 70), modal, 3)
            title = self.large_font.render('Victory!', True, (20, 20, 20))
            self.screen.blit(title, (mx + 24, my + 18))
            msg_surf = self.font.render(msg, True, (40, 40, 40))
            self.screen.blit(msg_surf, (mx + 24, my + 64))
            sub = self.small_font.render('Press R to restart or M for menu', True, (80,80,90))
            self.screen.blit(sub, (mx + 24, my + 110))