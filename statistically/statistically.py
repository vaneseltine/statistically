"""An empty-featured Stata output scraper/parser."""
import locale
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

    def __init__(self, raw, header):
        self.results = dict()
        self.raw = raw + [""]
        self.full_text = "\n".join(self.raw)
        if self.header_is_in_table:
            header += 1
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

    @staticmethod
    def parse_n(text):
        print(text)
        obs_match = re.search(r"Number of obs[\s=]+([\d,]+)", text)
        if not obs_match:
            return None
        return locale.atoi(obs_match.group(1))

    @property
    def n(self):
        return self.results["n"]

    def report(self):
        print(self, "start")
        for attr in ("raw_header", "raw_table", "raw_footer"):
            print("    " + attr, "~" * 80)
            print(*("    " + x for x in getattr(self, attr)), sep="\n")
        print(self, "end")

    @classmethod
    def find_handler(cls, s):
        for subc in cls.members:
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
    end_table_pattern = re.compile(r"^$")


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

    def __init__(self, text):
        self.text = self.import_text(text)
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
        output = handler(self.text, line)
        self.outputs.append(output)
        return output.end

    def __len__(self):
        return len(self.text)

    def __str__(self):
        return f'{self.__class__.__name__}("something or other")'


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
    log = Log.from_path(path)
    for output in log.outputs:
        output.report()
    print(*[[o, len(o.raw_table)] for o in log.outputs])

    print(f"{len(log.outputs)} tables")

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


if __name__ == "__main__":
    sys.exit(main())
