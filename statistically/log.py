import re
from itertools import groupby
from operator import itemgetter
from pathlib import Path
from typing import List, Sequence, Union

from .stat import N, P, Stat

Lines = List[str]

line_horiz = re.compile(r"(?<=)[-+]+(?=\W)")
line_only = re.compile(r"^[-+]+$")

LINE_HORIZONTAL = "h"
LINE_HAS_COLUMN = "c"
LINE_UNUSED = " "


class TextLog:

    column_finder = re.compile(r" [|+]+(\s|$)")

    def __init__(self, path: Union[Path, str]) -> None:
        self.lines = self.make_lines(path)
        self.table_slices = self.find_tables(self.lines)
        # print(self.table_boundaries)
        self.tables = [Table(self.lines[ts]) for ts in self.table_slices]
        # parameters = self.find_parameters()

    @staticmethod
    def make_lines(path: Union[Path, str]) -> Lines:
        return Path(path).read_text().splitlines()

    @classmethod
    def find_tables(cls, lines: Lines) -> List[slice]:
        tables_string = "".join(cls.find_line(l) for l in lines)
        # print(tables_string)
        table_quantifier = re.compile(
            r"""(?x)  # allow these comments
            (?<=\b)   # boundary, including start of line
            \w+       # table identifiers
            (?=\b)    # boundary, including end of file
            """
        )
        table_groups = table_quantifier.finditer(tables_string)
        return [slice(*x.span()) for x in table_groups]

    @classmethod
    def find_line(cls, line: str) -> str:
        if line_horiz.search(line):
            return LINE_HORIZONTAL
        if cls.column_finder.search(line):
            return LINE_HAS_COLUMN
        return LINE_UNUSED


class Column:

    known_types = {
        "obs": N,
        "p": P,
        "P>|t|": P,
        "P>|z|": P,
    }
    common_names = {
        "[95% Conf.": "min95",
        "Coef.": "coef",
        "Delta-method Std. Err.": "se",
        "freq.": "freq",
        "Interval]": "max95",
        "std. dev.": "sd",
        "Std. Err.": "se",
    }

    def __init__(self, lines: Lines, header_num: int) -> None:
        self.header = " ".join(lines[:header_num])
        # print("header =", self.header)
        known_type = self.known_types.get(self.header)
        if known_type:
            self.type = known_type  # TODO: really need a factory method here
            self.type_name = known_type.default_name
        else:
            self.type = Stat
            self.type_name = self.common_names.get(self.header, self.header)
        # print("type     =", self.type)
        # print("type_name=", self.type_name)
        self.data = lines[header_num:]
        # print("rest")
        # print(self.data)

    def __str__(self) -> str:
        return self.type_name

    def __repr__(self) -> str:
        return self.type_name


class Row:
    def __init__(self, values: Sequence[str], columns: Sequence[Column]) -> None:
        self.dict = dict(zip(columns, values))

    def __str__(self) -> str:
        return str(self.dict)


class Table:
    def __init__(self, lines: Lines) -> None:
        print("START OF BUILD TABLE")
        # print(*lines, sep="\n")
        self.raw = lines
        self.cleaned = self.clean_table_lines(lines)
        for i, line in enumerate(self.cleaned):
            print(f"  {i:>2} {line}")
        self.header_num = self.find_header(self.cleaned)
        self.text_columns = self.parse_columns(self.cleaned)
        self.columns = [Column(c, self.header_num) for c in self.text_columns]
        key_rows = [*zip(*self.text_columns)][self.header_num :]
        self.rows = [Row(r, self.columns) for r in key_rows]
        for i, row in enumerate(self.rows):
            print(i, row)
        print("END OF BUILD TABLE")

    @classmethod
    def clean_table_lines(cls, lines: Lines) -> Lines:
        range_slice = cls.determine_horizontal_range(lines)
        cut_lines = [l[range_slice] for l in lines]

        for row in (0, -1):
            if line_only.match(cut_lines[row]):
                cut_lines.pop(row)

        return cut_lines

    @classmethod
    def determine_horizontal_range(cls, lines: Lines) -> slice:
        line_matches = [line_horiz.search(l) for l in lines if line_horiz.search(l)]
        table_min = min(l.span()[0] for l in line_matches)
        table_max = max(l.span()[-1] for l in line_matches) + 1
        return slice(table_min, table_max)

    @classmethod
    def find_header(cls, lines: Lines) -> int:
        for i, line in enumerate(lines):
            if line_horiz.match(line):
                return i
        return 1

    @classmethod
    def parse_columns(cls, lines: Lines) -> List[List[str]]:
        content_lines = [l for l in lines if re.search(r"\w", l)]
        good_cols = cls.find_useful_columns(content_lines)
        col_slices = [*make_slices(good_cols)]
        groups_of_columns = [
            [l[cs].strip() for l in content_lines] for cs in col_slices
        ]
        return groups_of_columns

    @classmethod
    def find_useful_columns(cls, lines: Lines):
        full_length = max(len(l) for l in lines)
        lines = [f"{l:<{full_length}}" for l in lines]
        rotated_lines = enumerate(zip(*lines))
        return [i for i, col in rotated_lines if not cls.is_column_sep(col)]

    @staticmethod
    def is_column_sep(seq: Sequence[str]):
        return all(x in (" |+") for x in seq)

    def find_parameters(self) -> None:
        r"""
        Pick up additional parameters grouped by equals such as output:

            ```
            Probit regression                               Number of obs     =         74
                                                            LR chi2(2)        =      36.38
                                                            Prob > chi2       =     0.0000
            Log likelihood = -26.844189                     Pseudo R2         =     0.4039
            ```

        Or those with colons such as :

            ```
            Predictive margins                              Number of obs     =      3,000
            Model VCE    : OLS

            Expression   : Linear prediction, predict()
            ```

        Hmm something like...?

            equals_finder = re.compile(r"  +(\w +)  +=  +[-+.0-9]")

        no... probably divide up with simple " = "
        then capture nearest total boundaries of `\s\s\w` and `\w\b`
        """
        pass  # pylint: disable=unnecessary-pass


def make_slices(ids: List[int]) -> List[slice]:
    """
    Turn a list with consecutive integers, e.g.
        [1, 2, 3, 8, 9]
    Into slices
        [slice(1, 4), slice(8, 10)]
    """

    for _, grp in groupby(enumerate(ids), key=lambda x: x[0] - x[1]):
        consecutives = [*map(itemgetter(1), grp)]
        yield slice(consecutives[0], consecutives[-1] + 1)
    # return column_groups
