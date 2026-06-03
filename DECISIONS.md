# DECISIONS.md — append-only log

> Format: `date · decision · alternatives · why`. **Append only.** Never rewrite history.
> Any decision that would change `VISION.md` must be flagged to the human (mark it ⚠️).

---

### 2026-06-01 · Project name = `overthink`
- **Alternatives:** `ponder` (fallback).
- **Why:** `overthink` PyPI name is free; GitHub namespace is only a personal user; no
  obvious trademark conflict. `ponder` is blocked on PyPI (claimed/yanked, PEP 541 reclaim
  uncertain) and collides with `ponder-sh/ponder` (1.1k★) and `ponder.ai` (YC). PyPI
  availability is the hard constraint for a pip-installable tool. Action: register `0.0.1`
  placeholder to secure; live TESS/domain check still pending.

### 2026-06-01 · KV-cache-aware branching is OUT for v0.1
- **Alternatives:** (a) build explicit fork/clone in v0.1; (b) drop prefix reuse entirely.
- **Why:** Against a remote OpenAI-compatible endpoint we do not control, there is no API
  to fork/reuse server KV state — explicit branching is infeasible without owning the
  server. v0.1 instead relies on **transparent** server-side prefix caching (vLLM APC /
  SGLang RadixAttention) by keeping shared prefixes byte-stable. Explicit branch-reuse is
  deferred to a post-launch, self-hosted-backend phase. Keeps v0.1 honest and
  endpoint-agnostic.

### 2026-06-01 · Budget router IP = Lagrangian "price-of-tokens" allocation
- **Alternatives:** (a) fixed per-difficulty-bin schedules (Snell-style lookup); (b) a
  heavy learned classifier like optillm's ModernBERT router; (c) pure ZIP-RC early-stop.
- **Why:** A single token-price `λ` with marginal-gain-per-token stopping makes the entire
  accuracy-vs-cost frontier a tunable knob — which is exactly what produces the killer
  "match BoN-16 at 40% tokens" chart. Difficulty is estimated cheaply via a probe pass
  (consensus + confidence + dispersion), upgradable to a small learned head. Avoids a heavy
  classifier in v0.1; black-box early-stop keeps it endpoint-agnostic, with ZIP-RC
  introspection as a white-box upgrade on local backends.

