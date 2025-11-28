class BaghChal:
    def __init__(self):
        # Board representation: 5x5 grid
        # 0 = Empty, 1 = Goat (G), -1 = Tiger (T)
        self.board = [[0 for _ in range(5)] for _ in range(5)]
        
        # Game State
        self.goats_placed = 0  # Count of goats placed on board (max 20)
        self.goats_captured = 0 # Count of goats eaten by tigers
        self.turn = 'G'  # 'G' for Goat, 'T' for Tiger. Goat starts first (placement).
        self.phase = 'PLACEMENT' # 'PLACEMENT' or 'MOVEMENT'
        self.winner = None # 'G', 'T', or None
        
        # Initialize Tigers at the four corners
        for r, c in [(0,0),(0,4),(4,0),(4,4)]:
            self.board[r][c] = -1

    def get_valid_moves(self, r, c, check_turn=True):
        """
        Algorithm: Graph Traversal / Adjacency Check
        Returns a list of valid (r, c) tuples where the piece at [r][c] can move.
        For Tigers, this includes jumps.
        """
        if self.winner:
            return []

        piece = self.board[r][c]
        if piece == 0:
            return[]
        moves = []

        # If it's Goat's turn but we are still in PLACEMENT phase, 
        # goats on board cannot move yet.
        if piece == 1 and self.phase == 'PLACEMENT':
            return []
        
        # If it's not the piece's turn, no moves.
        if check_turn:
            if (piece == 1 and self.turn != 'G') or (piece == -1 and self.turn != 'T'):
                return []

        # 1. Check adjacent moves (distance 1)
        # Directions: Up, Down, Left, Right
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        # Add Diagonals if the position allows it
        # In Baghchal, diagonals are valid only on specific squares.
        # Logic: If (r + c) is even, diagonals are available.
        if (r + c) % 2 == 0:
            directions += [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 5 and 0 <= nc < 5:
                if self.board[nr][nc] == 0:
                    moves.append((nr, nc))

        # 2. Check Tiger Jumps (Captures)
        # Only Tigers (-1) can jump over Goats (1)
        if piece == -1:
            for dr, dc in directions:
                # Mid point (potential goat)
                mr, mc = r + dr, c + dc
                # Landing point (must be empty)
                lr, lc = r + 2*dr, c + 2*dc
                
                if 0 <= lr < 5 and 0 <= lc < 5:
                    if self.board[mr][mc] == 1 and self.board[lr][lc] == 0:
                        moves.append((lr, lc))

        return moves

    def make_move(self, start_pos, end_pos):
        """
        Executes a move on the board.
        start_pos: (r, c) tuple of the piece being moved.
        end_pos: (r, c) tuple of the destination.
        Returns True if move was successful, False otherwise.
        """
        if self.winner:
            return False

        r1, c1 = start_pos
        r2, c2 = end_pos
        
        if self.board[r1][c1] == 0:
            return False

        # Validate move is in allowed list
        valid_moves = self.get_valid_moves(r1, c1)
        if end_pos not in valid_moves:
            return False

        piece = self.board[r1][c1]
        
        # Execute Move
        self.board[r1][c1] = 0
        self.board[r2][c2] = piece
        
        # Handle Capture (Tiger Jump)
        captured = False
        if piece == -1:
            # Check if distance is 2 (Jump)
            if abs(r2 - r1) == 2 or abs(c2 - c1) == 2:
                # Calculate mid point to remove goat
                mr, mc = (r1 + r2) // 2, (c1 + c2) // 2
                self.board[mr][mc] = 0 # Remove Goat
                self.goats_captured += 1
                captured = True
        
        # Switch Turn
        self.switch_turn()
        self.check_win_condition()
        
        return True

    def place_goat(self, r, c):
        """
        Places a goat on the board during PLACEMENT phase.
        """
        if self.winner:
            return False
            
        if self.phase != 'PLACEMENT' or self.turn != 'G':
            return False
        
        if self.board[r][c] != 0:
            return False # Occupied
            
        self.board[r][c] = 1 # Place Goat
        self.goats_placed += 1
        
        if self.goats_placed == 20:
            self.phase = 'MOVEMENT'
            
        self.switch_turn()
        self.check_win_condition()
        
        return True

    def switch_turn(self):
        self.turn = 'T' if self.turn == 'G' else 'G'

    def check_win_condition(self):
        """
        Algorithm: State Analysis
        1. Tiger Win: Captured 5 goats.
        2. Goat Win: Tigers have NO valid moves (Stalemate for tigers).
        """
        # Condition 1: Tiger Win
        if self.goats_captured >= 5:
            self.winner = 'T'
            return

        # Condition 2: Goat Win (Trap Tigers)
        # Check if ANY tiger has ANY valid move.
        tiger_can_move = False
        for r in range(5):
            for c in range(5):
                if self.board[r][c] == -1: # Found a tiger
                    moves = self.get_valid_moves(r, c, check_turn=False)
                    if len(moves) > 0:
                        tiger_can_move = True
                        break
            if tiger_can_move:
                break
        
        if not tiger_can_move:
            self.winner = 'G'

    def get_valid_placements(self):
        """Helper for UI to highlight empty spots during placement phase"""
        placements = []
        for r in range(5):
            for c in range(5):
                if self.board[r][c] == 0:
                    placements.append((r, c))
        return placements

