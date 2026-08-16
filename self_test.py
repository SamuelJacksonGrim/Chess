"""self_test.py — smoke tests for the chess-duel skill.

Run: python3 self_test.py
Exit 0 = all checks pass. Prints one line per check.
"""

import chess

from chess_lib import game_status, legal_moves, validate_move
from mini_engine import MiniEngine

COUNT = 0


def check(name, cond, extra=""):
    global COUNT
    if not cond:
        print(f"FAIL: {name} {extra}")
        raise SystemExit(1)
    COUNT += 1
    print(f"ok {COUNT:02d}: {name}")


def main():
    # 1. Starting position: 20 legal moves.
    check("start has 20 legal moves", len(legal_moves(chess.STARTING_FEN)) == 20)

    # 2. SAN moves apply and return a new FEN.
    res = validate_move(chess.STARTING_FEN, "e4")
    check("SAN e4 applies", res["ok"] and res["fen"].startswith("rnbqkbnr/pppppppp/8/8/4P3"))
    res = validate_move(res["fen"], "e5")
    check("SAN e5 reply", res["ok"])
    res = validate_move(res["fen"], "Nf3")
    check("SAN Nf3", res["ok"])

    # 3. UCI move applies.
    res = validate_move(chess.STARTING_FEN, "g1f3")
    check("UCI g1f3 applies", res["ok"] and res["fen"].startswith("rnbqkbnr/pppppppp/8/8/8/5N2"))

    # 4. Illegal move rejected, with legal moves in detail.
    res = validate_move(chess.STARTING_FEN, "e5")
    check("illegal e5 rejected", (not res["ok"]) and res["state"] == "illegal" and len(res["detail"]) == 20)

    # 5. Castling.
    board = chess.Board()
    for mv in ["e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5"]:
        res = validate_move(board.fen(), mv)
        check(f"opening line move {mv}", res["ok"])
        board = chess.Board(res["fen"])
    res = validate_move(board.fen(), "O-O")
    check("castling O-O applies", res["ok"] and res["fen"].split()[2] == "kq")

    # 6. Fool's mate detection (1.f3 e5 2.g4 Qh4#).
    board = chess.Board()
    for mv in ["f3", "e5", "g4", "Qh4"]:
        res = validate_move(board.fen(), mv)
        check(f"fool's mate move {mv}", res["ok"])
        board = chess.Board(res["fen"])
    state, detail = game_status(board.fen())
    check("fool's mate detected", state == "checkmate" and detail == "black")

    # 7. Check status flag on a plain check.
    board = chess.Board()
    for mv in ["e4", "e5", "Bc4", "Bc5", "Qh5", "Nc6", "Qxf7"]:
        res = validate_move(board.fen(), mv)
        check(f"scholar's line {mv}", res["ok"])
        board = chess.Board(res["fen"])
    state, _ = game_status(board.fen())
    check("scholar's mate detected", state == "checkmate")

    # 8. Engine self-play: legal moves throughout, game resolves or truncates.
    engine = MiniEngine(depth=2, node_cap=60000)
    board = chess.Board()
    plies = 0
    while not board.is_game_over() and plies < 60:
        move = engine.best_move(board)
        check(f"engine move {plies + 1} available", move is not None)
        board.push(move)
        plies += 1
    check("self-play ran at least 20 plies", plies >= 20)
    check("self-play resolved or truncated", board.is_game_over() or plies == 60)

    print(f"\nAll {COUNT} checks passed.")


if __name__ == "__main__":
    main()
