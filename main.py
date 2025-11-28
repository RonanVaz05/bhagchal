import pygame
import sys
from game_logic import BaghChal

# --- Constants ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 700 # Extra space for UI/Stats
BOARD_SIZE = 500
MARGIN = 50
GRID_SIZE = 5
CELL_SIZE = BOARD_SIZE // (GRID_SIZE - 1)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)       # Tiger
GREEN = (34, 139, 34)     # Goat
BLUE = (70, 130, 180)     # Highlight
CREAM = (255, 253, 208)   # Background
GRAY = (200, 200, 200)

class BaghChalUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Baghchal - Tiger and Goat Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        
        self.game = BaghChal()
        
        # UI State
        self.selected_pos = None # (r, c) of selected piece
        self.valid_moves_cache = [] # List of valid moves for selected piece

    def run(self):
        running = True
        while running:
            # 1. Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r: # Reset
                        self.game = BaghChal()
                        self.selected_pos = None
                        self.valid_moves_cache = []

            # 2. Drawing
            self.draw()
            
            # 3. Update Display
            pygame.display.flip()
            self.clock.tick(30) # 30 FPS

        pygame.quit()
        sys.exit()

    def handle_click(self, pos):
        """
        Algorithm: Input Mapping & State Machine
        1. Convert Screen Coords -> Grid Coords
        2. Determine Action based on Game Phase & Selection
        """
        x, y = pos
        
        # Ignore clicks outside board area
        if not (MARGIN - 20 <= x <= MARGIN + BOARD_SIZE + 20 and 
                MARGIN - 20 <= y <= MARGIN + BOARD_SIZE + 20):
            return

        # Snap to nearest grid point
        # Formula: round((mouse - margin) / cell_size)
        c = round((x - MARGIN) / CELL_SIZE)
        r = round((y - MARGIN) / CELL_SIZE)
        
        # Boundary Check
        if not (0 <= r < 5 and 0 <= c < 5):
            return
            
        # Logic Delegation
        if self.game.winner:
            return # Game Over, no clicks

        clicked_pos = (r, c)

        # -- PLACEMENT PHASE (Goats only) --
        if self.game.phase == 'PLACEMENT' and self.game.turn == 'G':
            # Try to place goat at clicked position
            if self.game.place_goat(r, c):
                print(f"Goat placed at {r}, {c}")
                # Check for instant win/loss logic updates if any
            return

        # -- MOVEMENT PHASE (or Tiger turn during Placement) --
        # Case A: Select a Piece
        piece = self.game.board[r][c]
        is_current_player_piece = (
            (piece == 1 and self.game.turn == 'G') or 
            (piece == -1 and self.game.turn == 'T')
        )

        if is_current_player_piece:
            self.selected_pos = clicked_pos
            self.valid_moves_cache = self.game.get_valid_moves(r, c)
            print(f"Selected {clicked_pos}, Valid Moves: {self.valid_moves_cache}")
            return

        # Case B: Move Selected Piece
        if self.selected_pos:
            if clicked_pos in self.valid_moves_cache:
                success = self.game.make_move(self.selected_pos, clicked_pos)
                if success:
                    print(f"Moved from {self.selected_pos} to {clicked_pos}")
                    # Reset selection after move
                    self.selected_pos = None
                    self.valid_moves_cache = []
            else:
                # If clicked elsewhere (invalid move or empty space), deselect
                # unless it was a piece selection handled above.
                self.selected_pos = None
                self.valid_moves_cache = []

    def draw(self):
        self.screen.fill(CREAM)
        
        # 1. Draw Grid Lines
        # Horizontal & Vertical
        for i in range(5):
            start = MARGIN + i * CELL_SIZE
            # Vertical
            pygame.draw.line(self.screen, BLACK, (start, MARGIN), (start, MARGIN + BOARD_SIZE), 2)
            # Horizontal
            pygame.draw.line(self.screen, BLACK, (MARGIN, start), (MARGIN + BOARD_SIZE, start), 2)
            
        # Diagonals
        # Main diagonals
        pygame.draw.line(self.screen, BLACK, (MARGIN, MARGIN), (MARGIN + BOARD_SIZE, MARGIN + BOARD_SIZE), 2)
        pygame.draw.line(self.screen, BLACK, (MARGIN + BOARD_SIZE, MARGIN), (MARGIN, MARGIN + BOARD_SIZE), 2)
        
        # Diamond (rotated square)
        mid = MARGIN + BOARD_SIZE // 2
        pygame.draw.line(self.screen, BLACK, (mid, MARGIN), (MARGIN + BOARD_SIZE, mid), 2)
        pygame.draw.line(self.screen, BLACK, (MARGIN + BOARD_SIZE, mid), (mid, MARGIN + BOARD_SIZE), 2)
        pygame.draw.line(self.screen, BLACK, (mid, MARGIN + BOARD_SIZE), (MARGIN, mid), 2)
        pygame.draw.line(self.screen, BLACK, (MARGIN, mid), (mid, MARGIN), 2)

        # 2. Draw Connections / Highlights
        if self.selected_pos:
            sr, sc = self.selected_pos
            sx = MARGIN + sc * CELL_SIZE
            sy = MARGIN + sr * CELL_SIZE
            pygame.draw.circle(self.screen, BLUE, (sx, sy), 25, 4) # Selection Ring
            
            # Draw Valid Moves
            for (mr, mc) in self.valid_moves_cache:
                mx = MARGIN + mc * CELL_SIZE
                my = MARGIN + mr * CELL_SIZE
                pygame.draw.circle(self.screen, BLUE, (mx, my), 10) # Small dot for valid move

        # 3. Draw Pieces
        for r in range(5):
            for c in range(5):
                piece = self.game.board[r][c]
                x = MARGIN + c * CELL_SIZE
                y = MARGIN + r * CELL_SIZE
                
                if piece == 1: # Goat
                    pygame.draw.circle(self.screen, GREEN, (x, y), 20)
                elif piece == -1: # Tiger
                    pygame.draw.circle(self.screen, RED, (x, y), 22)
                    pygame.draw.circle(self.screen, BLACK, (x, y), 22, 2) # Border

        # 4. Draw UI / Info
        self.draw_info()

    def draw_info(self):
        # Stats area below board
        y_offset = MARGIN + BOARD_SIZE + 20
        
        turn_text = f"Turn: {'Goat (Green)' if self.game.turn == 'G' else 'Tiger (Red)'}"
        phase_text = f"Phase: {self.game.phase}"
        goats_info = f"Goats Placed: {self.game.goats_placed}/20 | Captured: {self.game.goats_captured}/5"
        
        color = BLACK
        if self.game.winner:
            turn_text = f"GAME OVER! Winner: {'Goat' if self.game.winner == 'G' else 'Tiger'}"
            color = RED if self.game.winner == 'T' else GREEN

        t1 = self.font.render(turn_text, True, color)
        t2 = self.font.render(phase_text, True, BLACK)
        t3 = self.font.render(goats_info, True, BLACK)
        
        self.screen.blit(t1, (MARGIN, y_offset))
        self.screen.blit(t2, (MARGIN, y_offset + 30))
        self.screen.blit(t3, (MARGIN, y_offset + 60))

        if self.game.winner:
            restart_text = self.font.render("Press 'R' to Restart", True, BLUE)
            self.screen.blit(restart_text, (MARGIN, y_offset + 90))

if __name__ == "__main__":
    app = BaghChalUI()
    app.run()

