# chess-duel

[![License: AGPL-3.0-only](https://img.shields.io/badge/license-AGPL--3.0--only-blue)](LICENSE)
[![dual-license](https://img.shields.io/badge/dual--license-AGPL--3.0--only%20or%20commercial-blueviolet)](LICENSING.md)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://www.python.org)

## License

This project is dual-licensed under **AGPL-3.0-only** OR a commercial license.

- [LICENSE](LICENSE) — GNU AGPL-3.0-only (the free track)
- [LICENSING.md](LICENSING.md) — how the two tracks work
- [COMMERCIAL-LICENSE.md](COMMERCIAL-LICENSE.md) — the commercial agreement
- [NOTICE](NOTICE) — copyright, SPDX identifier, and provenance


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

