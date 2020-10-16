from pathlib import Path

import pytest

from statistically.lexer import LineLexer

EXAMPLE_DIR = Path(__file__).parent / "examples"


class TestLineLexerBasics:
    # l = LineLexer.from_path(EXAMPLE_DIR / "tebalance.txt")
    l = LineLexer.from_path(EXAMPLE_DIR / "multiple" / "full_log.txt")

    def t_lex(self):
        assert len(self.l) == len(self.l.text)


colnames = [
    "    Variable |        Obs        Mean    Std. Dev.       Min        Max",
    "   Group |     Obs        Mean    Std. Err.   Std. Dev.   [95% Conf. Interval]",
    "               two_n_pubs |      Coef.   Std. Err.      z    P>|z|     [95% Conf. Interval]",
    "                  |Standardized differences          Variance ratio",
    "                  |        Raw     Matched           Raw    Matched",
]

l = LineLexer.from_path(EXAMPLE_DIR / "nbreg.txt")
print(*l.lines.items(), sep="\n")
