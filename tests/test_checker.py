"""Unit tests for the deterministic answer checker (no network)."""
from paretothink.checker import extract_answer, is_equivalent


class TestExtract:
    def test_boxed(self):
        assert extract_answer("blah \\boxed{42} done") == "42"

    def test_boxed_nested(self):
        assert extract_answer("so \\boxed{\\frac{1}{2}}") == "\\frac{1}{2}"

    def test_last_boxed_wins(self):
        assert extract_answer("\\boxed{1} ... \\boxed{7}") == "7"

    def test_answer_phrase(self):
        assert extract_answer("The final answer is 686.") == "686"

    def test_answer_phrase_decimal(self):
        # decimal must survive the fallback (regression: used to truncate to "3")
        assert extract_answer("The final answer is 3.50") == "3.50"

    def test_answer_phrase_sentence(self):
        assert extract_answer("The answer is 686. It follows that we are done.") == "686"

    def test_last_number_fallback(self):
        assert extract_answer("I think it is 3 then maybe 56") == "56"

    def test_empty(self):
        assert extract_answer("") is None
        assert extract_answer("no digits here") is None


class TestEquivalence:
    def test_int(self):
        assert is_equivalent("56", "56")

    def test_int_wrong(self):
        assert not is_equivalent("7", "360")

    def test_fraction_latex_vs_decimal(self):
        assert is_equivalent("\\frac{1}{2}", "0.5")

    def test_dfrac(self):
        assert is_equivalent("\\dfrac{3}{6}", "\\frac{1}{2}")

    def test_sqrt(self):
        assert is_equivalent("2\\sqrt{3}", "\\sqrt{12}")

    def test_pi(self):
        assert is_equivalent("\\frac{\\pi}{2}", "pi/2")

    def test_thousands_separator(self):
        assert is_equivalent("2,600", "2600")

    def test_negative_fraction(self):
        assert is_equivalent("-\\frac{1}{4}", "-0.25")

    def test_tuple(self):
        assert is_equivalent("(3, \\frac{\\pi}{2})", "(3, pi/2)")

    def test_tuple_order_matters(self):
        assert not is_equivalent("(1, 2)", "(2, 1)")

    def test_tuple_vs_scalar(self):
        assert not is_equivalent("(1, 2)", "3")

    def test_none_pred(self):
        assert not is_equivalent(None, "5")

    def test_expression(self):
        assert is_equivalent("x**2 + 1", "1 + x^2")
