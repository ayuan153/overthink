"""Eval harness: run a strategy over MATH problems -> accuracy + token cost.

A *strategy* maps (client, prompt) -> (answer, output_tokens, meta). Fixed-BoN and the
adaptive router are both strategies, so the cost-frontier is just several strategies
evaluated on the same problem set (DESIGN.md §10.1).
"""
from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

from .bon import run_bon
from .checker import is_equivalent
from .router import DifficultyRouter

PROMPT = (
    "Solve the math problem. Show brief reasoning, then give the final answer "
    "in \\boxed{{}}.\n\nProblem: {q}"
)


@dataclass
class StrategyResult:
    name: str
    n: int
    n_correct: int
    accuracy: float
    total_output_tokens: int
    mean_output_tokens: float
    meta: dict = field(default_factory=dict)


def fixed_bon_fn(n: int, max_tokens: int, temperature: float):
    def fn(client, prompt):
        v, out, _ = run_bon(client, prompt, n, max_tokens, temperature)
        return v.answer, out, {}

    return fn


def adaptive_fn(k0: int, tau_stop: float, bon_n: int, max_tokens: int, temperature: float):
    def fn(client, prompt):
        rr = DifficultyRouter(client, k0, tau_stop, bon_n, max_tokens, temperature).answer(prompt)
        return rr.answer, rr.output_tokens, {"rung": rr.rung}

    return fn


def evaluate(client, problems, name, strategy_fn, max_workers: int = 6) -> StrategyResult:
    def one(p):
        answer, out, meta = strategy_fn(client, PROMPT.format(q=p.problem))
        return is_equivalent(answer, p.answer), out, meta

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        results = list(ex.map(one, problems))

    n = len(results)
    n_correct = sum(1 for correct, _, _ in results if correct)
    total = sum(out for _, out, _ in results)
    rungs = Counter(m["rung"] for _, _, m in results if "rung" in m)
    return StrategyResult(
        name=name,
        n=n,
        n_correct=n_correct,
        accuracy=n_correct / n if n else 0.0,
        total_output_tokens=total,
        mean_output_tokens=total / n if n else 0.0,
        meta=dict(rungs),
    )
