"""An empty-featured Stata output scraper/parser."""
import locale
import logging
import re
import sys
from pathlib import Path

locale.setlocale(locale.LC_ALL, "en_US.UTF8")

__version__ = "0.0.4"

UserInput = str


class Output:

    header_length = None
    footer_length = 0

    minimum_length = 1
    end_table_pattern = re.compile(r"^\s{0,3}-+$")
    header_is_in_table = False

    def __init__(self, raw, header, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.results = dict()
        self.raw = raw + [""]
        self.full_text = "\n".join(self.raw)
        if self.header_is_in_table:
            header -= 1
        self.start = header
        self.table_start = self.start + self.header_length
        self.table_end = self.find_table_end(self.table_start)
        self.end = self.table_end + 1 + self.footer_length
        self.lines = self.raw[self.start : self.end]
        print(
            f"head {self.start},",
            f"table, {self.table_start},",
            f"footer, {self.table_end + 1},",
            f"end, {self.end}",
        )
        self.raw_header = self.raw[self.start : self.table_start]
        self.raw_table = self.raw[self.table_start : self.table_end + 1]
        self.raw_footer = self.raw[self.table_end + 1 : self.end]
        self.parse_results()

    def parse_results(self):
        self.results["n"] = self.parse_n(self.full_text)

    @property
    def table(self):
        return []

    @staticmethod
    def parse_n(text):
        obs_match = re.search(r"Number of obs[\s=]+([\d,]+)", text)
        if not obs_match:
            return None
        return locale.atoi(obs_match.group(1))

    @property
    def n(self):
        return self.results["n"]

    def report(self):
        INDENT = "   "
        HEADER = "==="
        for attr in ("raw_header", "raw_table", "raw_footer"):
            print(HEADER, attr)
            print(*(INDENT + " " + x for x in getattr(self, attr)), sep="\n")
        print(HEADER, "analysis properties")
        print(INDENT, f"{'key':<20} value")
        for k, v in self.results.items():
            print(INDENT, f"{k:<20} {v}")
        print(HEADER, "tables rows")
        for row in self.table:
            print(INDENT, row)

    @classmethod
    def find_handler(cls, s):
        for subc in cls.__subclasses__():
            if subc.first_line.match(s):
                # print(subc, s)
                return subc
        return None

    def find_table_end(self, table_start):
        i = table_start + self.minimum_length
        while i is not None and i < len(self.raw):
            # print(i)
            # print(len(self.raw), repr(self.raw))
            # print("looking for end of table", i, self.raw[i])
            if self.end_table_pattern.match(self.raw[i]):
                # print("got it")
                return i
            i += 1
        # raise RuntimeWarning("Could not find end of table, got to end of file")
        return len(self.raw) - 1

    def __len__(self):
        return len(self.lines)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.start}-{self.end})"


class Logistic(Output):
    header_length = 5
    first_line = re.compile(r"^Logistic regression\s+Number of obs\s+=")


class Margins(Output):
    header_length = 5
    first_line = re.compile(r"^Predictive margins\s+Number of obs\s+=")
    row_divider_pattern = re.compile(r"^[-+ ]+$")
    row_data_pattern = re.compile(r"[^-\d,+.]+")
    row_treatment_pattern = re.compile(r"[\w]+\s+\|$")
    skippable = re.compile(r"(\-\-\-)|Delta-method|(95% Conf. Interval)|(^[ \|]+$)")
    data_columns = "value margin std_err z p_z ci_lo ci_hi".split()
    _table = None

    @property
    def table(self):
        if self._table is not None:
            return self._table
        self._table = self.construct_table()
        return self.table

    def construct_table(self):
        pre_table = [self.add_row(i, row) for i, row in enumerate(self.raw_table)]
        return [row for row in pre_table if row]

    def add_row(self, i, row):
        row = row.strip()
        if self.row_divider_pattern.match(row):
            return None
        if self.skippable.search(row):
            return None
        print(row)
        if self.row_treatment_pattern.match(row):
            print(self.row_treatment_pattern.match(row))
            return None
        values = self.row_data_pattern.split(row)
        result_dict = {
            k: locale.atof(values[i]) for i, k in enumerate(self.data_columns)
        }
        result_dict["line"] = i
        return result_dict


class Poisson(Output):
    header_length = 5  # does not include iterations
    first_line = re.compile(r"^Poisson regression\s+Number of obs\s+=")


class Reg(Output):
    header_length = 7
    first_line = re.compile(r"^\s+Source \|\s+SS\s+df\s+MS\s+Number of obs\s+=")


class Summarize(Output):
    header_length = 1
    first_line = re.compile(r"^    Variable \|        Obs")
    end_table_pattern = re.compile(r"^$")
    header_is_in_table = True


class TabStat(Output):
    header_length = 1
    first_line = re.compile(r"^.*variable \|\s+mean\s+sd\s+min\s+max\s+N$")
    minimum_length = 2


class TEBalance(Output):
    header_length = 8
    first_line = re.compile(r"^\s*Covariate balance summary\s*$")
    end_table_pattern = re.compile(r"^\s{0,3}-+$")


class TEffectsEstimation(Output):
    header_length = 4
    first_line = re.compile(r"Treatment-effects estimation\s+Number of obs\s+=")


class TTest(Output):
    header_length = 1
    footer_length = 5
    first_line = re.compile(r"^Two-sample t test with equal variances$")


class Log:
    """A full Stata log, parsable into separate Outputs"""

    table_start = re.compile(r"^\s*[ -]+$")

    def __init__(self, text, logger=None):
        self.text = self.import_text(text)
        self.logger = logger
        self.outputs = []
        self.parse()

    @staticmethod
    def import_text(raw_text):
        return [line.rstrip() for line in raw_text.splitlines()]

    @classmethod
    def from_path(cls, path):
        return cls(Path(path).read_text())

    def parse(self):
        line = 0
        while line is not None and line < len(self.text):
            line = self.advance_line(line)

    def advance_line(self, line):
        handler = Output.find_handler(self.text[line])
        if handler is None:
            return line + 1
        output = handler(self.text, line, logger=self.logger)
        self.outputs.append(output)
        return output.end

    def __len__(self):
        return len(self.text)

    def __str__(self):
        return f'{self.__class__.__name__}("something or other")'


def main() -> int:
    logger = get_statistically_logger()

    if check_cli_only():
        return 0
    raw_input = input_from_args()
    logger.debug(f"Raw input {raw_input!r}")
    if raw_input:
        path = Path(raw_input)
    else:
        path = Path(r"./test/examples/members.log")
    assert path.exists()
    log = Log.from_path(path)
    print("= Begin")
    for i, output in enumerate(log.outputs):
        print(f"== {i+1} of {len(log.outputs)}: {output}")
        output.report()
    logger.debug(f"Total table count: {len(log.outputs)}")
    print("= End")

    return 0


def check_cli_only() -> bool:
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        report_help()
        return True
    if "-V" in args or "--version" in args:
        report_version()
        return True
    return False


def input_from_args() -> UserInput:
    """
    Just smash together all arguments from the command line.
    """
    command_line_input: UserInput = " ".join(sys.argv[1:])
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


def get_statistically_logger(log_file=None):
    """

    Another option:
        sfmt="{asctime} {levelname:>7} {message}", style="{", datefmt=r"%H:%M:%S"
    """

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

    new_logger = logging.getLogger(__name__)
    if log_file:
        new_logger.debug(f"Logging to {log_file}")
    return new_logger


if __name__ == "__main__":
    sys.exit(main())
