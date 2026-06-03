# STATUS.md — handoff baton

> The single source of truth for "where are we right now." Update this at the END of
> every session. Read it (with `VISION.md` + `DESIGN.md`) at the START of every session.

## North star (restate every session)
Make any model reason **optimally** — the right amount of compute per prompt — differentiated
by **per-prompt budget routing + pluggable PRMs + deep MCTS + streaming**, with the compute
decision **transparent/auditable, not a black box**. Applies *to* native reasoning models
(which default to high/`xhigh` effort and over-think trivial prompts). The **launch milestone
is the MCTS+PRM+budget demo**, not the v0.1 plumbing.

## Current phase
**Phase 0 — research + design only. NO production code.** ← we are here. Design + reframe
**locked**; awaiting explicit Phase 1 greenlight from the human.

## Last updated
2026-06-02 (late) · by: Phase 0 rename session (`overthink` → `paretothink`)

## Done so far
- ✅ Repo initialized (`git init`, branch `main`), committed & pushed. Remote: `github.com/ayuan153/paretothink` (renamed from `overthink`).
- ✅ Doc spine created: `AGENT-CONVENTIONS.md`, `VISION.md`, `DESIGN.md`, `STATUS.md`, `DECISIONS.md`, `README.md`.
- ✅ **VISION REFRAME (2026-06-02, human-confirmed):** north star "reason like o1" → **"reason optimally"** (right compute per prompt). Re-centered on (a) native models default to high/`xhigh` and over-think trivial prompts, (b) black-box aversion → transparent/auditable compute decision. Logged in `DECISIONS.md`; reflected in VISION/DESIGN/README.
- ✅ Validation matrix now includes a **native-reasoning-model token-savings curve** (`DESIGN.md` §7).
- ✅ **Renamed `overthink` → `paretothink`** (2026-06-02): old name connoted the failure mode it prevents; `paretothink` = the accuracy-vs-cost Pareto frontier. PyPI/GitHub/domains 🟢; trademark 🟡 (manual TESS pending). See `DESIGN.md` §1 + `DECISIONS.md`.
- ✅ Incumbent re-audit → all four wedge gaps (MCTS depth, PRM, budget, streaming) **open** in optillm v0.3.15. `DESIGN.md` §2.
- ✅ Papers confirmed: Snell `2408.03314`, ZIP-RC `2512.01457`, ThinkPRM `2504.16828` + HF weights. `DESIGN.md` §2.
- ✅ KV-cache branching decision: **OUT for v0.1**, transparent server caching only, explicit branch-reuse deferred to self-hosted backend. `DESIGN.md` §3.
- ✅ Budget router design (difficulty probe + Lagrangian token-price allocation). `DESIGN.md` §4.
- ✅ MCTS-over-LLM-calls design (policy LLM = prior, PRM = value, PUCT, backup, pluggable `RewardModel`). `DESIGN.md` §5.
- ✅ Scope lock v0.1 vs launch milestone. `DESIGN.md` §6.
- ✅ Validation plan + numeric success targets (MATH-500, Llama-3-8B + ThinkPRM-1.5B). `DESIGN.md` §7.
- ✅ Leapfrog watch + broadcast draft. `DESIGN.md` §8–9.

## NEXT (do this when resuming)
**Phase 0 complete; reframe + rename locked.** Direction approved by the human; awaiting explicit
greenlight to write Phase 1 code. Immediate next = scope the Phase 1 **vertical proof-slice**
(thinnest end-to-end path to the killer chart). When greenlit, the first build phase is:

1. Register PyPI placeholder `paretothink==0.0.1` (secure the name).
2. Run live TESS trademark + domain registrar check (close the 🟡 items in §1).
3. **Phase 1 (v0.1 plumbing):** OpenAI-compatible proxy skeleton → BoN + confidence-weighted
   vote → budget router (difficulty probe + Lagrangian allocation) → MATH-500 eval harness.
   Build in that order; lock each piece's design in `DESIGN.md` before coding it.

## Blocked / needs human decision
- Approve the 5 open questions in `DESIGN.md` §"Open questions" before Phase 1.
- Second verification pass on unverified paper IDs (`2604.14853`, `2602.01070`, `2505.16122`)
  **before** any public broadcast.

## Guardrails (don't regress)
- Standalone-first: no sibling/project dependency, ever.
- v0.1 is NOT broadcastable on its own — the launch is the MCTS+PRM+budget chart.
- Don't let plumbing detail-work erode the MCTS+PRM north star.