### 2026-06-01 · MCTS value signal = pluggable PRM (policy LLM = prior, PRM = value)
- **Alternatives:** LLM-as-judge scoring (optillm's approach); regex/consistency heuristics
  (rStar's approach); outcome-only reward.
- **Why:** Maps the builder's AlphaZero background directly (policy = move priors, value =
  network). A real, swappable PRM as the value head is the core differentiator vs optillm's
  LLM-as-judge. A clean `RewardModel` Protocol (`score_steps` / `score_final`) seeds the
  long-term PRM ecosystem. Default validation PRM: `launch/ThinkPRM-1.5B` (single-GPU friendly).

### 2026-06-01 · v0.1 ships first but is NOT broadcast; launch = MCTS+PRM+budget+streaming
- **Alternatives:** broadcast v0.1 (proxy + BoN + budget router) to get early signal.
- **Why:** v0.1 alone is "optillm-lite" and not differentiated enough to announce. The
  defensible, high-signal story is the MCTS+PRM+budget cost-frontier demo. Budget ~6–8
  weeks to a convincing launch, not 3. v0.1 exists to prove plumbing + the difficulty
  estimator. (Consistent with `VISION.md`; not a vision change.)

### 2026-06-01 · Validation north star = MATH-500, Llama-3-8B-Instruct, single GPU
- **Alternatives:** GSM8K (too easy, saturates), AIME (too small/noisy for a frontier curve).
- **Why:** MATH-500 has enough difficulty spread to show per-prompt budget allocation paying
  off, and runs on a single GPU with an 8B policy + 1.5B PRM. Primary success metric: adaptive
  budget matches BoN-16 accuracy within ±0.5pp at ≤40% of its token cost.

### 2026-06-01 · Newer 2026 TTC papers flagged UNVERIFIED
- **Decision:** Do not cite `2604.14853`, `2602.01070`, `2505.16122` publicly until a second
  verification pass confirms IDs/titles.
- **Why:** Returned with future-dated/near-future arXiv IDs from a single research pass;
  honesty rule requires confirmation before they reach a public document. The three core
  anchors (Snell, ZIP-RC, ThinkPRM) are confirmed and safe to cite.

### 2026-06-02 · ⚠️ VISION REFRAME: north star "reason like o1" → "reason *optimally*"
- **Trigger:** mid-2026 landscape scan — 5+ open families (DeepSeek-R1/R2, Qwen3 hybrid,
  QwQ, Phi-4-reasoning) now reason natively, so "make non-reasoning models reason" is
  drifting toward solved at the model layer. Human reviewed and confirmed.
- **Decision:** Shift the north star verb from *reason like o1* → ***reason optimally***
  (the right amount of compute per prompt). Wedge re-centered on two durable, unoccupied
  pains: (1) native models default to high/`xhigh` effort and burn 10K–40K tokens on
  trivial "search-engine" prompts; (2) **black-box aversion** — teams need more
  intelligence in the compute decision but refuse to hand it to an opaque model, so the
  router + PRM trace must be **transparent and auditable**. Now applies *to* reasoning
  models, not just non-reasoning ones.
- **Alternatives:** (a) keep "reason like o1" (rejected — commoditizing); (b) pivot fully
  to a pure cost-optimizer and drop the MCTS+PRM centerpiece (rejected — search+PRM is
  *how* you spend deep compute at the hard end, and is the portfolio/narrative anchor).
- **Why this is a nudge, not a rewrite:** architecture, build order, MCTS+PRM launch
  showcase, AlphaZero narrative, standalone-first, single-GPU validation, and the killer
  chart all stand. Only the framing/emphasis and the validation matrix change. The
  AlphaZero story actually strengthens: search that *knows when to stop* is cheaper than
  a reasoning model thinking on its own. Flagged as VISION-level per AGENT-CONVENTIONS.

### 2026-06-02 · Validation matrix gains a native-reasoning-model token-savings curve
- **Decision:** Add a second policy to §7 (a native reasoning model, e.g.
  `DeepSeek-R1-Distill-Qwen-7B` / Qwen3-thinking) and a third curve: on that policy,
  adaptive budget **holds accuracy within ±0.5pp while cutting ≥40% of default-effort
  thinking tokens.** This is the proof that lands in today's world (tokens saved, not
  accuracy added) and is produced by the *same* router code.
- **Alternatives:** keep only the non-reasoning Llama-3-8B accuracy-vs-cost chart
  (rejected — it no longer reflects where the pain actually is in mid-2026).
- **Why:** directly evidences the reframed north star and the broadcast hook. No new GPU
  budget (same single-GPU setup, swap the policy).

### 2026-06-02 · Project renamed `overthink` → `paretothink`
- **Supersedes** the 2026-06-01 "Project name = `overthink`" entry above (kept for history).
- **Why rename:** `overthink` connotes the *failure mode the tool prevents* — overthinking =
  wasteful — which directly contradicts the reframed pitch ("reason **optimally**"). `paretothink`
  instead names the value: pushing each prompt onto the **accuracy-vs-cost Pareto frontier**, the
  exact shape of the north-star chart, and it reads natively to the technical/lab (MTS) audience.
  Narrative bonus: `overthink → paretothink` flips the "think" valence from *too much* → *optimal*.
- **Alternatives considered (PyPI-gauntleted 2026-06-02):** `pareto` (BLOCKED — PyPI taken + "Pareto
  Security" brand + crowded namespace), `throttle` (BLOCKED — taken; connotes *limiting* not
  *optimizing*), `governor` (BLOCKED — taken + Rust rate-limiter brand), `paropt` (GO but obscure +
  34★ academic repo collision), `rightthink` (rejected — Newspeak/Orwell echo: goodthink/crimethink).
- **Availability:** `paretothink` PyPI 🟢 free; GitHub 🟢 no collision; domains `.com/.dev/.ai/.io`
  🟢 no DNS record (likely free); trademark 🟡 no direct conflict (nearest unrelated: Pareto Security,
  a UK "Pareto Thinking" coach, the "ParaThinker" paper) — **confirm registrar purchase + manual
  USPTO TESS before any spend/launch.**
- **Note on the `-think` suffix:** weaker Orwell concern than `rightthink` because `pareto` is a
  neutral technical term, not an ideological-correctness word. Accepted.
- **Scope of rename:** all 6 Phase-0 docs updated; GitHub repo renamed `overthink` → `paretothink`
  + remote URL updated; PyPI placeholder still to register. English verb "overthinking" in prose
  left intact (it is not the project name).