from pathlib import Path

import pytest

from statistically.lexer import Lexer

EXAMPLE_DIR = Path(__file__).parent / "examples"


class TestLexerBasics:
    l = Lexer.from_path(EXAMPLE_DIR / "multiple" / "full_log.txt")

    def t_lex(self):
        assert len(self.l) > 0


colnames = [
    "    Variable |        Obs        Mean    Std. Dev.       Min        Max",
    "   Group |     Obs        Mean    Std. Err.   Std. Dev.   [95% Conf. Interval]",
    "               two_n_pubs |      Coef.   Std. Err.      z    P>|z|     [95% Conf. Interval]",
    "                  |Standardized differences          Variance ratio",
    "                  |        Raw     Matched           Raw    Matched",
]
