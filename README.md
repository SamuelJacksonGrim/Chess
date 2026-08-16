# chess-duel

Play chess as an AI agent. Stateless, serverless, no API keys.

Three modes:

- **Agent vs agent** — the whole game is a FEN string passed between two
  agents over DMs. No board server, no shared state, no third party.
- **Agent vs engine** — spar against the bundled mini engine (negamax +
  alpha-beta, depth 3, piece-square tables, pure Python).
- **Agent vs human** — the human types SAN moves in chat; you validate and
  reply.

## Files

| File | Purpose |
| --- | --- |
| `SKILL.md` | Skill definition (iLands skill format) |
| `scripts/chess_lib.py` | Referee: move validation, SAN/UCI, game status |
| `scripts/mini_engine.py` | Sparring engine |
| `scripts/play_cli.py` | Interactive terminal game vs the engine |
| `scripts/self_test.py` | Smoke tests (`python3 self_test.py`) |

## Setup

```bash
pip3 install python-chess
```

## Protocol (one message = one move + its FEN)

```
fen=rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 move=e4
```

Validate every move before answering:

```bash
python3 scripts/chess_lib.py validate "<fen>" "<move>"
# {"ok": true, "error": null, "fen": "...", "state": "in_progress", "detail": null}
```

`state` is `checkmate` / `stalemate` / `draw_*` when the game is over;
`check` when the king is attacked; `illegal` (with a legal-move list in
`detail`) when the move is rejected.

## License

MIT. Free to use, remix, and sell. The value is the protocol, not the fence.
