---
name: chess-duel
description: "Play a full chess game as an agent: versus another agent (stateless FEN handoff over DMs), versus the bundled mini engine, or versus a human. Validated moves, SAN/UCI notation, no server, no API key. Use when a chess match, chess game, or agent-vs-agent board game is requested."
allowed-tools: Bash(python3:*) Bash(pip3 install python-chess:*)
metadata:
  ilands:
    applicable-to: [full]
    priority: 2.0
    kind: atomic_skill
---

# Chess Duel

Play chess as an agent. Three modes:

1. **Agent vs agent** — two agents exchange moves over DMs. Stateless: the whole game fits in one FEN string per message. No server, no shared board, no third party.
2. **Agent vs engine** — spar against the bundled mini engine (negamax + alpha-beta, depth 3, piece-square tables). Good for practice, demos, and warm-ups.
3. **Agent vs human** — the human plays in chat (SAN moves like `e4`, `Nf3`, `O-O`); you validate and reply.

## Setup

One time per environment:

```bash
pip3 install python-chess
```

The skill ships three scripts under `scripts/`:

- `chess_lib.py` — validation, notation, game status. The referee. Use this, don't edit it.
- `mini_engine.py` — the sparring engine.
- `play_cli.py` — interactive terminal game vs the engine (for humans).

## Referee CLI (preferred: no imports needed)

```bash
python3 scripts/chess_lib.py validate "<fen>" "<move>"   # JSON: ok, error, fen, state, detail
python3 scripts/chess_lib.py legal "<fen>"               # legal moves, SAN, one per line
python3 scripts/chess_lib.py status "<fen>"              # in_progress | check | checkmate (winner) | stalemate | draw_*
```

## Protocol (agent vs agent)

**One message = one move + the FEN it applies to.** Nothing else.

- Opening message from White:

  `fen=rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 move=e4`

- Reply from Black: same shape, new FEN, their move.

  `fen=rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1 move=e5`

- Moves may be SAN (`e4`, `Nf3`, `exd5`, `O-O`, `Qh4#`) or UCI (`e2e4`, `e1g1`).

Before answering, validate the received move:

```bash
python3 scripts/chess_lib.py validate "<received fen>" "<received move>"
```

- `ok: true` → apply. Reply with the returned `fen` + your own move.
- `state: "checkmate"` / `"stalemate"` / `"draw_*"` → the game is over. Announce the result (`detail` names the winner) and offer a rematch. Do not move.
- `state: "check"` → warn the opponent in the same reply ("check").
- `ok: false` → do NOT move. Reply with the rejection and `python3 scripts/chess_lib.py legal "<fen>"` so the opponent can fix their move.

## Playing vs the engine

```bash
python3 scripts/mini_engine.py --fen "<fen>" [--depth 3] [--nodes 150000]
# prints: fen, best move (SAN + UCI), position after
```

Loop: validate your own move with `chess_lib.py`, take the returned FEN, feed it to the engine, repeat.

## Etiquette

- Always include the FEN you are moving from. A move without a FEN is unverifiable; ask for the FEN before answering.
- One move per message. No analysis dumps, no engine chatter.
- Claim the draw on threefold repetition or the 50-move clock instead of stalling.
- Resign plainly ("I resign"); don't ghost a game in progress.
- Never claim a win the referee didn't confirm. `chess_lib.py validate` is the referee; if it says `in_progress`, play on.
