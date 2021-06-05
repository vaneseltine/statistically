import collections
from os import stat
import re
from pathlib import Path
from typing import List, Sequence, Tuple, Union

Lines = List[str]

blank_line = re.compile(r"^$")

LINE_HORIZONTAL = "h"
LINE_HAS_COLUMN = "c"
LINE_UNUSED = " "


class TextLog:

    column_finder = re.compile(r" [|+]+(\s|$)")
    horizontal_line = re.compile(r"(?<=)[-+]+(?=\W)")
    only_a_line = re.compile(r"^[-+]+$")

    def __init__(self, path: Union[Path, str]) -> None:
        self.lines = self.make_lines(path)
        self.table_boundaries = self.find_tables(self.lines)
        # print(self.table_boundaries)
        self.tables = [
            self.build_table(self.lines[start:end])
            for start, end in self.table_boundaries
        ]
        # parameters = self.find_parameters()

    @staticmethod
    def make_lines(path: Union[Path, str]) -> Lines:
        return Path(path).read_text().splitlines()

    @classmethod
    def find_tables(cls, lines: Lines) -> List[Tuple[int, int]]:
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
        return [x.span() for x in table_groups]

    @classmethod
    def find_line(cls, line: str) -> str:
        if cls.horizontal_line.search(line):
            return LINE_HORIZONTAL
        if cls.column_finder.search(line):
            return LINE_HAS_COLUMN
        return LINE_UNUSED

    @classmethod
    def build_table(cls, lines: Lines):
        print("START OF BUILD TABLE")
        # print(*lines, sep="\n")
        cleaned = cls.clean_table_lines(lines)
        for i, line in enumerate(cleaned):
            print(f"  {i:>2} {line}")
        columns = cls.make_columns(cleaned)
        print("END OF BUILD TABLE")

    @classmethod
    def clean_table_lines(cls, lines: Lines) -> Lines:
        start, end = cls.determine_horizontal_range(lines)
        cut_lines = [l[start : end + 1] for l in lines]

        for row in (0, -1):
            if cls.only_a_line.match(cut_lines[row]):
                cut_lines.pop(row)

        return cut_lines

    @classmethod
    def determine_horizontal_range(cls, lines: Lines) -> Tuple[int, int]:
        line_matches = [
            cls.horizontal_line.search(l)
            for l in lines
            if cls.horizontal_line.search(l)
        ]
        table_min = min(l.span()[0] for l in line_matches)
        table_max = max(l.span()[-1] for l in line_matches)
        return (table_min, table_max)

    @classmethod
    def make_columns(cls, lines: Lines):
        any_content = re.compile(r"\w")
        lines_with_content = [l for l in lines if any_content.search(l)]
        print(*(f"{x}        " for x in range(9)))
        print("0123456789" * 9)
        print(*lines_with_content, sep="\n")
        blank_cols = cls.find_blank_columns(lines_with_content)
        column_groups = cls.group_columns(blank_cols)
        print("groups")
        print(column_groups)
        for cg in column_groups:
            for l in lines_with_content:
                print(l[cg[0] : cg[1]])

    @classmethod
    def find_blank_columns(cls, lines: Lines):

        full_length = max(len(l) for l in lines)

        lines = [f"{l:<{full_length}}" for l in lines]
        rotated_lines = enumerate(zip(*lines))
        return [i for i, col in rotated_lines if cls.is_column_sep(col)]

    @staticmethod
    def is_column_sep(seq: Sequence[str]):
        return all(x in (" |+") for x in seq)

    @classmethod
    def group_columns(cls, blanks: Sequence[int]):
        print("blank")
        print(blanks)
        column_groups: List[Tuple[int, int]] = []
        if blanks[0] != 0:
            column_groups.append((0, blanks.pop(0)))
        return column_groups

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
