from pathlib import Path

import pytest

from statistically.stat import Label, N, P, Stat


class TestP:
    def t_core(self):
        val = 0.40952424
        p = P(val)
        assert str(p) == ".410"
        assert float(p) == val
        assert p.name == "p"
        assert repr(p) == "P(0.40952424)"

    @pytest.mark.parametrize(
        "raw, as_float, as_str",
        [
            (0, 0, ".000"),
            (0.5, 0.5, ".500"),
            ("0.5", 0.5, ".500"),
        ],
    )
    def t_basics(self, raw, as_float, as_str):
        p = P(raw)
        assert str(p) == as_str
        assert float(p) == as_float

    @pytest.mark.parametrize(
        "raw",
        [-1, 1.1, "bob"],
    )
    def t_baddies(self, raw):
        with pytest.raises(ValueError):
            P(raw)

    @pytest.mark.parametrize(
        "one, two",
        [
            (0.1, ".10"),
            (".10", ".100"),
            (".2", ".20"),
            (".3", ".300"),
            (0.9, ".9"),
        ],
    )
    def t_equals(self, one, two):
        assert P(one) == P(two)


class TestLabel:
    def t_core(self):
        val = "SBE"
        l = Label(val)
        assert str(l) == "SBE"
        assert l.name == "label"
        assert repr(l) == "Label('SBE')"


class TestN:
    def t_core(self):
        val = "4"
        x = N(val)
        assert str(x) == "4"
        assert x.name == "n"
        assert x.value is 4
        assert repr(x) == "N(4)"
