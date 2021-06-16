from pathlib import Path

import pytest

from statistically import statistically as st

STATA_OUTPUT = (Path(__file__).parent / "stata").absolute()


def get_log_dfs(filename, subdir="basic"):
    text = STATA_OUTPUT / subdir / f"{filename}.txt"
    tl = st.TextLog(text)
    return list(tl.cmd_dict.values())[0]


@pytest.fixture(scope="session")
def regress_dfs():
    return get_log_dfs("regress")


@pytest.fixture(scope="session")
def nbreg_df():
    return get_log_dfs("nbreg")[0]


@pytest.fixture(scope="session")
def nbreg_stats():
    return get_log_dfs("nbreg")[1]


@pytest.fixture(scope="session")
def margins1_df():
    return get_log_dfs("margins1")[0]


@pytest.fixture(scope="session")
def summarize_df():
    return get_log_dfs("summarize")[0]
