# DESIGN.md — `overthink` Phase 0

> Phase-0 output: architecture, locked v0.1 scope, and key decisions. **No production
> code exists yet and none should be written until the design it implements is locked
> here.** Read `VISION.md` first; this document serves it.

**Status:** Phase 0 design — reframe approved 2026-06-02 ("reason *optimally*"); locked, pending Phase 1 greenlight.
**Last verification pass:** 2026-06-01 (re-verify before any public broadcast).

---

## 0. North star (restated)

Make any model reason **optimally** — the right amount of compute for each prompt —
differentiated by **per-prompt budget routing + real pluggable PRMs + deep MCTS +
streaming**, with the compute decision **transparent and auditable** rather than left to
the model as a black box. This applies *to* native reasoning models (which default to
high / `xhigh` effort and over-think trivial, search-engine-style prompts), not just
non-reasoning ones. The launch milestone is the MCTS+PRM+budget demo, not v0.1.

---

## 1. Name check — `overthink` → GO

| Channel | `overthink` | `ponder` (fallback) |
|---|---|---|
| **PyPI** (hard constraint) | 🟢 **Available** — `/simple/overthink/` 404, unregistered. | 🔴 **Blocked** — name claimed (yanked `ponder-org` pkg); PEP 541 reclaim slow/uncertain. |
| **GitHub** | 🟢 `github.com/overthink` is a personal user (no competing project). | 🔴 `ponder-sh/ponder` (1.1k★ EVM indexer) + others. |
| **Domain** | 🟡 `overthink.dev` / `.ai` did not resolve (likely free; unconfirmed). | 🔴 `ponder.ai` taken (YC voice-AI). |
| **Trademark** | 🟡 No obvious USPTO conflict in SW/AI (live TESS not run). | 🔴 Multiple active "Ponder" AI marks. |

**Decision:** Use **`overthink`**. Register a placeholder `0.0.1` on PyPI promptly to
secure the name. Treat domain/trademark as 🟡 unconfirmed — do a live TESS + registrar
check before any spend or public launch.

---

## 2. Incumbent + literature audit (dated 2026-06-01)

### Incumbent: `optillm` (`algorithmicsuperintelligence/optillm`, ~4.1k★, v0.3.15, 918 commits)

| Wedge axis | optillm today | Gap |
|---|---|---|
| **MCTS depth** | Default `mcts_depth=1`, `mcts_simulations=2`. `simulate()` loops `range(depth)`; depth>1 just chains random LLM rollouts — no value net, no PRM. (`rstar.py` goes to depth=3 but scores via regex + word-overlap consistency.) | **OPEN** — no genuine search with a real value signal. |
| **Pluggable PRM** | None. `mcts.py` asks the LLM to "score 0–1" (LLM-as-judge); `rstar.py` uses regex confidence. No `reward_model` param/callback/config anywhere. | **WIDE OPEN** |
| **Compute-optimal budget** | `router_plugin.py` uses a ModernBERT classifier to pick *which technique* (13 options); `effort` hardcoded 0.7. Does not adjust *how much* compute per prompt. `AutoThink` is local-decode only. | **MOSTLY OPEN** |
| **Streaming (multi-step)** | `generate_streaming_response()` wraps the already-computed final answer in SSE chunks. Real streaming only for `none` passthrough. | **WIDE OPEN** |

