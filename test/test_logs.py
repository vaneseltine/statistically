# type: ignore
import pytest

from statistically import statistically as st

from . import STATA_OUTPUT


@pytest.mark.parametrize("log", [*STATA_OUTPUT.glob("**/*.txt")])
def test_logs_do_not_just_break(log):
    assert st.TextLog(log)
