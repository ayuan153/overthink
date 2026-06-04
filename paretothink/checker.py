"""Deterministic answer extraction + math-equivalence checking for MATH-style problems.

No LLM-as-judge: extract the final answer (prefer ``\\boxed{}``), normalize common LaTeX,
and compare via SymPy symbolic equivalence with a numeric fallback. Keeps the accuracy
numbers reproducible (a DESIGN principle).
"""
from __future__ import annotations

import re

from sympy import simplify
from sympy.parsing.sympy_parser import (
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

_TRANSFORMS = standard_transformations + (implicit_multiplication_application,)


def _extract_brace(text: str, start: int) -> str | None:
    """Return the content of the first brace group at/after ``start`` (brace-matched)."""
    i = text.find("{", start)
    if i == -1:
        return None
    depth = 0
    for j in range(i, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[i + 1 : j]
    return None


def extract_answer(text: str) -> str | None:
    """Pull the final answer from a model completion.

    Priority: last ``\\boxed{...}`` -> 'answer is/: X' phrase -> last number.
    """
    if not text:
        return None
    idx = text.rfind("\\boxed")
    if idx != -1:
        sub = _extract_brace(text, idx + len("\\boxed"))
        if sub is not None:
            return sub.strip()
    m = re.findall(r"(?:final answer|answer)\s*(?:is|:|=)?\s*\$?([^\n.$]+)", text, re.I)
    if m:
        return m[-1].strip()
    nums = re.findall(r"-?\d+(?:\.\d+)?", text)
    return nums[-1] if nums else None


def _latex_to_expr(s: str) -> str:
    """Best-effort LaTeX -> SymPy-parseable string (numeric/fraction/sqrt/pi cases)."""
    s = s.strip().strip("$").strip()
    s = s.replace("\\left", "").replace("\\right", "")
    s = s.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")
    for tok in ("\\!", "\\,", "\\;", "\\ ", "~", "\\%", "%", "^{\\circ}", "\\circ", "$"):
        s = s.replace(tok, "")
    s = s.replace("{,}", "").replace(",", "")  # number grouping (tuples handled upstream)
    frac = re.compile(r"\\frac\{([^{}]*)\}\{([^{}]*)\}")
    while frac.search(s):
        s = frac.sub(r"((\1)/(\2))", s)
    s = re.sub(r"\\sqrt\{([^{}]*)\}", r"sqrt(\1)", s)
    s = s.replace("\\sqrt", "sqrt")
    s = s.replace("\\pi", "pi").replace("\\cdot", "*").replace("\\times", "*")
    s = s.replace("^", "**")
    s = s.replace("{", "(").replace("}", ")")
    return s


def _safe_parse(s: str):
    try:
        return parse_expr(s, transformations=_TRANSFORMS, evaluate=True)
    except Exception:
        return None


def _split_tuple(s: str) -> list[str] | None:
    """Split a *bracketed* top-level comma tuple like '(3, \\frac{\\pi}{2})' into elements.

    Requires surrounding parens/brackets so bare numbers with thousands separators
    (e.g. '2,600') are NOT treated as tuples.
    """
    s = s.strip()
    if not (s[:1] in "([" and s[-1:] in ")]"):
        return None
    inner = s[1:-1]
    if "," not in inner:
        return None
    parts, depth, buf = [], 0, ""
    for ch in inner:
        if ch in "({[":
            depth += 1
        elif ch in ")}]":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(buf)
            buf = ""
        else:
            buf += ch
    parts.append(buf)
    return [p.strip() for p in parts]


def is_equivalent(pred: str | None, gold: str) -> bool:
    """True if ``pred`` is mathematically equivalent to ``gold``."""
    if pred is None:
        return False
    p, g = pred.strip(), gold.strip()
    if p == g:
        return True

    # Tuple / ordered-pair comparison (before comma-stripping in normalization).
    pt, gt = _split_tuple(p), _split_tuple(g)
    if pt is not None and gt is not None:
        return len(pt) == len(gt) and all(is_equivalent(a, b) for a, b in zip(pt, gt))
    if (pt is None) != (gt is None):
        return False

    pe, ge = _safe_parse(_latex_to_expr(p)), _safe_parse(_latex_to_expr(g))
    if pe is not None and ge is not None:
        try:
            if simplify(pe - ge) == 0:
                return True
        except Exception:
            pass
        try:
            if abs(float(pe) - float(ge)) < 1e-6:
                return True
        except Exception:
            pass
    return _latex_to_expr(p).replace(" ", "") == _latex_to_expr(g).replace(" ", "")
