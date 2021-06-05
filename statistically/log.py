import re
from itertools import groupby
from operator import itemgetter
from pathlib import Path
from typing import List, Sequence, Union

import pandas as pd

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
        self.main_tables = self.get_tables(self.lines)
        self.stats = self.get_more_stats(self.lines)
        self.tables = self.main_tables + self.stats

    def get_tables(self, lines: Lines):
        table_slices = self.find_tables(lines)
        # print(self.table_boundaries)
        return [Table(lines[ts]) for ts in table_slices]

    def get_more_stats(self, lines: Lines):
        lines_with_equals = [l for l in lines if re.search(r"=", l)]
        for line in lines_with_equals:
            param = self.get_param(line)
        exit()

    @classmethod
    def get_param(cls, line) -> List[str]:
        print(line)
        squasher = re.compile(r"\s+=\s+")
        squashed = squasher.sub("=", line)
        final = squashed
        return [l.strip() for l in final.split("=")]

    def report(self):
        for i, line in enumerate(self.lines):
            print(f"{i:>4} {line}")

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


class Table:
    def __init__(self, lines: Lines) -> None:
        # print(*lines, sep="\n")
        self.raw = lines
        self.cleaned = self.clean_table_lines(lines)
        # for i, line in enumerate(self.cleaned):
        #     print(f"  {i:>2} {line}")
        self.text_columns = self.parse_columns(self.cleaned)
        header_count = self.find_header(self.cleaned)
        column_names = self.create_column_names(self.text_columns, header_count)
        # self.columns = [Column(c, self.header_num) for c in self.text_columns]
        # print(self.columns)
        key_rows = [*zip(*self.text_columns)][header_count:]
        # print(key_rows)
        self.df = pd.DataFrame(key_rows, columns=column_names)
        # set_index("colname", verify_integrity=True)

    def to_df(self) -> pd.DataFrame:
        return self.df

    @staticmethod
    def create_column_names(text_columns: List[List[str]], header_count: int):
        header_cols = [c[:header_count] for c in text_columns]
        column_names = [" ".join(c).strip() for c in header_cols]
        return column_names

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
