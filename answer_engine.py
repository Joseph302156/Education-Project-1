import re
from sympy import SympifyError, solve, sympify
from sympy.parsing.sympy_parser import parse_expr

# Optional: parse_latex can fail on some LaTeX; we'll try parse_expr for plain math


def _extract_equation(text: str) -> str | None:
    """Try to get 'expr = number' or 'expr = expr' from text."""
    # Strip leading "Solve for x:", "Find x:", etc.
    cleaned = re.sub(r"^(?:Solve for \w+:\s*|Find \w+:\s*|Solve\s*)+", "", text, flags=re.I).strip()
    m = re.search(r"([^=]+)=([^=]+)", cleaned)
    if m:
        return m.group(0).strip()
    return cleaned or text.strip()


def get_answer(problem_text: str) -> dict:
    """
    Attempt to solve or simplify using SymPy. Returns dict with answer_text, steps (optional), error.
    For word problems we return a placeholder; production would use an LLM.
    """
    eq_str = _extract_equation(problem_text)
    if not eq_str or len(problem_text.split()) > 40:
        return {
            "answer_text": "This looks like a word problem. For production, plug in your LLM here for step-by-step answers.",
            "steps": [],
            "solved": False,
            "error": None,
        }

    try:
        if "=" in eq_str:
            left, right = eq_str.split("=", 1)
            try:
                lhs = parse_expr(left.strip())
                rhs = parse_expr(right.strip())
            except (SympifyError, Exception):
                return {
                    "answer_text": "Could not parse equation. Try using * for multiplication and ** for power.",
                    "steps": [],
                    "solved": False,
                    "error": "parse",
                }
            sol = solve(lhs - rhs)
            if sol:
                answer_text = ", ".join(str(s) for s in sol)
                return {
                    "answer_text": answer_text,
                    "steps": [f"Solve: {eq_str}", f"Solution: {answer_text}"],
                    "solved": True,
                    "error": None,
                }
            return {
                "answer_text": "No solution found (or equation not in one variable).",
                "steps": [],
                "solved": False,
                "error": None,
            }
        else:
            expr = parse_expr(eq_str)
            simplified = expr.simplify()
            return {
                "answer_text": str(simplified),
                "steps": [f"Simplify: {eq_str}", f"Result: {simplified}"],
                "solved": True,
                "error": None,
            }
    except Exception as e:
        return {
            "answer_text": "Could not compute answer with built-in solver. Use an LLM endpoint for open-ended problems.",
            "steps": [],
            "solved": False,
            "error": str(e),
        }
