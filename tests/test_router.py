"""Unit tests for vote + DifficultyRouter using a scripted mock client (no network)."""
import pytest

from paretothink.bon import run_bon, vote
from paretothink.client import Completion
from paretothink.router import DifficultyRouter


class MockClient:
    """Returns scripted (text, output_tokens) pairs, cycling through the list."""

    def __init__(self, scripted: list[tuple[str, int]]):
        self.scripted = scripted
        self.calls = 0

    def complete(self, prompt, max_tokens=512, temperature=0.7):
        text, out = self.scripted[self.calls % len(self.scripted)]
        self.calls += 1
        return Completion(text, 10, out)


def boxed(x):
    return f"reasoning... \\boxed{{{x}}}"


class TestVote:
    def test_unanimous(self):
        r = vote([boxed(42)] * 5)
        assert r.answer == "42" and r.confidence == 1.0 and r.n_clusters == 1

    def test_split(self):
        r = vote([boxed(1), boxed(1), boxed(1), boxed(2), boxed(2)])
        assert r.answer == "1" and r.confidence == pytest.approx(0.6) and r.n_clusters == 2

    def test_equivalence_clustering(self):
        # 1/2 and 0.5 are equivalent -> one cluster, full confidence
        r = vote([boxed("\\frac{1}{2}"), boxed("0.5"), boxed("0.5")])
        assert r.confidence == 1.0 and r.n_clusters == 1

    def test_unparseable_counts_against_consensus(self):
        r = vote([boxed(3), boxed(3), boxed(3), boxed(3), "I am not sure"])
        assert r.answer == "3" and r.confidence == pytest.approx(0.8) and r.n_valid == 4

    def test_all_unparseable(self):
        r = vote(["nope", "nada"])
        assert r.answer is None and r.confidence == 0.0


class TestRouter:
    def test_easy_stops_at_R0(self):
        client = MockClient([(boxed(42), 5)])  # always agrees
        rr = DifficultyRouter(client, k0=5, tau_stop=0.80, bon_n=16).answer("q")
        assert rr.rung == "R0"
        assert rr.samples_used == 5 and rr.confidence == 1.0
        assert rr.difficulty == 0.0 and rr.output_tokens == 25
        assert client.calls == 5  # no escalation

    def test_hard_escalates_to_R1(self):
        # five distinct answers -> consensus 0.2 -> escalate
        client = MockClient([(boxed(i), 5) for i in range(1, 6)])
        rr = DifficultyRouter(client, k0=5, tau_stop=0.80, bon_n=16).answer("q")
        assert rr.rung == "R1"
        assert rr.samples_used == 16 and client.calls == 16
        assert rr.output_tokens == 80  # 16 * 5
        assert rr.difficulty == pytest.approx(0.8)  # 1 - 0.2 probe consensus

    def test_k0_must_not_exceed_bon_n(self):
        with pytest.raises(ValueError):
            DifficultyRouter(MockClient([(boxed(1), 1)]), k0=8, bon_n=4)

    def test_run_bon_token_accounting(self):
        client = MockClient([(boxed(7), 3)])
        result, out_tokens, comps = run_bon(client, "q", n=4)
        assert result.answer == "7" and out_tokens == 12 and len(comps) == 4
