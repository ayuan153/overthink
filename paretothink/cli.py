"""CLI: run fixed-BoN and adaptive strategies on MATH-500 -> accuracy-vs-cost frontier.

Example:
    paretothink-eval --limit 50 --strategies 1shot,bon4,bon8,bon16,adaptive
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from .client import BedrockClient
from .data import load_math500
from .eval import adaptive_fn, evaluate, fixed_bon_fn

_FIXED = {"1shot": 1, "bon4": 4, "bon8": 8, "bon16": 16}


def _strategy_fn(name: str, a):
    if name in _FIXED:
        return fixed_bon_fn(_FIXED[name], a.max_tokens, a.temperature)
    if name == "adaptive":
        return adaptive_fn(a.k0, a.tau_stop, a.bon_n, a.max_tokens, a.temperature)
    raise SystemExit(f"unknown strategy: {name}")


def main() -> None:
    ap = argparse.ArgumentParser(prog="paretothink-eval")
    ap.add_argument("--model", default="meta.llama3-8b-instruct-v1:0")
    ap.add_argument("--region", default="us-east-1")
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--strategies", default="1shot,bon4,bon8,bon16,adaptive")
    ap.add_argument("--k0", type=int, default=5)
    ap.add_argument("--tau-stop", type=float, default=0.80, dest="tau_stop")
    ap.add_argument("--bon-n", type=int, default=16, dest="bon_n")
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--max-tokens", type=int, default=512, dest="max_tokens")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    client = BedrockClient(a.model, a.region)
    problems = load_math500(a.limit)
    print(f"model={a.model} problems={len(problems)} strategies={a.strategies}\n")

    rows = []
    print(f"{'strategy':10} {'accuracy':>8} {'mean_out_tok':>12} {'correct/n':>10}  meta")
    for name in [s.strip() for s in a.strategies.split(",") if s.strip()]:
        res = evaluate(client, problems, name, _strategy_fn(name, a), a.workers)
        rows.append(res)
        print(
            f"{res.name:10} {res.accuracy:>8.3f} {res.mean_output_tokens:>12.0f} "
            f"{f'{res.n_correct}/{res.n}':>10}  {res.meta}"
        )

    out = Path(a.out or f"eval_results/frontier_{int(time.time())}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "model": a.model,
        "limit": a.limit,
        "params": {"k0": a.k0, "tau_stop": a.tau_stop, "bon_n": a.bon_n,
                   "temperature": a.temperature, "max_tokens": a.max_tokens},
        "results": [r.__dict__ for r in rows],
    }
    out.write_text(json.dumps(payload, indent=2))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
