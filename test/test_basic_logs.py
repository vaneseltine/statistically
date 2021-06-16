# type: ignore
import pytest


@pytest.mark.parametrize(
    "n, row, col",
    [
        (0, 3, 4),
        (1, 3, 7),
    ],
)
def test_regress_shape(regress_dfs, n, row, col):
    assert regress_dfs[n].shape == (row, col)


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
def test_regress_columns(regress_dfs, n, names):
    cols = regress_dfs[n].columns
    assert list(cols) == names


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
def test_regress_dict(regress_dfs, n, proper):
    assert regress_dfs[n].to_dict() == proper


def test_margins1_columns(margins1_df):
    expected = [
        "col0",
        "Margin",
        "Delta-method   Std. Err.",
        "t",
        "P>|t|",
        "[95% Conf.",
        "Interval]",
    ]
    observed = list(margins1_df.columns)
    assert expected == observed


def test_margins1_dict(margins1_df):
    expected = {
        "col0": {0: "sex = male", 1: "sex = female"},
        "Margin": {0: "60.56034", 1: "78.88236"},
        "Delta-method   Std. Err.": {0: "  .5781782  ", 1: "  .5772578  "},
        "t": {0: "104.74", 1: "136.65"},
        "P>|t|": {0: "0.000", 1: "0.000"},
        "[95% Conf.": {0: "59.42668  ", 1: " 77.7505  "},
        "Interval]": {0: " 61.69401", 1: " 80.01422"},
    }
    observed = margins1_df.to_dict()
    assert expected == observed


def test_nbreg_columns(nbreg_df):
    expected = [
        "deaths",
        "Coef.",
        "Std. Err.",
        "z",
        "P>|z|",
        "[95% Conf.",
        "Interval]",
    ]
    observed = list(nbreg_df.columns)
    assert expected == observed


def test_nbreg_dict(nbreg_df):
    expected = {
        "deaths": {
            0: "cohort = 1960-1967",
            1: "cohort = 1968-1976",
            2: "_cons",
            3: "/lnalpha",
            4: "alpha",
        },
        "Coef.": {
            0: " .0591305",
            1: "-.0538792",
            2: " 4.435906",
            3: "-1.207379",
            4: "   .29898",
        },
        "Std. Err.": {
            0: ".2978419 ",
            1: ".2981621 ",
            2: ".2107213 ",
            3: ".3108622 ",
            4: ".0929416 ",
        },
        "z": {0: " 0.20", 1: "-0.18", 2: "21.05", 3: "     ", 4: "     "},
        "P>|z|": {0: "0.843", 1: "0.857", 2: "0.000", 3: "     ", 4: "     "},
        "[95% Conf.": {
            0: "-.5246289  ",
            1: "-.6382662  ",
            2: "   4.0229  ",
            3: "-1.816657  ",
            4: " .1625683  ",
        },
        "Interval]": {
            0: "   .64289",
            1: " .5305077",
            2: " 4.848912",
            3: "-.5980999",
            4: " .5498555",
        },
    }
    observed = nbreg_df.to_dict()
    assert expected == observed


def test_nbreg_stats(nbreg_stats):
    expected = {
        "Number of obs": "21",
        "LR chi2(2)": "0.14",
        "Dispersion": "mean",
        "Prob > chi2": "0.9307",
        "Log likelihood": "-108.48841",
        "Pseudo R2": "0.0007",
        "LR test of alpha=0: chibar2(01)": "434.62",
        "Prob >= chibar2": "0.000",
    }
    assert expected == nbreg_stats


def test_summarize_columns(summarize_df):
    expected = ["Variable", "Obs", "Mean", "Std. Dev.", "Min", "Max"]
    assert expected == list(summarize_df.columns)


def test_summarize_dict(summarize_df):
    expected = {
        "Variable": {
            0: "make",
            1: "price",
            2: "mpg",
            3: "rep78",
            4: "headroom",
            5: "trunk",
            6: "weight",
            7: "length",
            8: "turn",
            9: "displacement",
            10: "gear_ratio",
            11: "foreign",
        },
        "Obs": {
            0: "  0",
            1: " 74",
            2: " 74",
            3: " 69",
            4: " 74",
            5: " 74",
            6: " 74",
            7: " 74",
            8: " 74",
            9: " 74",
            10: " 74",
            11: " 74",
        },
        "Mean": {
            0: "",
            1: "6165.257",
            2: " 21.2973",
            3: "3.405797",
            4: "2.993243",
            5: "13.75676",
            6: "3019.459",
            7: "187.9324",
            8: "39.64865",
            9: "197.2973",
            10: "3.014865",
            11: ".2972973",
        },
        "Std. Dev.": {
            0: "",
            1: "2949.496 ",
            2: "5.785503 ",
            3: ".9899323 ",
            4: ".8459948 ",
            5: "4.277404 ",
            6: "777.1936 ",
            7: "22.26634 ",
            8: "4.399354 ",
            9: "91.83722 ",
            10: ".4562871 ",
            11: ".4601885 ",
        },
        "Min": {
            0: "",
            1: "3291",
            2: "  12",
            3: "   1",
            4: " 1.5",
            5: "   5",
            6: "1760",
            7: " 142",
            8: "  31",
            9: "  79",
            10: "2.19",
            11: "   0",
        },
        "Max": {
            0: "",
            1: "15906",
            2: "   41",
            3: "    5",
            4: "    5",
            5: "   23",
            6: " 4840",
            7: "  233",
            8: "   51",
            9: "  425",
            10: " 3.89",
            11: "    1",
        },
    }
    assert expected == summarize_df.to_dict()
