from pathlib import Path

import pytest

from statistically import statistically as st

EXAMPLE_DIR = Path(__file__).parent / "examples"


def get_example(name):
    if name == "single":
        return list(EXAMPLE_DIR.glob("*.*"))
    if name == "full":
        return list((EXAMPLE_DIR / "full").glob("*.*"))
    if name == "all":
        return get_example("single") + get_example("full")
    return next(EXAMPLE_DIR.glob(name + "*"))


class TestExamples:
    @pytest.mark.parametrize("path", get_example("all"))
    def t_from_path_does_not_break(self, path):
        log = st.Log.from_path(path)
        assert len(log) > 0

    @pytest.mark.parametrize("path", get_example("single"))
    def t_single_examples_singular(self, path):
        log = st.Log.from_path(path)
        assert len(log.outputs) == 1


class TestMargins:
    path = get_example("margins")
    log = st.Log.from_path(path)
    output = log.outputs[0]

    def t_thing_loads_probably(self):
        assert len(self.log.outputs) == 1

    def t_n(self):
        assert self.output.n == 2395
