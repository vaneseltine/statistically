import re
from pathlib import Path
from typing import List, Tuple, Union

Lines = List[str]

blank_line = re.compile(r"^$")

LINE_HORIZONTAL = "h"
LINE_HAS_COLUMN = "c"
LINE_UNUSED = " "


class TextLog:

    column_finder = re.compile(r" [|+]+(\s|$)")
    horizontal_line = re.compile(r"(?<=)[-+]+(?=\W)")

    def __init__(self, path: Union[Path, str]) -> None:
        self.lines = self.make_lines(path)
        # print(self.raw)
        self.table_boundaries = self.find_tables(self.lines)
        print(f'("{Path(path).name}", {self.table_boundaries}),')
        # parameters = self.find_parameters()

    @staticmethod
    def make_lines(path: Union[Path, str]) -> Lines:
        return Path(path).read_text().splitlines()

    @classmethod
    def find_tables(cls, lines: Lines) -> List[Tuple[int, int]]:
        # debug
        # for i, line in enumerate(lines):
        #     print(f"{i:>3} {line}")

        tables_string = "".join(cls.find_line(l) for l in lines)
        print(tables_string)
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

    def find_parameters(self) -> None:
        """
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

        equals_finder = re.compile(r"  =  ")
        """
        pass  # pylint: disable=unnecessary-pass
