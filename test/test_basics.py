from statistically import statistically as st
from statistically.log import TextLog
import pytest


def test_does_not_immediately_explode():
    assert st


@pytest.mark.parametrize(
    "line, result",
    [
        ("  4 = 5  ", ["4", "5"]),
        ("  4 = 5", ["4", "5"]),
        ("4 = 5  ", ["4", "5"]),
        ("4=5", ["4", "5"]),
        ("x  4 = 5  ", ["4", "5"]),
    ],
)
def test_params(line, result):
    assert TextLog.get_param(line) == result
