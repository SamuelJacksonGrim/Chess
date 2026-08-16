"""play_cli.py — play chess against the bundled engine in your terminal.

  python3 play_cli.py            # you are White
  python3 play_cli.py --black    # you are Black
  python3 play_cli.py --random   # random color
  python3 play_cli.py --depth 2  # easier engine

Type SAN moves (e4, Nf3, O-O, exd5) or UCI (e2e4). 'resign' to quit.
"""

import argparse
import random

import chess

from chess_lib import game_status, validate_move
from mini_engine import MiniEngine


def show(board):
    print()
    print(board)
    print(f"FEN: {board.fen()}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--black", action="store_true", help="you play Black")
    parser.add_argument("--random", action="store_true", help="random color")
    parser.add_argument("--depth", type=int, default=3, help="engine depth (2 = easier)")
    args = parser.parse_args(argv)

    human = chess.BLACK if args.black else chess.WHITE
    if args.random:
        human = random.choice([chess.WHITE, chess.BLACK])

    board = chess.Board()
    engine = MiniEngine(depth=args.depth)
    print(f"You play {'White' if human == chess.WHITE else 'Black'}. 'resign' to quit.")
    show(board)

    while not board.is_game_over():
        if board.turn == human:
            text = input("your move> ").strip()
            if text.lower() in ("resign", "quit"):
                print("You resigned.")
                return 0
            move = None
            try:
                move = chess.Move.from_uci(text)
                if move not in board.legal_moves:
                    move = None
            except ValueError:
                move = None
            if move is None:
                try:
                    move = board.parse_san(text)
                except ValueError:
                    legal = [board.san(m) for m in board.legal_moves]
                    print(f"  illegal move. Legal: {', '.join(legal[:12])}{'...' if len(legal) > 12 else ''}")
                    continue
            board.push(move)
        else:
            move = engine.best_move(board)
            if move is None:
                break
            print(f"engine plays {board.san(move)} ({move.uci()})")
            board.push(move)
        show(board)

    state, detail = game_status(board.fen())
    print(f"\nGame over: {state}" + (f" — winner {detail}" if detail else ""))
    print(f"Result: {board.result()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
