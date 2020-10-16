import sys
from pathlib import Path

import pytest

from statistically.lexer import LineLexer, LineToken, TableRow

EXAMPLE_DIR = Path(__file__).parent / "examples"


class TestLineLexerBasics:
    def t_lex_keeps_all_lines(self):
        l = LineLexer.from_path(EXAMPLE_DIR / "multiple" / "full_log.txt")
        assert len(l) == len(l.text)


class TestTableRow:
    @staticmethod
    @pytest.mark.parametrize(
        "line",
        [
            "    Variable |        Obs        Mean    Std. Dev.       Min        Max",
            "   Group |     Obs        Mean    Std. Err.   Std. Dev.   [95% Conf. Interval]",
            "               two_n_pubs |      Coef.   Std. Err.      z    P>|z|     [95% Conf. Interval]",
            "                  |Standardized differences          Variance ratio",
            "                  |        Raw     Matched           Raw    Matched",
        ],
    )
    def t_good(line):
        assert LineToken.find(line) == TableRow
        assert LineLexer.lex(line).__class__ == TableRow

    @staticmethod
    @pytest.mark.parametrize(
        "line",
        [
            "                          Raw     Matched           Raw    Matched",
            " Pr(T < t) = 1.0000         Pr(|T| > |t|) = 0.0000          Pr(T > t) = 0.0000",
        ],
    )
    def t_bad(line):
        assert LineToken.find(line) != TableRow
        assert LineLexer.lex(line).__class__ != TableRow


if __name__ == "__main__" and sys.argv[1:]:
    lexed = LineLexer.from_path(" ".join(sys.argv[1:]))
    print(*lexed.lines.items(), sep="\n")
