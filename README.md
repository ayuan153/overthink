# overthink

> Make any model reason *optimally* — the right amount of compute for each prompt,
> via compute-optimal test-time scaling.

`overthink` is a fast, pluggable **test-time-compute engine**: an OpenAI-compatible
proxy that decides *how hard your model should think on each prompt* — through best-of-N,
confidence-weighted voting, **deep MCTS**, **pluggable Process Reward Models (PRMs)**,
and the differentiator: **compute-optimal per-prompt budget allocation** (more compute on
hard prompts, less on easy ones). It works *on* native reasoning models too — capping the
10K–40K-token default-effort overthinking on trivial prompts — with a compute decision you
can see and tune, not a black box.

> **Status: Phase 0 — design only. No production code yet.** This repo currently
> contains the design spine. Implementation begins after human review of `DESIGN.md`.

## Read these first
- **[VISION.md](./VISION.md)** — the long-term arc, the wedge, the north-star proof.
- **[DESIGN.md](./DESIGN.md)** — architecture, locked v0.1 scope, key decisions.
- **[STATUS.md](./STATUS.md)** — where the project is right now (handoff baton).
- **[DECISIONS.md](./DECISIONS.md)** — append-only rationale log.
- **[AGENT-CONVENTIONS.md](./AGENT-CONVENTIONS.md)** — how to work in this repo across sessions.

## The wedge (vs `optillm`)
1. Compute-optimal **per-prompt budget routing** (Snell 2408.03314; ZIP-RC 2512.01457).
2. Real **pluggable PRMs** for step-level scoring (ThinkPRM, Qwen2.5-Math-PRM).
3. Genuine **deep MCTS** over LLM calls, with the PRM as the value signal.
4. **Streaming** of partial results during multi-step search.

## North-star proof
On MATH-500 with Llama-3-8B-Instruct: accuracy climbs 1-shot → BoN-8 → MCTS+PRM, and
**adaptive budget matches fixed BoN-16 accuracy at ~40% of the token cost.** On a native
reasoning policy, the same router **holds accuracy while cutting 40–60% of default-effort
thinking tokens.**
