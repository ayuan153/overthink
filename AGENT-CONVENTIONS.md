# AGENT-CONVENTIONS.md

> How any agent (human or AI) works in this repo. This project spans many sessions
> over months. These conventions are the contract that keeps work coherent across
> handoffs. Read this first, every session.

## The documentation spine

Four living documents carry state between sessions. Keep them honest and current.

| Doc | Role | Mutability |
|-----|------|------------|
| `VISION.md` | The long-term arc, the wedge, the north-star proof. Grounds every decision. | Rarely changes. Changing it is a deliberate, flagged act. |
| `DESIGN.md` | Architecture, current scope, key technical decisions. The "how". | Evolves as design matures. |
| `STATUS.md` | The handoff baton: where we are right now, what's next, what's blocked. | Updated **every** session. |
| `DECISIONS.md` | Append-only log: date · decision · alternatives · why. | Append only. Never rewrite history. |

## Session ritual (non-negotiable)

**START every session by:**
1. Reading `VISION.md`, `STATUS.md`, and `DESIGN.md`.
2. Restating the north star in one sentence (out loud, in your first response).
3. Confirming the current phase and the next concrete task from `STATUS.md`.

**DURING the session:**
- Check meaningful decisions against `VISION.md`. If a decision would change the
  long-term vision, **make it explicit and flag it to the human** — do not silently decide.
- Prefer reversible, local actions. Flag destructive or high-blast-radius actions.

**END every session by:**
1. Updating `STATUS.md` (what changed, what's next, what's blocked).
2. Appending any meaningful decisions to `DECISIONS.md`.
3. Never leaving the repo in a broken state (docs consistent; if code exists, it builds).

## Phase discipline

This project is built in explicit phases. **Do not jump ahead.**
- **Phase 0 (current): research + design only. NO production code.** Output is the doc spine.
- Later phases build code only after the design they implement is locked in `DESIGN.md`.
- If a phase's scope is ambiguous, stop and ask rather than guessing.

## Honesty rules

- Re-verify external facts (incumbent capabilities, paper IDs, model availability) —
  they go stale. Cite sources. Flag anything unverified before it reaches a public doc.
- Distinguish "shipped/confirmed" from "aspirational/unverified" everywhere.
- No scope inflation. v0.1 is deliberately small. The launch milestone is deliberately
  bigger and is a separate, explicit target.

## North star (do not let detail-work erode this)

> **Make any model reason *optimally* — the right amount of compute for each prompt** —
> via compute-optimal test-time scaling, with **real deep MCTS + pluggable PRMs +
> per-prompt budget allocation** as the differentiator, and the compute decision
> **transparent/auditable, not a black box**. Applies *to* native reasoning models
> (which default to high/`xhigh` effort and over-think trivial prompts). The launch
> milestone is the MCTS+PRM+budget demo, not the v0.1 plumbing.

`paretothink` is **standalone-first**: its own eval/benchmark harness, zero sibling
dependency. It is the portfolio anchor. Resist coupling it to anything else.
