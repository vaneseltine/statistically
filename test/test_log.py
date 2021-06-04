import pytest

from statistically.log import TextLog

from . import TEST_RESULTS_DIRECTORY


@pytest.mark.parametrize(
    "line, code",
    [
        ("--------------                ", "h"),
        ("           --------------     spam", "h"),
        ("--------------", "h"),
        ("-----+--------", "h"),
        ("-----|--------", "h"),
        (" | ", "c"),
        (" -3 ", " "),
    ],
)
def test_find_line(line, code):
    assert TextLog.find_line(line) == code


@pytest.mark.parametrize(
    "logfile, boundaries",
    [
        ("logit.txt", [(19, 26)]),
        ("margins1.txt", [(12, 20)]),
        ("margins4.txt", [(12, 25)]),
        ("margins8.txt", [(12, 24)]),
        ("nbreg_offset.txt", [(12, 26)]),
        ("nbreg.txt", [(31, 44)]),
        ("probit.txt", [(19, 26)]),
        ("regress.txt", [(7, 13), (14, 21)]),
        ("summarize.txt", [(7, 23)]),
        ("table_contents.txt", [(7, 18)]),
        ("table.txt", [(7, 18)]),
    ],
)
def test_log_boundaries(logfile, boundaries):
    path = TEST_RESULTS_DIRECTORY / logfile
    log = TextLog(path)
    assert log.table_boundaries == boundaries


@pytest.mark.parametrize(
    "lines, boundaries",
    [
        (
            [
                "a",
                "",
                "-----",
                "   |",
                "   |  ",
                "-----",
                "   |  ",
                "-----",
            ],
            [(2, 8)],
        ),
        (
            [
                "-----",
                "   |",
                "   |  ",
                "-----",
                "   |  ",
                "-----",
                "3",
                "a",
            ],
            [(0, 6)],
        ),
        (
            [
                "-----",
                "   |",
                "   |  ",
                "-----",
                "   |  ",
                "-----",
            ],
            [(0, 6)],
        ),
    ],
)
def test_boundaries(lines, boundaries):
    assert TextLog.find_tables(lines) == boundaries
