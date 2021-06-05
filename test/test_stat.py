from typing import Any

import pytest

from statistically.stat import AmbiguousValue as AmbV
from statistically.stat import Label, N, P, Stat


class TestGeneric:
    def t_name(self):
        t = Stat(2, name="Coef", core_format=int)
        assert repr(t) == "Coef(2)"


class TestLabel:
    def t_core(self):
        l = Label("SBE")
        assert str(l) == "SBE"
        assert l.name == "Label"
        assert repr(l) == "Label('SBE')"


class TestN:
    def t_core(self):
        raw = "4"
        x = N(raw)
        assert str(x) == "4"
        assert x.name == "n"
        assert x.value is 4
        assert x is not 4
        assert repr(x) == "n(4)"


class TestP:
    def t_core(self):
        val = 0.40952424
        p = P(val)
        assert str(p) == ".410"
        assert float(p) == val
        assert p.name == "P"
        assert repr(p) == "P(0.40952424)"

    @pytest.mark.parametrize(
        "raw, as_float, as_str",
        [
            (0, 0, ".000"),
            (0.5, 0.5, ".500"),
            ("0.5", 0.5, ".500"),
        ],
    )
    def t_basics(self, raw: AmbV, as_float: float, as_str: str):
        p = P(raw)
        assert str(p) == as_str
        assert float(p) == as_float

    @pytest.mark.parametrize(
        "raw",
        [-1, 1.1, "bob", str],
    )
    def t_invalid_values(self, raw: Any):
        with pytest.raises(ValueError):
            P(raw)

    @pytest.mark.parametrize(
        "one, two, boo",
        [
            (0.1, ".10", 0.3),
            (".10", ".100", 1),
            (".2", ".20", 0.22),
            (".3", ".300", ".33"),
            (0.9, ".9", 0),
        ],
    )
    def t_equality(self, one: AmbV, two: AmbV, boo: AmbV):
        assert P(one) == P(two)
        assert P(one) != P(boo)
        assert P(two) != P(boo)
