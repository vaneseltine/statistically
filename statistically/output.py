import locale
import logging
import re

from .stat import Label, N, P, Stat

locale.setlocale(locale.LC_ALL, "en_US.UTF8")


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
        self.parse_analysis_properties()

    def parse_analysis_properties(self):
        # print(self.lines)
        self.results["n"] = self.parse_n(" ".join(self.lines))

    @property
    def table(self):
        return []

    @staticmethod
    def parse_n(text):
        obs_match = re.search(r"Number of obs[\s]+=[\s]+([\d,]+)", text)
        if not obs_match:
            return None
        return N(obs_match.group(1))

    @property
    def n(self):
        return self.results["n"]

    def report(self):
        indent = "   "
        header_line = "==="
        for attr in ("raw_header", "raw_table", "raw_footer"):
            print(header_line, attr)
            print(*(indent + " " + x for x in getattr(self, attr)), sep="\n")
        print(header_line, "analysis properties")
        print(indent, self.results)
        print(header_line, "tables rows")
        for row in self.table:
            print(indent, row)

    @classmethod
    def find_handler(cls, s):
        checks = {subc: subc.is_hander_for(s) for subc in cls.__subclasses__()}
        matches = [key for key, value in checks.items() if value]
        if not matches:
            return None
        if len(matches) > 1:
            raise ValueError(f"Found multiple handlers for {s}")
        return matches[0]

    @classmethod
    def is_hander_for(cls, s):
        return bool(cls.first_line.match(s))

    def find_table_end(self, table_start):
        i = table_start + self.minimum_length
        while i is not None and i < len(self.raw):
            if self.end_table_pattern.match(self.raw[i]):
                return i
            i += 1
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
    row_data_pattern = re.compile(r"[^-\w#,+.]+")
    row_variable_pattern = re.compile(r"([\w#]+)\s+\|$")
    row_not_estimable = re.compile(r"not estimable")
    skippable = re.compile(r"(\-\-\-)|Delta-method|(95% Conf. Interval)|(^[ \|]+$)")
    columns = "value margin std_err z p_z ci_lo ci_hi".split()
    stats = [Label, Stat, Stat, Stat, P, Stat, Stat]
    _table = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.variable = None

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
        if not self.has_useful_values(row):
            return None
        stats = self.create_stats(row)
        labeled = dict(zip(self.columns, stats))
        labeled["variable"] = self.variable
        labeled["line"] = i
        return labeled

    def has_useful_values(self, row):
        if self.row_divider_pattern.match(row):
            return False
        if self.skippable.search(row):
            return False
        if self.row_not_estimable.search(row):
            return False
        if self.row_variable_pattern.match(row):
            self.variable = self.row_variable_pattern.match(row).group(1)
            return False
        return True

    def create_stats(self, row):
        values = self.row_data_pattern.split(row)
        stats = [c(v) for c, v in zip(self.stats, values)]
        return stats


class Poisson(Output):
    header_length = 5  # does not include iterations
    first_line = re.compile(r"^Poisson regression\s+Number of obs\s+=")


class NBReg(Output):
    header_length = 5  # does not include iterations
    footer_length = 5
    minimum_length = 4
    first_line = re.compile(r"^Negative binomial regression\s+Number of obs\s+=")
    end_table_pattern = re.compile(r"-+\+-+$")


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
    header_length = 2
    footer_length = 5
    first_line = re.compile(r"^Two-sample t test with equal variances")
