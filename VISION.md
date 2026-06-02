# VISION.md

> The long-term arc for `overthink`. This grounds every later decision. Changing
> anything here is a deliberate act that must be flagged to the human and logged in
> `DECISIONS.md`.

## North star

**Make any model reason *optimally* — the right amount of compute for each prompt.**
Not "run the model N times," and not "let the model decide how hard to think." Instead:
estimate each prompt's difficulty, spend search proportional to it, guide that search
with a real process reward model, and stream the result.

This matters *more* now that strong models reason natively. Today's models default to
**high / `xhigh` reasoning** and burn 10K–40K thinking tokens on every prompt — including
the trivial, search-engine-style questions users actually send. And teams **refuse to
hand the compute decision to the model as a black box**: they want more intelligence in
*how much* to think, with a decision they can see, tune, and audit. `overthink` is that
transparent, per-prompt compute controller.

The project that defines **"reasoning orchestration"** for open models.

## The one-sentence pitch

> `pip install overthink`, point it at any OpenAI-compatible endpoint, and it spends
> *just enough* compute on each prompt — AlphaZero-style search + a pluggable reward
> model on the hard ones, instant answers on the easy ones — for reasoning-model
> accuracy at a fraction of the tokens, with a compute decision you can see instead of
> a black box.

## Who hurts and why

Strong reasoning is no longer the scarce thing — open models reason natively now. The
scarce thing is **control over the compute**. Native reasoning models think at a fixed
high / `xhigh` effort on *every* prompt, wasting 10K–40K tokens on questions that needed
a sentence. The knobs providers expose (`reasoning_effort: low|med|high`) are *manual* —
they push the decision back onto the user. And nobody wants to hand "how hard should I
think?" to the model as an opaque black box on work that matters. The techniques to
decide this well exist in papers (Snell compute-optimal scaling, process reward models,
MCTS-over-LLM-calls) — but there is **no fast, pluggable tool you can `pip install` that
does them *well* and lets you see and tune the decision.** The research code is research
code; the one popular proxy does the easy 80% and stops exactly where it gets hard.

## The wedge (narrow and deliberate)

The incumbent is **`optillm`** (~4.1k★, actively developed, 20+ techniques incl. MCTS,
best-of-N, rStar). It is real competition. We do **not** try to out-feature it. We win
on the four things that are genuinely hard to bolt on, all of which are open as of the
last verification (see `DESIGN.md` for the dated audit):

1. **Compute-optimal per-prompt budget routing** — estimate difficulty, then spend
   compute proportional to it. (Snell, arXiv 2408.03314; early-stop via ZIP-RC,
   arXiv 2512.01457.) *optillm's router picks which technique, not how much compute.*
2. **Real pluggable PRMs** — step-level process reward scoring from a swappable model
   (e.g. ThinkPRM, Qwen2.5-Math-PRM). *optillm uses LLM-as-judge / regex heuristics.*
3. **Genuine deep MCTS** over LLM calls, with PRM as the value signal. *optillm's MCTS
   defaults to depth=1 — sample-and-verify, not search.*
4. **Streaming** of partial results during multi-step search. *optillm fakes it:
   computes the full answer, then chunks it.*

The differentiation is **led by budget-routing + real PRM**, with deep MCTS as the
showcase of what good search looks like when the value signal is real.

## The arc

### v0.1 — now — "the plumbing" (NOT broadcastable on its own)
OpenAI-compatible proxy + best-of-N + confidence-weighted vote + the **compute-optimal
budget router**. This is "optillm-lite." It ships first to prove the plumbing, the
proxy ergonomics, and the budget router's difficulty estimator. It is explicitly **not**
the thing we announce.

### ~6 months — THE LAUNCH MILESTONE — "reason optimally"
**Deep MCTS + pluggable PRM + streaming**, wrapped in the accuracy-vs-cost story. This
is what gets broadcast. The launch hook leans on the builder's AlphaZero / self-play RL
background: *"I built MCTS for game AI; here's the same search applied to LLM reasoning,
with a learned value model (the PRM) instead of a game-result rollout."* Budget
~6–8 weeks of focused work to a convincing launch — not 3.

### ~2 years — "the standard test-time-compute layer"
The default TTC layer for open models: a **PRM ecosystem** (plug any reward model),
**adaptive budgeting as a first-class serving feature**, **multi-model search** (route
different branches to different models). The OSS project that owns "reasoning
orchestration."

## North-star proof (the killer chart)

One chart decides whether the launch lands. On **MATH-500 with Llama-3-8B-Instruct**:

- Accuracy climbs monotonically: **1-shot → BoN-8 → MCTS+PRM.**
- The money shot: **adaptive budget matches fixed BoN-16 accuracy at ~40% of the token
  cost.** Same accuracy, ~60% fewer tokens — because easy prompts stop early and hard
  prompts get the search.

And the proof that lands in *today's* world — run the same router on a **native reasoning
model** (an R1-distill / Qwen3-thinking policy): **adaptive budget holds accuracy while
cutting 40–60% of the model's default-effort thinking tokens.** Same answers, far fewer
tokens, because the trivial prompts no longer think at `xhigh`.

If those curves are real and reproducible on a single GPU, the project earns its broadcast.

## Principles

- **Standalone-first.** `overthink` owns its eval/benchmark harness and has zero sibling
  dependency. Never couple it to another project.
- **Portfolio anchor.** Highest ceiling, highest signal. Detail-work must not erode the
  MCTS+PRM north star.
- **Honesty over hype.** Re-verify the incumbent and the literature; they move. The
  wedge must survive a few of optillm's PRs.
- **Python-first, `pip`-installable, OpenAI-compatible.** A native core for tree
  traversal is optional and only if it pays for itself.
