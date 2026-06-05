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
**Phase 1a — BUILDING the proof-slice** (first accuracy-vs-cost frontier on MATH-500 via Bedrock).
Both premises validated by the 2026-06-03 Bedrock probe; spec locked in `DESIGN.md` §10.

## Last updated
2026-06-03 · by: Phase 1a build session

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
**Phase 1a code COMPLETE + unit-tested (28 pass); the live run is BLOCKED on AWS Midway auth.**
Proof-slice built per `DESIGN.md` §10, committed in slices:

1. ✅ DESIGN §10 spec + STATUS/DECISIONS logged.
2. ✅ Scaffold + pyproject + venv; SymPy answer-checker + 19 tests. (`56d759b`)
3. ✅ Bedrock Converse client wrapper. (`55cc875`)
4. ✅ BoN weighted vote + DifficultyRouter (k0=5, τ_stop=0.80, λ ladder) + 9 tests. (`bb71031`)
5. ✅ Eval harness + MATH-500 loader + CLI. (`f65f77d`) — validated end-to-end on `--limit 5`.
6. ✅ macOS threaded-boto3 segfault fixed (OBJC_DISABLE_INITIALIZE_FORK_SAFETY). (`bf15d27`)
7. ⛔ **BLOCKED — run on Bedrock (`--limit 50`) → first cost-frontier chart.** Needs creds.
8. ⬜ yolo-reviewer pass; address findings; push.

**UNBLOCK THE RUN (human, one step):** the sandbox cred tool is gone post-resume and isengardcli
needs Midway. Run `mwinit` in a terminal (authenticates Midway). I created `~/.aws/config` with a
`[profile kadmon]` (isengardcli credential_process, acct 137164215426, us-east-1). After `mwinit`,
either I run `AWS_PROFILE=kadmon ./.venv/bin/python -m paretothink.cli --limit 50`, or you do.

**Early signal (from `--limit 5` sanity run):** all 5 MATH problems escalated to R1 (consensus
< 0.80) — MATH-500 is much harder for Llama-3-8B than the trivial arithmetic in the 06-03 probe,
so τ_stop=0.80 may rarely early-stop. The 50-run will show the real easy/hard split; if few clear
τ_stop, expect to **tune τ_stop down / add adaptive variants** to trace a frontier that beats fixed BoN.

Side tasks (human): register PyPI `paretothink==0.0.1`; live USPTO TESS + registrar domain check; rename GitHub repo `overthink`→`paretothink` + `git remote set-url`.

## Blocked / needs human decision
- Approve the 5 open questions in `DESIGN.md` §"Open questions" before Phase 1.
- Second verification pass on unverified paper IDs (`2604.14853`, `2602.01070`, `2505.16122`)
  **before** any public broadcast.

## Guardrails (don't regress)
- Standalone-first: no sibling/project dependency, ever.
- v0.1 is NOT broadcastable on its own — the launch is the MCTS+PRM+budget chart.
- Don't let plumbing detail-work erode the MCTS+PRM north star.
