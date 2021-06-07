# type: ignore
# import pytest

from statistically import statistically as st

from . import TEST_FULL


def test_api():
    assert st.TextLog(TEST_FULL / "artificial.txt")
