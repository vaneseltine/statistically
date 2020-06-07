from pathlib import Path

import pytest

from statistically import statistically as st

TEST_DIR = Path(__file__).parent
EXAMPLES = list(TEST_DIR.glob("examples/*"))

print(EXAMPLES)


class TestExamples:
    @pytest.mark.parametrize("path", EXAMPLES)
    def t_initiation_does_not_break(self, path):
        assert st.Log(path)
