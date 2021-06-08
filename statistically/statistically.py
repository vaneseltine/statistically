"""An empty-featured Stata output scraper/parser."""
import logging
import re
import sys
from glob import glob
from itertools import groupby
from operator import itemgetter
from pathlib import Path
from typing import Dict, Generator, List, Optional, Sequence, Tuple, Union

import pandas as pd  # type: ignore

Lines = List[str]


line_horiz = re.compile(r"(?<=)[-+]+(?=\W)")
line_only = re.compile(r"^[-+]+$")

LINE_HORIZONTAL = "h"
LINE_HAS_COLUMN = "c"
LINE_UNUSED = " "

__version__ = "0.1.1"

UserInput = str


def main() -> int:

    if handle_cli_only():
        return 0
    args = sys.argv[1:]
    try:
        args.remove("--debug")
        debug = True
    except ValueError:
        debug = False
    create_logger(debug=debug)
    raw_input = input_from_args(args)
    logging.getLogger().debug(f"Raw input {raw_input!r}")
    for filename in glob(raw_input):
        print("\n", filename, "\n")
        # print(Path(filename).read_text())
        log = TextLog(filename)
        log.report()
        for cmd, items in log.cmd_dict.items():
            print(cmd)
            for item in items:
                print(item)
        # for tab in log.tables:
        #     print(tab.to_df())
        # print(log.stats)
        print("\n\n")
    return 0


def handle_cli_only() -> bool:
    args = sys.argv[1:]
    if not args or "-h" in args or "--help" in args:
        report_help()
        return True
    if "-V" in args or "--version" in args:
        report_version()
        return True
    return False


def input_from_args(args: List[str]) -> UserInput:
    """
    Just smash together all arguments from the command line.
    """
    command_line_input: UserInput = " ".join(args)
    return command_line_input


def report_help() -> None:
    """
    Report something useful, at some point.
    """
    print("Try: statistically blah.log")


def report_version() -> None:
    package = f"statistically {__version__} at {Path(__file__).parent.absolute()}"
    py_version = f"on Python {sys.version.split(' ')[0]} at {sys.executable}"
    print(f"{package}\n{py_version}")


