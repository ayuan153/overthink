"""Compute-optimal difficulty router (proof-slice v0).

Estimates per-prompt difficulty from a cheap k0-sample **consensus probe**, then walks the
escalation ladder R0 -> R1, stopping early when consensus clears ``tau_stop``. Probe samples
are *reused* toward the BoN budget (no wasted calls), so easy prompts cost ~k0 samples and
hard prompts cost ~bon_n. Sweeping ``tau_stop``/``bon_n`` (the token-price knob) traces the
accuracy-vs-cost frontier. See DESIGN.md §10.4.
"""
from __future__ import annotations

from dataclasses import dataclass

from .bon import vote


@dataclass
class RouterResult:
    answer: str | None
    confidence: float
    difficulty: float  # 1 - probe consensus
    output_tokens: int  # total spent across all rungs
    samples_used: int
    rung: str  # "R0" (stopped at probe) or "R1" (escalated to BoN)


class DifficultyRouter:
    def __init__(
        self,
        client,
        k0: int = 5,
        tau_stop: float = 0.80,
        bon_n: int = 16,
        max_tokens: int = 512,
        temperature: float = 0.7,
    ):
        if k0 > bon_n:
            raise ValueError("k0 must be <= bon_n")
        self.client = client
        self.k0 = k0
        self.tau_stop = tau_stop
        self.bon_n = bon_n
        self.max_tokens = max_tokens
        self.temperature = temperature

    def _sample(self, prompt: str):
        return self.client.complete(prompt, self.max_tokens, self.temperature)

    def answer(self, prompt: str) -> RouterResult:
        # R0 — cheap difficulty probe.
        comps = [self._sample(prompt) for _ in range(self.k0)]
        v = vote([c.text for c in comps])
        difficulty = 1.0 - v.confidence
        if v.confidence >= self.tau_stop:
            out = sum(c.output_tokens for c in comps)
            return RouterResult(v.answer, v.confidence, difficulty, out, len(comps), "R0")

        # R1 — escalate to BoN, reusing the probe samples.
        for _ in range(self.bon_n - self.k0):
            comps.append(self._sample(prompt))
        v2 = vote([c.text for c in comps])
        out = sum(c.output_tokens for c in comps)
        return RouterResult(v2.answer, v2.confidence, difficulty, out, len(comps), "R1")