Recent commits (Mar–Jun 2026): a "compact" context-compression plugin (PR #305) and
ARM64/spaCy maintenance. **No MCTS / PRM / budget / streaming work in the pipeline.**
→ All four wedge gaps are open today. The wedge is live.

### Literature anchors

**Confirmed (safe to cite publicly):**
- **arXiv 2408.03314** — Snell et al., *"Scaling LLM Test-Time Compute Optimally can be
  More Effective than Scaling Model Parameters."* Compute-optimal **per-prompt** allocation
  is >4× more token-efficient than best-of-N and can beat a 14× larger model FLOPs-matched.
  → anchors the **budget router**.
- **arXiv 2512.01457** — *"Zero-Overhead Introspection for Adaptive Test-Time Compute"*
  (ZIP-RC). Repurposes unused logits to predict reward + remaining cost per token; a
  sampling-utility (E[max reward] − compute − latency) drives early-stop/continue/resample.
  +up to 12% over majority vote at equal/lower cost. → anchors **early-stopping**.
- **arXiv 2504.16828** — *"Process Reward Models That Think"* (ThinkPRM). Generative PRM
  that emits a verification CoT; trained on ~1K synthetic examples; beats discriminative
  PRMs trained on 100× more data. → anchors the **pluggable PRM**.

**Available PRM weights (HuggingFace):**
- `launch/ThinkPRM-1.5B` / `-7B` / `-14B` (base: DeepSeek-R1-Distill-Qwen). Generative.
- `Qwen/Qwen2.5-Math-PRM-7B` (also 72B). Discriminative, `<extra_0>` step token, ~180k dl/mo.
- `RLHFlow/Llama3.1-8B-PRM-Deepseek-Data`. Discriminative.
  → v0.1 validation PRM target: **`launch/ThinkPRM-1.5B`** (fits a single GPU beside an 8B policy).

**⚠️ Unverified — do NOT cite publicly until a second pass confirms:** `2604.14853`,
`2602.01070`, `2505.16122` (Plan-and-Budget). Returned with future-dated/near-future IDs;
treat as leads, not citations.

---

## 3. Hardest unknown — KV-cache-aware branching against a remote endpoint

**Question:** can sibling expansions in the search tree reuse the shared prefix's KV
cache to avoid re-encoding the prompt on every branch?

**Finding:** Against a **remote OpenAI-compatible endpoint we do not control, no.** The
Chat Completions API exposes no handle to fork, clone, or reuse server-side KV state.
Explicit KV-branching requires owning the server.

**Decision (explicit scope call):**
- **v0.1: OUT.** No explicit KV fork/clone API. We do not pretend to control a remote KV cache.
- **Mitigation that works today:** lean on **transparent server-side prefix caching**
  (vLLM Automatic Prefix Caching, SGLang RadixAttention). It needs no API change, and our
  tree naturally produces siblings that share a **byte-identical prefix** → automatic
  cache hits. We will **design prompts so shared prefixes are byte-stable** (no
  nondeterministic interpolation in the shared portion) to maximize transparent reuse.
- **Later (post-launch) feature, gated on a self-hosted backend:** explicit
  branch/prefix-reuse via a vLLM/SGLang adapter that owns the cache. Logged as a future
  axis, not a v0.1 promise.

This keeps v0.1 honest (works against any endpoint) while preserving the upside on
self-hosted backends.

---

## 4. The budget router (core IP) — concrete design

Two components: a **per-prompt difficulty estimator** and a **compute-optimal allocation
policy**. The allocation is framed as constrained optimization (matches Snell's
per-prompt-optimal result), which is what makes the killer chart possible.

### 4.1 Difficulty estimator `d(x) ∈ [0,1]`

Cheap-first, escalate only if needed:

1. **Probe pass:** generate `k0` (default 2) low-cost samples at moderate temperature.
2. **Signals (black-box-friendly, work against any endpoint):**
   - **Consensus** — fraction of probes whose extracted answers agree.
   - **Self-reported confidence** — parsed from a lightweight "confidence: 0–1" suffix.
   - **Probe dispersion** — answer entropy / number of distinct answers.
   - *(If logits ARE available — local vLLM — add ZIP-RC-style introspection: predicted
     reward + remaining-cost from spare logits. Optional, backend-gated.)*
3. **Estimator:** v0.1 = a transparent **calibrated heuristic** combining the signals
   (high consensus + high confidence ⇒ low `d`). Upgrade path = a small learned
   regression head over probe features, calibrated on the eval set. No heavy classifier
   in v0.1 — the probe IS the difficulty signal.

### 4.2 Allocation policy — Lagrangian "price of tokens"

We allocate marginal compute where the **predicted marginal accuracy gain per token** is
highest, under a global token budget. Concretely:

- Each prompt has a budget-response curve `a_i(b)` = predicted accuracy as a function of
  tokens `b` (monotone, concave; parameterized by `d(x)` — hard prompts have a curve that
  keeps rising, easy prompts saturate immediately).
- Choose a single **token price `λ`** and, per prompt, spend until
  `da_i/db < λ` (marginal gain no longer worth the price). Easy prompts stop almost
  immediately; hard prompts keep buying compute.
- **Sweeping `λ` traces the entire accuracy-vs-cost frontier** — this is exactly the
  knob that produces "match BoN-16 accuracy at 40% of the tokens."

**Mechanism the policy controls** (in increasing cost order):
`k0` probes → early-stop on consensus → escalate to **BoN-`N`** with weighted vote →
escalate to **MCTS** (sets `simulations`, `depth`, branching `m`). The router decides
*which rung and how far up* per prompt; ZIP-RC-style early-stop can halt mid-rung.

### 4.3 Early stopping

- **Black-box (any endpoint):** sequential consensus — stop as soon as the running
  weighted vote crosses a confidence threshold (cheap, robust).
- **White-box (local logits):** ZIP-RC sampling-utility meta-actions (stop/continue/resample).
- The two share one interface so the policy is backend-agnostic.

This is the differentiator optillm's technique-router does not touch: it adjusts **how
much** compute, per prompt, against a global budget — not just **which** technique.

---

## 5. MCTS-over-LLM-calls (the launch showcase)

The builder's AlphaZero / self-play background maps directly:

| AlphaZero | `overthink` MCTS |
|---|---|
| Policy network (move priors) | **Policy LLM** — samples candidate next reasoning steps; its sequence prob is the prior `P(s,a)`. |
| Value network | **PRM** — scores a partial trajectory `V(s) ∈ [0,1]`. The PRM *is* the value head. |
| Game tree | **Reasoning tree** — nodes are solution prefixes. |
| Self-play result | **Outcome check** at terminals (answer extraction + optional self-consistency). |

### 5.1 State & actions
- **State `s`** = prompt + an ordered list of reasoning **steps** (a step = a CoT chunk
  delimited by a stop sequence / `"\nStep k:"` / newline policy). A node is a prefix.
- **Expansion:** sample `m` (default 3–4) candidate next-steps from the policy LLM at
  temperature, conditioned on the prefix. Each candidate = one child. Shared prefix is
  byte-stable to court transparent server-side prefix caching (§3).
- **Terminal:** node emits a final answer (stop token / answer regex) or hits `max_depth`.

### 5.2 Selection — PUCT
```
a* = argmax_a  Q(s,a) + c_puct · P(s,a) · sqrt(N(s)) / (1 + N(s,a))
```
`Q` = backed-up PRM value, `P` = policy prior (uniform if logprobs unavailable),
`c_puct` tunes exploration. Identical in spirit to AlphaZero selection.

### 5.3 Evaluation (the value signal)
- **Non-terminal:** `V(s) =` PRM step-score of the newest step (or running PRM score of
  the trajectory). **This is where we beat optillm** — a real, swappable value model
  instead of LLM-as-judge.
- **Terminal:** blend PRM final-score with an outcome check.

### 5.4 Backup
Propagate the leaf value up the visited path; update `N(s,a)` and `Q(s,a)` by running
mean (AlphaZero-style; `max` available as a config for sharper greedy behavior).

### 5.5 Output
Best terminal trajectory by visit count / backed-up value, **or** PRM-weighted vote
across terminal leaves — which marries MCTS with v0.1's confidence-weighted voting.

### 5.6 PRM plug-in interface (the ecosystem seed)
A single abstract contract; multiple implementations:
```
class RewardModel(Protocol):
    def score_steps(self, prompt: str, steps: list[str]) -> list[float]: ...   # step-level
    def score_final(self, prompt: str, solution: str) -> float: ...            # outcome-level
```
- **ThinkPRM adapter** (generative): runs a verification CoT, parses per-step labels.
- **Qwen2.5-Math-PRM adapter** (discriminative): reads the `<extra_0>` step-token logit.
- **LLM-as-judge adapter** (fallback, no extra model): parity floor with optillm.
Scoring is **batched** for throughput; the PRM may run on the same GPU (1.5B) or a
separate process/endpoint.

---

## 6. Scope lock — v0.1 vs the launch milestone (they differ, deliberately)

| | **v0.1 — "the plumbing"** | **Launch milestone (~6mo)** |
|---|---|---|
| Proxy | OpenAI-compatible passthrough proxy | same + streaming for multi-step |
| Techniques | BoN + confidence-weighted vote | + **deep MCTS** |
| Budget | **Compute-optimal budget router** (difficulty probe + Lagrangian allocation) + black-box early-stop | + ZIP-RC white-box early-stop on local backends |
| PRM | LLM-as-judge fallback only | **Pluggable PRM** (ThinkPRM, Qwen-Math-PRM) as MCTS value |
| Streaming | passthrough only | **partial-result streaming during search** |
| KV branching | OUT (transparent server caching only) | explicit branch-reuse on self-hosted vLLM/SGLang |
| Eval harness | MATH-500 runner, accuracy + token accounting | + the adaptive-vs-fixed cost-frontier chart |
| **Broadcast?** | **NO** ("optillm-lite") | **YES** — this is what gets announced |

**Rule:** v0.1 ships to prove plumbing + the budget router's difficulty estimator. The
public announcement waits for MCTS+PRM+streaming + the killer chart.

---

## 7. Validation plan (north star) — numeric success criteria

**Setup (single GPU):** policy = **Llama-3-8B-Instruct** (non-reasoning baseline) **and a
native reasoning policy** (e.g. `DeepSeek-R1-Distill-Qwen-7B` or a Qwen3-thinking model);
PRM = **`launch/ThinkPRM-1.5B`** (policy + 1.5B PRM co-resident on one 24–48GB GPU; PRM
quantizable / offloadable if tight). Benchmark = **MATH-500**. Own harness (standalone —
no sibling dependency).

**Curves to produce:**
1. **Accuracy monotonicity:** `1-shot < BoN-8 < MCTS+PRM` on MATH-500 accuracy.
2. **The killer chart (cost-frontier):** x = mean tokens/prompt, y = accuracy. Plot
   fixed BoN-{1,4,8,16} and the **adaptive-budget** curve (sweeping `λ`).
3. **The reasoning-model cost cut (today's proof):** on a native reasoning policy, plot
   default-effort token cost vs the adaptive-budget curve at matched accuracy — the
   headline is **tokens saved on over-thought trivial prompts**, not accuracy added.

**Numeric success (targets to *measure*, not claims):**
- **Primary:** adaptive budget **matches BoN-16 accuracy within ±0.5pp at ≤40% of BoN-16's
  mean token cost.** (The headline "same accuracy, ~60% fewer tokens.")
- **Reasoning-model target:** on a native reasoning policy, adaptive budget **holds
  accuracy within ±0.5pp while cutting ≥40% of default-effort thinking tokens.**
- **Secondary:** MCTS+PRM beats BoN-8 by **≥3pp** at equal or lower token cost.
- **Sanity:** PRM-guided selection beats majority vote at fixed N (isolates PRM value).
- **Repro:** one command, one GPU, < a few hours; seeds fixed; tokens counted from usage.

All numbers above are **targets**, to be replaced with measured values once the harness runs.

---

## 8. Leapfrog watch — what kills the wedge, and the mitigation

| Threat | Likelihood | Mitigation |
|---|---|---|
| **optillm adds a pluggable PRM interface.** | Medium | Ship first; make our PRM the *MCTS value signal* (deep integration), not a bolt-on scorer. Own the PRM-adapter ecosystem + a clean `RewardModel` contract. |
| **optillm ships real deep MCTS.** | Medium | Our MCTS is differentiated *by the PRM value model + budget-aware search*, not depth alone. Lead with the cost-frontier story, which needs the budget router they lack. |
| **optillm adds per-prompt compute budgeting.** | Low-Med | This is our hardest IP (the Lagrangian frontier + calibrated estimator). Stay ahead with the published cost-frontier chart and a tuned policy. |
| **vLLM/SGLang ship first-class search/PRM serving.** | Medium | We sit *above* the server (any OpenAI endpoint). If they add server-side search, we adopt it as a fast backend and keep the orchestration/budget/eval layer + multi-model search. |
| **Native reasoning models self-route well enough** (Qwen3-style hybrid thinking decides its own effort). | Medium | Own the *cross-model* + *domain-PRM* + *auditable-trace* story. Our value is a transparent, tunable, model-agnostic controller you can inspect — not an effort guess the model makes internally. |
| **A frontier lab open-sources a turnkey TTC layer.** | Low | Standalone harness + honest benchmarks + PRM ecosystem = defensible niche; integrate rather than compete on raw model quality. |

**Standing posture:** assume optillm moves. Keep the wedge on the *combination*
(budget-routing + real PRM value + deep MCTS + streaming) and the *reproducible chart*,
not any single feature.

---

## 9. Broadcast draft (for the launch milestone — NOT v0.1)

> Draft only. Numbers are placeholders until the harness produces them. Re-verify all
> paper IDs before posting.

**HN title:**
`Show HN: overthink — compute-optimal test-time scaling for any OpenAI-compatible model`

**X/Twitter thread (skeleton):**
1. Hook — *"I spent years building AlphaZero-style MCTS + self-play RL for game AI. I
   pointed the same search at LLM reasoning. `pip install overthink` decides how hard
   your model should think on each prompt — and proves it on the token bill."*
2. The problem — models reason natively now, but think at a fixed high/`xhigh` effort on
   *every* prompt; the knobs are manual and nobody wants to hand "how hard to think" to a
   black box. Papers solve compute-optimal allocation, but no pluggable tool does it well.
3. The idea — policy LLM = move priors, **PRM = the value network**, PUCT search over
   reasoning steps. Same AlphaZero loop, learned value instead of game rollout.
4. The differentiator — **per-prompt budget routing**: spend compute where it pays, with
   a decision you can see and tune (not a black box).
5. **The chart** — adaptive budget matches BoN-16 accuracy at ~40% of the tokens on
   MATH-500 with Llama-3-8B; on a reasoning policy it cuts 40–60% of default-effort
   thinking tokens at matched accuracy. [accuracy-vs-cost curve]
6. Pluggable PRMs (ThinkPRM, Qwen-Math-PRM), streaming, single-GPU repro. Links.

**The visual:** the §7 cost-frontier chart — fixed BoN curve vs the adaptive curve
sitting up-and-to-the-left. One image carries the launch.

---

## Open questions for human review (Phase 0 → Phase 1 gate)
1. Confirm `overthink` (vs registering PyPI placeholder now) — and run live TESS/domain check.
2. Approve the **KV-branching = OUT for v0.1** decision (§3).
3. Approve the **Lagrangian budget-allocation** framing as the core IP (§4.2).
4. Approve v0.1 scope (§6) — explicitly *not* broadcast.
5. Greenlight Phase 1 (v0.1 plumbing) — or request design changes first.