def create_logger(debug: bool = False, log_file: Optional[str] = None) -> None:
    """

    Another option:
        sfmt="{asctime} {levelname:>7} {message}", style="{", datefmt=r"%H:%M:%S"
    """
    noisiness = logging.DEBUG if debug else logging.INFO

    formatter = logging.Formatter(
        fmt="{asctime} {name:<20} {lineno:>3}:{levelname:<7} {message}",
        style="{",
        datefmt=r"%Y%m%d-%H%M%S",
    )
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    handlers = [stream_handler]
    if log_file is not None:
        file_handler = logging.FileHandler(filename=log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    logging.basicConfig(level=logging.DEBUG, handlers=handlers)

    # new_logger = logging.getLogger(__name__)
    logging.getLogger().setLevel(noisiness)

    # if log_file:
    #     new_logger.debug(f"Logging to {log_file}")
    # return new_logger


class Command:

    command_pattern = re.compile(r"^\. ([\w]+)")

    def __init__(self, line: str, start: int, end: int) -> None:
        self.core = self.command_pattern.search(line).group(1)  # type: ignore
        self.slice = slice(start, end)
        self.line = line

    @classmethod
    def get_commands(cls, lines: Lines) -> List["Command"]:
        comm_lines = [(l, i) for i, l in enumerate(lines) if cls.is_command(l)]
        endings = [i for _, i in comm_lines[1:]] + [len(lines)]
        all_cmds = [cls(*line_info, end) for line_info, end in zip(comm_lines, endings)]
        logging.getLogger().debug(str(all_cmds))
        return all_cmds

    @classmethod
    def is_command(cls, line: str) -> bool:
        return cls.command_pattern.search(line) is not None

    def __str__(self) -> str:
        start = self.slice.start
        end = self.slice.stop - 1
        return f"{self.core}({start}-{end})"

    def __repr__(self) -> str:
        return f"<Command({self.core}, {self.slice.start})>"


class TextLog:

    column_finder = re.compile(r"[|+]+(\s|$)")

    def __init__(self, path: Union[Path, str]) -> None:
        self.lines = Path(path).read_text().splitlines()
        # add a phantom line to sync with doc line numbers
        self.lines = [""] + self.lines
        self.commands = self.get_commands(self.lines)
        self.cmd_dict: Dict[Command, List[Union[pd.DataFrame, Dict[str, str]]]] = {}
        for cmd in self.commands:
            logging.getLogger().debug(cmd)
            cmd_lines = self.lines[cmd.slice]
            cmd_stats = self.get_stats(cmd_lines)
            cmd_tables = self.get_tables(cmd_lines)
            self.cmd_dict[cmd] = [*cmd_tables, cmd_stats]
        # self.tables = self.main_tables + self.stats

    @classmethod
    def get_commands(cls, lines: Lines) -> List[Command]:
        return Command.get_commands(lines)

    @staticmethod
    def get_stats(lines: Lines) -> Dict[str, str]:
        return EquationBuilder(lines).to_dict()

    @classmethod
    def get_tables(cls, lines: Lines) -> List[pd.DataFrame]:
        table_slices = cls.find_tables(lines)
        # print(self.table_boundaries)
        return [Table(lines[ts]).to_df() for ts in table_slices]

    def report(self) -> None:
        for i, line in enumerate(self.lines):
            print(f"{i:>4} {line}")

    @classmethod
    def find_tables(cls, lines: Lines) -> List[slice]:
        tables_string = "".join(cls.find_line(l) for l in lines)
        table_quantifier = re.compile(
            r"""(?x)  # allow these comments
            (?<=\b)   # boundary, including start of line
            \w+       # table identifiers
            (?=\b)    # boundary, including end of file
            """
        )
        table_groups = table_quantifier.finditer(tables_string)
        table_slices = [slice(*x.span()) for x in table_groups if cls.long_enough(x)]
        logging.getLogger().debug(f"{table_slices}")
        return table_slices

    @classmethod
    def long_enough(cls, matched: re.Match) -> bool:  # type: ignore
        start, finish = matched.span()
        if finish - start <= 2:
            logging.getLogger().debug(f"Lines {start}-{finish} too short for table.")
            return False
        return True

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
        final_rows = self.finalize_rows(key_rows)
        self.df = pd.DataFrame(final_rows, columns=column_names)
        # set_index("colname", verify_integrity=True)

    def finalize_rows(self, rows: List[Tuple[str, ...]]):
        print(rows)
        new_rows: List[Tuple[str, ...]] = []
        label: str = ""
        for row in rows:
            var, *content = row
            # print([i, var])
            if all(val == "" for val in content):
                print("THIS IS A LABEL")
                label: str = var.strip()
                continue
            elif var[-1] == " " and var[-2] != " ":
                print("THIS IS A CATEGORY")
                new_label = f"{label} = {var.strip()}"
                new_row = (new_label, *content)
            else:
                print("NEITHER LABEL NOR CATEGORY")
                label = ""
                new_row = (var.strip(), *content)
            print(new_row)
            new_rows.append(new_row)
        return new_rows

    def to_df(self) -> pd.DataFrame:
        return self.df

    @staticmethod
    def create_column_names(
        text_columns: List[List[str]], header_count: int
    ) -> List[str]:
        header_cols = [c[:header_count] for c in text_columns]
        column_names = [
            " ".join(c).strip() or f"col{i}" for i, c in enumerate(header_cols)
        ]
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
        table_min = min(l.span()[0] for l in line_matches)  # type: ignore
        table_max = max(l.span()[-1] for l in line_matches) + 1  # type: ignore
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
        groups_of_columns = [[l[cs] for l in content_lines] for cs in col_slices]
        return groups_of_columns

    @classmethod
    def find_useful_columns(cls, lines: Lines) -> List[int]:
        full_length = max(len(l) for l in lines)
        lines = [f"{l:<{full_length}}" for l in lines]
        rotated_lines = enumerate(zip(*lines))
        return [i for i, col in rotated_lines if not cls.is_column_sep(col)]

    @staticmethod
    def is_column_sep(seq: Sequence[str]) -> bool:
        return all(x in (" |+") for x in seq)


class EquationBuilder:

    SPACER = "                      "
    EQUALS = r"!!EQUALS!!"

    exclusion = re.compile(r"^Iteration \d")
    raw_equals = re.compile(r"\s+=\s+")

    def __init__(self, lines: Lines) -> None:
        vetted_lines = self.vet_lines(lines)
        # make a giant string -- no reason to keep row by row
        joined = self.SPACER.join(vetted_lines)
        # remove space around = (sometimes it's a lot)
        tagged = "  " + self.raw_equals.sub(self.EQUALS, joined) + "  "
        # split by double spaces which "should" bracket params
        segments = [x for x in tagged.split("  ") if self.EQUALS in x]
        # separate and clean strings into list of tuples
        self.params = self.parameterize(segments)

    @classmethod
    def vet_lines(cls, lines: Lines) -> Lines:
        good_lines = [l for l in lines if cls.raw_equals.search(l)]
        no_bad_lines = [l for l in good_lines if not cls.exclusion.search(l)]
        for line in no_bad_lines:
            logging.getLogger().debug(line)
        return no_bad_lines

    @classmethod
    def parameterize(cls, segments: List[str]) -> List[Tuple[str, str]]:
        return [cls.clean_into_tuple(x) for x in segments]

    @classmethod
    def clean_into_tuple(cls, s: str) -> Tuple[str, str]:
        return tuple(y.strip() for y in s.split(cls.EQUALS))  # type: ignore

    def to_dict(self) -> Dict[str, str]:
        return dict(self.params)

    def keys(self) -> List[str]:
        return list(self.to_dict())

    def __getitem__(self, key: str) -> str:
        return self.to_dict()[key]


def make_slices(ids: List[int]) -> Generator[slice, None, None]:
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
