# type: ignore
import pytest

from statistically import statistically as st

from . import STATA_OUTPUT


@pytest.mark.parametrize("log", [*STATA_OUTPUT.glob("**/*.txt")])
def test_logs_do_not_just_break(log):
    assert st.TextLog(log)


@pytest.mark.xfail(reason="badly written test")
def test_estat_vif_with_interaction():
    """
    The line
        spam_and_egg#|
    Was not being picked up as a column due to regex requiring a space...
    Now only requiring space/ending after |
    """
    loglines = (STATA_OUTPUT / "adhoc" / "estat_vif_prob.txt").read_text().splitlines()
    t = st.Table(loglines)
    df = t.to_df().set_index("Variable")
    assert "tomato" in df.index
    # assert 12 <= len(t.to_df()) <= 16


@pytest.mark.xfail(reason="badly written test")
def test_nested_variables():
    """
    The way Stata subtly positions headings on i.vars
    Makes it difficult to capture the difference when multiple things are represented
    """
    loglines = (STATA_OUTPUT / "basic" / "margins4.txt").read_text().splitlines()
    t = st.Table(loglines)
    df = t.to_df()
    print(df.columns)
    assert "group = 1" in str(df)
