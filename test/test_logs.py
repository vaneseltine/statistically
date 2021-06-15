# type: ignore
import pytest

from statistically import statistically as st

from . import STATA_OUTPUT


@pytest.mark.parametrize("log", [*STATA_OUTPUT.glob("**/*.txt")])
def test_logs_do_not_just_break(log):
    assert st.TextLog(log)


@pytest.mark.xfail(reason="Need to improve long variable handling")
def test_estat_vif_with_interaction():
    """
    The lines
        spam_and_egg#|
        tomato       |
    Are not being picked up as a row... not clear why.
        Is tomato being counted as a subcat of nonexistent group? Hmm.

    And once they are it'll be a whole thing to figure out the group name
    """
    loglines = (STATA_OUTPUT / "adhoc" / "estat_vif_prob.txt").read_text().splitlines()
    t = st.Table(loglines)
    df = t.to_df()
    assert "tomato" in str(df)
    # assert 12 <= len(t.to_df()) <= 16


@pytest.mark.xfail(reason="Need to improve group var handling in margins")
def test_nested_variables():
    """
    The way Stata subtly positions headings on i.vars
    Makes it difficult to capture the difference when multiple things are represented
    """
    loglines = (STATA_OUTPUT / "basic" / "margins4.txt").read_text().splitlines()
    df = st.Table(loglines).to_df()
    assert "group = 1" in str(df)


def test_summarize_does_not_cut_off():
    """
    We were dropping the final character on the right end.
    """
    loglines = (STATA_OUTPUT / "basic" / "summarize.txt").read_text().splitlines()
    df = st.Table(loglines).to_df()
    assert "Max" in str(df)
