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


@pytest.mark.xfail(
    reason="Harder to deal with misarranged lists...", raises=AssertionError
)
@pytest.mark.parametrize(
    "inlist, outlist",
    [
        (
            [
                "egg spam bacon".split(),
                "egg bacon spam".split(),
            ],
            "egg spam bacon".split(),
        ),
    ],
)
def test_accept_first_sort_of_missorted_variables(inlist, outlist):
    assert st.sort_variable_lists(inlist) == outlist


@pytest.mark.xfail(
    reason="incompatible sort, with a before/after gf and gu", raises=RuntimeError
)
@pytest.mark.parametrize(
    "inlist, outset",
    [
        (
            [
                "sr sb i N".split(),
                "sr sb gf gu a u2 i9 iE i N".split(),
                "sr sb gf gu a u2 i9 iE i N".split(),
                "sr sb a sc.ar sc.ab gf gu u2 i9 iE i N".split(),
                "sr sb gf gu zrf zru zbf zbu a u2 i9 iE i N".split(),
                "sr sb gf gu zrf zru zbf zbu a u2 i9 iE i N".split(),
            ],
            "sr sb gf gu zrf zru zbf zbu a u2 i9 iE i N",
        ),
        (
            [
                "egg spam bacon".split(),
                "egg bacon spam sausage".split(),
            ],
            "egg spam bacon sausage".split(),
        ),
    ],
)
def test_wrongly_duplicating(inlist, outset):
    assert set(st.sort_variable_lists(inlist)) == set(outset)


@pytest.mark.parametrize(
    "inlist",
    [
        ["a b c d".split(), "a b c d e".split(), "a b c d e d".split()],
        ["a b c d".split(), "a b c d e".split(), "a b c d e a".split()],
        ["a a".split()],
    ],
)
def test_raise_on_duplicates(inlist):
    with pytest.raises(ValueError):
        st.sort_variable_lists(inlist)
