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

    def t_stats(self):
        assert self.output.results["n"] == self.output.n == 2395

    def t_table_length(self):
        assert len(self.output.table) == 2

    @pytest.mark.parametrize(
        "row, cell, value",
        [
            (0, "value", 0),
            (0, "margin", 1.926662,),
            (0, "std_err", 0.0332418,),
            (0, "z", 57.96,),
            (0, "p_z", 0.0,),
            (0, "ci_lo", 1.861509,),
            (0, "ci_hi", 1.991815,),
            (1, "value", 1),
            (1, "margin", 2.045452,),
            (1, "std_err", 0.0635479,),
            (1, "z", 32.19,),
            (1, "p_z", 0.0,),
            (1, "ci_lo", 1.9209,),
            (1, "ci_hi", 2.170003,),
        ],
    )
    def t_table_cells(self, row, cell, value):
        assert self.output.table[row][cell] == value
