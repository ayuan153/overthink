"""Best-of-N sampling + confidence-weighted majority vote.

Votes are clustered by mathematical equivalence (so ``1/2`` and ``0.5`` count together),
and confidence = winning-cluster weight / total samples (unparseable samples count against
consensus). Weights are uniform in v0; a PRM supplies real weights at the launch milestone.
"""
from __future__ import annotations

from dataclasses import dataclass

from .checker import extract_answer, is_equivalent


@dataclass
class VoteResult:
    answer: str | None
    confidence: float  # winning-cluster weight / total sample weight
    n_clusters: int
    n_valid: int


def vote(texts: list[str], weights: list[float] | None = None) -> VoteResult:
    """Confidence-weighted vote over completion texts, clustered by equivalence."""
    weights = weights if weights is not None else [1.0] * len(texts)
    total = sum(weights)
    clusters: list[list] = []  # [rep_answer, weight, count]
    valid = 0
    for text, w in zip(texts, weights):
        a = extract_answer(text)
        if a is None:
            continue
        valid += 1
        for cl in clusters:
            if is_equivalent(a, cl[0]):
                cl[1] += w
                cl[2] += 1
                break
        else:
            clusters.append([a, w, 1])
    if not clusters:
        return VoteResult(None, 0.0, 0, 0)
    best = max(clusters, key=lambda c: c[1])
    confidence = best[1] / total if total else 0.0
    return VoteResult(best[0], confidence, len(clusters), valid)


def run_bon(client, prompt: str, n: int, max_tokens: int = 512, temperature: float = 0.7):
    """Sample N completions, return (VoteResult, total_output_tokens, completions)."""
    comps = [client.complete(prompt, max_tokens, temperature) for _ in range(n)]
    result = vote([c.text for c in comps])
    out_tokens = sum(c.output_tokens for c in comps)
    return result, out_tokens, comps
