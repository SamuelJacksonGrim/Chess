"""chess_lib.py — core library for the chess-duel skill.

Stateless chess: every position is a FEN string. No server, no database,
no API key. Validate moves, convert notation, read game status, list legal
moves. Built on python-chess (pip3 install python-chess).

CLI usage (preferred — no imports needed):
  python3 chess_lib.py validate "<fen>" "<move>"   # JSON: ok, error, fen, state, detail
  python3 chess_lib.py legal "<fen>"               # legal moves (SAN), one per line
  python3 chess_lib.py status "<fen>"              # game status line
"""

import json
import sys

import chess

DEFAULT_FEN = chess.STARTING_FEN


def board_from(fen):
    try:
        return chess.Board(fen)
    except ValueError as e:
        raise ValueError(f"bad FEN: {e}") from e


def game_status(fen):
    """Return (state, detail) for the position.

    state: in_progress | check | checkmate | stalemate |
           draw_insufficient_material | draw_fifty_moves | draw_repetition
    detail: winner color for checkmate, None otherwise.
    """
    b = board_from(fen)
    if b.is_checkmate():
        winner = "white" if b.turn == chess.BLACK else "black"
        return ("checkmate", winner)
    if b.is_stalemate():
        return ("stalemate", None)
    if b.is_insufficient_material():
        return ("draw_insufficient_material", None)
    if b.is_fifty_moves():
        return ("draw_fifty_moves", None)
    if b.is_repetition(3):
        return ("draw_repetition", None)
    if b.is_check():
        return ("check", None)
    return ("in_progress", None)


def legal_moves(fen, notation="san"):
    """List legal moves. notation: 'san' (default) or 'uci'."""
    b = board_from(fen)
    if notation == "uci":
        return [m.uci() for m in b.legal_moves]
    return [b.san(m) for m in b.legal_moves]


def validate_move(fen, move_text):
    """Try to apply move_text (SAN or UCI) to fen.

    Returns a dict:
      ok     — True if the move was legal and applied
      error  — rejection reason when ok is False
      fen    — new FEN after the move (input FEN when ok is False)
      state  — game status of the new position, or 'illegal'
      detail — winner for checkmate / legal moves on rejection
    """
    b = board_from(fen)
    move_text = move_text.strip()

    move = None
    try:
        move = chess.Move.from_uci(move_text)
        if move not in b.legal_moves:
            move = None
    except ValueError:
        move = None

    if move is None:
        try:
            move = b.parse_san(move_text)
        except ValueError:
            return {
                "ok": False,
                "error": f"illegal or unparseable move: {move_text!r}",
                "fen": fen,
                "state": "illegal",
                "detail": legal_moves(fen),
            }

    b.push(move)
    state, detail = game_status(b.fen())
    return {"ok": True, "error": None, "fen": b.fen(), "state": state, "detail": detail}


def _cli(argv):
    if len(argv) < 3:
        print(__doc__)
        return 1
    cmd = argv[1]
    if cmd == "validate" and len(argv) == 4:
        print(json.dumps(validate_move(argv[2], argv[3])))
    elif cmd == "legal" and len(argv) == 3:
        print("\n".join(legal_moves(argv[2])))
    elif cmd == "status" and len(argv) == 3:
        state, detail = game_status(argv[2])
        print(state + (f" ({detail})" if detail else ""))
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(_cli(sys.argv))
