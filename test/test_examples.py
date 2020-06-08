from pathlib import Path

import pytest

from statistically import statistically as st

TEST_DIR = Path(__file__).parent
EXAMPLE_DIR = TEST_DIR / "examples"
EXAMPLES = [*EXAMPLE_DIR.glob("*")]
assert len(EXAMPLES) > 0


class TestExamples:
    @pytest.mark.parametrize("path", EXAMPLES)
    def t_from_path_does_not_break(self, path):
        log = st.Log.from_path(path)
        assert len(log) > 0


class TestMargins:
    text = (EXAMPLE_DIR / "margins.txt").read_text()
    log = st.Log(text=text)

    def t_basic_stat(self):
        assert len(self.log.outputs) == 1
