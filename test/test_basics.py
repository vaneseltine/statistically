import pytest

from statistically import statistically as st
from statistically.log import EquationBuilder


def test_does_not_immediately_explode():
    assert st


@pytest.mark.parametrize(
    "line, result",
    [
        (["  x = 5  "], {"x": "5"}),
        (["  x = 5"], {"x": "5"}),
        (["x = 5  "], {"x": "5"}),
        (["x  x = 5  "], {"x": "5"}),
        (["x  x = 5  x"], {"x": "5"}),
        (["  x = 5  x"], {"x": "5"}),
    ],
)
def test_single_equations(line, result):
    assert dict(EquationBuilder(line)) == result


@pytest.mark.parametrize(
    "line, result",
    [
        (["two = 2    five = 5  x"], {"two": "2", "five": "5"}),
    ],
)
def test_multiple_equations(line, result):
    assert dict(EquationBuilder(line)) == result
