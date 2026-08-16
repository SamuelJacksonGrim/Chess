"""mini_engine.py — bundled sparring engine for the chess-duel skill.

Negamax with alpha-beta pruning, captures-first move ordering, shallow
capture-only quiescence, piece-square table evaluation. Pure Python.
Strong enough to punish blunders. Weak enough that a human can win.

CLI:
  python3 mini_engine.py [--fen "<fen>"] [--depth 3] [--nodes 150000]

Prints: input FEN, best move (SAN + UCI), and the position after.
"""

import argparse

import chess

MATE = 100000

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000,
}

# Simplified evaluation function tables (white perspective, index 0 = a1).
PST = {
    chess.PAWN: [
        0, 0, 0, 0, 0, 0, 0, 0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5, 5, 10, 25, 25, 10, 5, 5,
        0, 0, 0, 20, 20, 0, 0, 0,
        5, -5, -10, 0, 0, -10, -5, 5,
        5, 10, 10, -20, -20, 10, 10, 5,
        0, 0, 0, 0, 0, 0, 0, 0,
    ],
    chess.KNIGHT: [
        -50, -40, -30, -30, -30, -30, -40, -50,
        -40, -20, 0, 0, 0, 0, -20, -40,
        -30, 0, 10, 15, 15, 10, 0, -30,
        -30, 5, 15, 20, 20, 15, 5, -30,
        -30, 0, 15, 20, 20, 15, 0, -30,
        -30, 5, 10, 15, 15, 10, 5, -30,
        -40, -20, 0, 5, 5, 0, -20, -40,
        -50, -40, -30, -30, -30, -30, -40, -50,
    ],
    chess.BISHOP: [
        -20, -10, -10, -10, -10, -10, -10, -20,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -10, 0, 5, 10, 10, 5, 0, -10,
        -10, 5, 5, 10, 10, 5, 5, -10,
        -10, 0, 10, 10, 10, 10, 0, -10,
        -10, 10, 10, 10, 10, 10, 10, -10,
        -10, 5, 0, 0, 0, 0, 5, -10,
        -20, -10, -10, -10, -10, -10, -10, -20,
    ],
    chess.ROOK: [
        0, 0, 0, 0, 0, 0, 0, 0,
        5, 10, 10, 10, 10, 10, 10, 5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        0, 0, 0, 5, 5, 0, 0, 0,
    ],
    chess.QUEEN: [
        -20, -10, -10, -5, -5, -10, -10, -20,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -10, 0, 5, 5, 5, 5, 0, -10,
        -5, 0, 5, 5, 5, 5, 0, -5,
        0, 0, 5, 5, 5, 5, 0, -5,
        -10, 5, 5, 5, 5, 5, 0, -10,
        -10, 0, 5, 0, 0, 0, 0, -10,
        -20, -10, -10, -5, -5, -10, -10, -20,
    ],
    chess.KING: [
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -20, -30, -30, -40, -40, -30, -30, -20,
        -10, -20, -20, -20, -20, -20, -20, -10,
        20, 20, 0, 0, 0, 0, 20, 20,
        20, 30, 10, 0, 0, 10, 30, 20,
    ],
}


def evaluate(board):
    """Static evaluation in centipawns, from White's perspective."""
    if board.is_checkmate():
        return -MATE if board.turn == chess.WHITE else MATE
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
    score = 0
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece is None:
            continue
        table = PST[piece.piece_type]
        idx = sq if piece.color == chess.WHITE else sq ^ 56
        value = PIECE_VALUES[piece.piece_type] + table[idx]
        score += value if piece.color == chess.WHITE else -value
    return score


class MiniEngine:
    """Small negamax engine with alpha-beta. Depth 3 default."""

    def __init__(self, depth=3, node_cap=150000):
        self.depth = depth
        self.node_cap = node_cap
        self.nodes = 0

    def best_move(self, board):
        """Return the engine's move for the side to move (None if game over)."""
        self.nodes = 0
        if board.is_game_over():
            return None
        moves = self._order(board)
        alpha, beta = -MATE - 1, MATE + 1
        best = moves[0]
        best_score = -MATE - 2
        for move in moves:
            board.push(move)
            score = -self._negamax(board, self.depth - 1, -beta, -alpha)
            board.pop()
            if score > best_score:
                best_score = score
                best = move
            if score > alpha:
                alpha = score
        return best

    def _negamax(self, board, depth, alpha, beta):
        self.nodes += 1
        if self.nodes > self.node_cap:
            return self._quiesce(board, alpha, beta, 1)
        if board.is_game_over():
            return -MATE if board.turn == chess.WHITE else MATE
        if depth <= 0:
            return self._quiesce(board, alpha, beta, 1)
        for move in self._order(board):
            board.push(move)
            score = -self._negamax(board, depth - 1, -beta, -alpha)
            board.pop()
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha

    def _quiesce(self, board, alpha, beta, qdepth):
        stand = evaluate(board)
        if stand >= beta:
            return beta
        if stand > alpha:
            alpha = stand
        if qdepth <= 0:
            return alpha
        for move in self._order(board, captures_only=True):
            board.push(move)
            score = -self._quiesce(board, -beta, -alpha, qdepth - 1)
            board.pop()
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha

    def _order(self, board, captures_only=False):
        moves = list(board.legal_moves)

        def key(move):
            score = 0
            victim = board.piece_at(move.to_square)
            attacker = board.piece_at(move.from_square)
            if victim is not None:
                score += 10 * PIECE_VALUES[victim.piece_type]
                if attacker is not None:
                    score -= PIECE_VALUES[attacker.piece_type]
            if move.promotion:
                score += PIECE_VALUES[move.promotion]
            return -score

        moves.sort(key=key)
        if captures_only:
            return [m for m in moves if board.is_capture(m) or m.promotion]
        return moves


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fen", default=chess.STARTING_FEN)
    parser.add_argument("--depth", type=int, default=3)
    parser.add_argument("--nodes", type=int, default=150000)
    args = parser.parse_args(argv)

    board = chess.Board(args.fen)
    if board.is_game_over():
        print(f"game over: {board.result()}")
        return 0

    engine = MiniEngine(depth=args.depth, node_cap=args.nodes)
    move = engine.best_move(board)
    print(f"fen:   {board.fen()}")
    print(f"best:  SAN={board.san(move)} UCI={move.uci()}  nodes={engine.nodes}")
    board.push(move)
    print(f"after: {board.fen()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
