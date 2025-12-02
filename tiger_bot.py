import copy
import math
import random

class TigerBot:
    def __init__(self, depth=3):
        self.depth = depth

    def get_best_move(self, game):
        """
        Returns the best move for the Tiger as a tuple: (start_pos, end_pos)
        start_pos: (r, c)
        end_pos: (r, c)
        """
        # We maximize for Tiger ('T')
        best_score = -math.inf
        best_move = None
        
        # Get all possible moves for all tigers
        possible_moves = self.get_all_tiger_moves(game)
        
        # If no moves available, we lost (or will lose)
        if not possible_moves:
            return None

        # Shuffle to add a bit of randomness for equal-value moves
        random.shuffle(possible_moves)

        for start, end in possible_moves:
            # Simulate move
            game_copy = copy.deepcopy(game)
            game_copy.make_move(start, end)
            
            # Call Minimax
            score = self.minimax(game_copy, self.depth - 1, False, -math.inf, math.inf)
            
            if score > best_score:
                best_score = score
                best_move = (start, end)
                
        return best_move

    def minimax(self, game, depth, is_maximizing, alpha, beta):
        # Terminal states
        if game.winner == 'T':
            return 10000 + depth # Prefer winning sooner
        if game.winner == 'G':
            return -10000
        
        if depth == 0:
            return self.evaluate(game)

        if is_maximizing: # Tiger's Turn
            max_eval = -math.inf
            moves = self.get_all_tiger_moves(game)
            
            if not moves: # No moves = Trap = Loss
                return -10000
                
            for start, end in moves:
                game_copy = copy.deepcopy(game)
                game_copy.make_move(start, end)
                eval = self.minimax(game_copy, depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else: # Goat's Turn
            min_eval = math.inf
            moves = self.get_all_goat_moves(game)
            
            # If goat has no moves (rare in movement, but possible), skip turn or game over logic?
            # In Baghchal, if goats are blocked, they usually win, but here we just check moves.
            # For simplicity in placement phase, we sample a few moves to save time.
            
            if not moves:
                return 10000 # If Goat can't move, Tiger might have won or it's a weird state
                
            # Optimization: If in placement phase, there are too many moves (empty spots).
            # We just pick a subset to analyze to keep it fast.
            if game.phase == 'PLACEMENT':
                if len(moves) > 5:
                    moves = random.sample(moves, 5)

            for start, end in moves:
                game_copy = copy.deepcopy(game)
                if game.phase == 'PLACEMENT':
                    game_copy.place_goat(end[0], end[1])
                else:
                    game_copy.make_move(start, end)
                    
                eval = self.minimax(game_copy, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def evaluate(self, game):
        """
        Heuristic Evaluation Function.
        Positive is good for Tiger.
        """
        score = 0
        
        # 1. Captures (Most Important)
        score += game.goats_captured * 1000
        
        # 2. Mobility (Avoid Traps)
        tiger_moves = self.get_all_tiger_moves(game)
        score += len(tiger_moves) * 10
        
        # 3. Position (Slight preference for center or key spots? Optional)
        # For now, mobility is the best proxy for "good position"
        
        return score

    def get_all_tiger_moves(self, game):
        moves = []
        for r in range(5):
            for c in range(5):
                if game.board[r][c] == -1: # Tiger
                    valid_destinations = game.get_valid_moves(r, c, check_turn=False)
                    for dest in valid_destinations:
                        moves.append(((r, c), dest))
        return moves

    def get_all_goat_moves(self, game):
        moves = []
        if game.phase == 'PLACEMENT':
            # In placement, "start" is None, "end" is the board position
            # But to keep format consistent, we'll use start=None
            for r in range(5):
                for c in range(5):
                    if game.board[r][c] == 0:
                        moves.append((None, (r, c)))
        else:
            for r in range(5):
                for c in range(5):
                    if game.board[r][c] == 1: # Goat
                        valid_destinations = game.get_valid_moves(r, c, check_turn=False)
                        for dest in valid_destinations:
                            moves.append(((r, c), dest))
        return moves
