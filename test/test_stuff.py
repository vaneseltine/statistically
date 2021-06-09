# type: ignore
import pytest

from statistically import statistically as st


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
    assert st.TextLog.find_line(line) == code


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
            [slice(2, 8)],
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
            [slice(0, 6)],
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
            [slice(0, 6)],
        ),
    ],
)
def test_boundaries(lines, boundaries):
    assert st.TextLog.find_tables(lines) == boundaries


def test_does_not_immediately_explode():
    assert st


@pytest.mark.parametrize(
    "line, result",
    [
        (["  x = 5  "], {"x": "5"}),
        (["  x = 5"], {"x": "5"}),
        (["x = 5  "], {"x": "5"}),
        (["x  x = 5  "], {"x": "5"}),
        (["x  x = 5  x"], {"x": "5"}),
        (["  x = 5  x"], {"x": "5"}),
    ],
)
def test_single_equations(line, result):
    assert dict(st.EquationBuilder(line)) == result


@pytest.mark.parametrize(
    "line, result",
    [
        (["two = 2    five = 5  x"], {"two": "2", "five": "5"}),
    ],
)
def test_multiple_equations(line, result):
    assert dict(st.EquationBuilder(line)) == result


@pytest.mark.parametrize(
    "full_list, slices",
    (
        [[1, 2, 3, 8, 9], [slice(1, 4), slice(8, 10)]],
        [[1, 2, 3], [slice(1, 4)]],
        [[3, 4, 9, 10], [slice(3, 5), slice(9, 11)]],
    ),
)
def test_make_slices(full_list, slices):
    assert [*st.make_slices(full_list)] == slices


@pytest.mark.parametrize(
    "inlist, outlist",
    [
        (
            ["egg spam bacon".split()],
            "egg spam bacon".split(),
        ),
        (
            [
                "egg spam bacon".split(),
                "egg spam bacon".split(),
            ],
            "egg spam bacon".split(),
        ),
        (
            [
                "eg sp ba".split(),
                "eg sp ha mu to ba".split(),
            ],
            "eg sp ha mu to ba".split(),
        ),
        (
            [
                "eg sp ba".split(),
                "eg sp ha".split(),
            ],
            "eg sp ba ha".split(),
        ),
        (
            [
                ["eg"],
                "eg sp ba".split(),
            ],
            "eg sp ba".split(),
        ),
        (
            [
                "eg sp ba".split(),
                "eg sp ha mu to ba".split(),
                "eg sp pa zu to ba".split(),
            ],
            "eg sp ha mu pa zu to ba".split(),
        ),
        (
            [
                "egg spam bacon".split(),
                "egg spam ham mushroom toast bacon".split(),
                "egg spam pancakes zucchini toast bacon".split(),
            ],
            "egg spam ham mushroom pancakes zucchini toast bacon".split(),
        ),
        (
            [
                "egg spam bacon".split(),
                "egg spam ham mushroom toast bacon".split(),
                "egg spam pancakes zucchini toast bacon".split(),
                "egg spam pancakes zucchini toast bacon cheese".split(),
            ],
            "egg spam ham mushroom pancakes zucchini toast bacon cheese".split(),
        ),
    ],
)
def test_sort_variables(inlist, outlist):
    assert st.sort_variable_lists(inlist) == outlist
