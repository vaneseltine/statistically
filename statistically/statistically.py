"""An empty-featured Stata output scraper/parser."""
import re
import sys
from pathlib import Path

__version__ = "0.0.4"

UserInput = str


class Output:

    header_length = None
    footer_length = 0

    minimum_length = 1
    end_table_pattern = re.compile(r"^\s{0,3}-+$")
    header_is_in_table = False

    def __init__(self, raw, header):
        # A bit hacky, but makes things a lot easier if we force a blank line
        self.raw = raw + [""]
        if self.header_is_in_table:
            header += 1
        self.start = header
        self.table_start = self.start + self.header_length
        self.table_end = self.find_table_end(self.table_start)
        self.end = self.table_end + 1 + self.footer_length
        self.lines = self.raw[self.start : self.end]
        print(
            f"head {self.start}, table, {self.table_start}, footer, {self.table_end + 1}, end, {self.end}"
        )
        print("all", len(self.lines), sep="\n")
        self.raw_header = self.raw[self.start : self.table_start]
        self.raw_table = self.raw[self.table_start : self.table_end + 1]
        self.raw_footer = self.raw[self.table_end + 1 : self.end]

    def report(self):
        print(self, "start")
        for attr in ("raw_header", "raw_table", "raw_footer"):
            print("    " + attr, "~" * 80)
            print(*("    " + x for x in getattr(self, attr)), sep="\n")
        print(self, "end")

    @property
    def rows(self):
        return self._get_rows()

    def _get_rows(self):
        useful = [x.strip() for x in self.raw_table if re.match(r".*\d$", x)]
        split_rows = [re.split(r"[ \|]+", row) for row in useful]
        return split_rows

    @classmethod
    def find_next(cls, s):
        for subc in cls.members:
            if subc.first_line.match(s):
                print(subc, s)
                return subc
        return None

    def find_table_end(self, table_start):
        i = table_start + self.minimum_length
        while i is not None and i <= len(self.raw):
            print("looking for end of table", i, self.raw[i])
            if self.end_table_pattern.match(self.raw[i]):
                print("got it")
                return i
            i += 1
        raise RuntimeError("Coudln't find elnds")

    def __len__(self):
        return len(self.lines)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.start}--{self.end})"


class Logistic(Output):
    header_length = 5
    first_line = re.compile(r"^Logistic regression\s+Number of obs\s+=")


class Margins(Output):
    header_length = 5
    first_line = re.compile(r"^Predictive margins\s+Number of obs\s+=")


class Poisson(Output):
    header_length = 5  # does not include iterations
    first_line = re.compile(r"^Poisson regression\s+Number of obs\s+=")


class Reg(Output):
    header_length = 7
    first_line = re.compile(r"^\s+Source \|\s+SS\s+df\s+MS\s+Number of obs\s+=")


class Summarize(Output):
    header_length = 1
    first_line = re.compile(r"^    Variable \|        Obs")


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


Output.members = [
    Logistic,
    Margins,
    Poisson,
    Reg,
    Summarize,
    TabStat,
    TEBalance,
    TEffectsEstimation,
    TTest,
]


class Log:
    """A full Stata log, parsable into separate Outputs"""

    table_start = re.compile(r"^\s*[ -]+$")

    def __init__(self, path):
        self.path = Path(path)
        self.text = self.import_text()
        self.outputs = []

    def import_text(self, path=None):
        path = path or self.path
        return [line.rstrip() for line in path.read_text().splitlines()]

    def parse(self):
        line = 0
        while line is not None and line < len(self.text):
            line = self.advance_line(line)
        return self.outputs

    def advance_line(self, line):
        handler = Output.find_next(self.text[line])
        if handler is None:
            return line + 1
        output = handler(self.text, line)
        self.outputs.append(output)
        return output.end

    def __len__(self):
        return len(self.text)

    def __str__(self):
        return f'{self.__class__.__name__}("{self.path}")'


def main() -> int:
    if check_cli_only():
        return 0
    raw_input = input_from_args()
    print("Raw input", repr(raw_input))
    if raw_input:
        path = Path(raw_input)
    else:
        path = Path(r"./test/examples/members.log")
    assert path.exists()
    log = Log(path)
    outputs = log.parse()
    for output in outputs:
        output.report()
    print(*[[o, len(o.raw_table)] for o in outputs])

    print(f"{len(outputs)} tables")

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


def report_version() -> None:
    package = f"statistically {__version__} at {Path(__file__).parent.absolute()}"
    py_version = f"on Python {sys.version.split(' ')[0]} at {sys.executable}"
    print(f"{package}\n{py_version}")


def report_help() -> None:
    """
    Report something useful, at some point.
    """
    print("Try: statistically blah.log")


def input_from_args() -> UserInput:
    """
    Just smash together all arguments from the command line.
    """
    command_line_input: UserInput = " ".join(sys.argv[1:])
    return command_line_input


if __name__ == "__main__":
    sys.exit(main())
