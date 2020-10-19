import sys
from pathlib import Path

import pytest

from statistically.lexer import LineLexer, LineToken, TableRow, Logistic

EXAMPLE_LOGS = Path(__file__).parent / "example_logs"


class TestLineLexerBasics:
    def t_lex_keeps_all_lines(self):
        l = LineLexer((EXAMPLE_LOGS / "full_log.txt").read_text())
        assert len(l) == len(l.text)


class TestTableRow:
    @staticmethod
    @pytest.mark.parametrize(
        "line",
        [
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
            "    Variable |        Obs        Mean    Std. Dev.       Min        Max",
            "                          Raw     Matched           Raw    Matched",
            " Pr(T < t) = 1.0000         Pr(|T| > |t|) = 0.0000          Pr(T > t) = 0.0000",
        ],
    )
    def t_bad(line):
        assert LineToken.find(line) != TableRow
        assert LineLexer.lex(line).__class__ != TableRow


class TestLogistic:
    @staticmethod
    @pytest.mark.parametrize(
        "line",
        [
            "Logistic regression                             Number of obs     =     60,262",
            "Logistic regression                             Number of obs     =         62",
            "Logistic regression                             Number of obs     =     62",
        ],
    )
    def t_good(line):
        assert LineToken.find(line) == Logistic
        assert LineLexer.lex(line).__class__ == Logistic

    @staticmethod
    @pytest.mark.parametrize(
        "line",
        [
            "                          Raw     Matched           Raw    Matched",
            " Pr(T < t) = 1.0000         Pr(|T| > |t|) = 0.0000          Pr(T > t) = 0.0000",
        ],
    )
    def t_bad(line):
        assert LineToken.find(line) != Logistic
        assert LineLexer.lex(line).__class__ != Logistic


if __name__ == "__main__" and sys.argv[1:]:
    lexed = LineLexer(Path(" ".join(sys.argv[1:])).read_text())
    print(*lexed, sep="\n")
