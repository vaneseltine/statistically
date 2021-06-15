# type: ignore
import pytest

from statistically import statistically as st

from . import STATA_OUTPUT


def get_table(filename, n=0):
    text = STATA_OUTPUT / "basic" / f"{filename}.txt"
    tl = st.TextLog(text)
    return list(tl.cmd_dict.values())[0][n]


@pytest.mark.parametrize(
    "n, row, col",
    [
        (0, 3, 4),
        (1, 3, 7),
    ],
)
def test_regress_shape(n, row, col):
    df = get_table("regress", n)
    assert df.shape == (row, col)


@pytest.mark.parametrize(
    "n, names",
    [
        (
            0,
            [
                "Source",
                "SS",
                "df",
                "MS",
            ],
        ),
        (
            1,
            [
                "mpg",
                "Coef.",
                "Std. Err.",
                "t",
                "P>|t|",
                "[95% Conf.",
                "Interval]",
            ],
        ),
    ],
)
def test_regress_columns(n, names):
    df = get_table("regress", n)
    assert list(df.columns) == names


@pytest.mark.parametrize(
    "n, proper",
    [
        (
            0,
            {
                "Source": {0: "Model", 1: "Residual", 2: "Total"},
                "SS": {0: " 1619.2877", 1: "824.171761", 2: "2443.45946"},
                "df": {0: " 2", 1: "71", 2: "73"},
                "MS": {0: "809.643849", 1: " 11.608053", 2: "33.4720474"},
            },
        ),
        (
            1,
            {
                "mpg": {0: "weight", 1: "foreign", 2: "_cons"},
                "Coef.": {0: "-.0065879", 1: "-1.650029", 2: "  41.6797"},
                "Std. Err.": {0: ".0006371 ", 1: "1.075994 ", 2: "2.165547 "},
                "t": {0: "-10.34", 1: " -1.53", 2: " 19.25"},
                "P>|t|": {0: "0.000", 1: "0.130", 2: "0.000"},
                "[95% Conf.": {0: "-.0078583  ", 1: "  -3.7955  ", 2: " 37.36172  "},
                "Interval]": {0: "-.0053175", 1: " .4954422", 2: " 45.99768"},
            },
        ),
    ],
)
def test_regress_dict(n, proper):
    df = get_table("regress", n)
    assert df.to_dict() == proper
