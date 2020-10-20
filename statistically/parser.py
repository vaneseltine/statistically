import locale
import logging
import re
from enum import IntEnum

from . import lexer
from . import stat

locale.setlocale(locale.LC_ALL, "en_US.UTF8")


class Collecting(IntEnum):
    HEADER = 1
    TABLE = 2
    FOOTER = 3


class Section:

    handlers = {}

    def __init__(self):
        self.properties = []

    def __init_subclass__(cls, **kwargs):
        cls.handlers.update({k: cls for k in cls.handlees})
        super().__init_subclass__(**kwargs)

    @classmethod
    def find(cls, line):
        return cls.handlers.get(line.__class__, SectionNull)

    def report(self):
        raise NotImplementedError

    def __call__(self, line):
        raise NotImplementedError

    def __str__(self):
        return str(self.__class__)


class SectionNull(Section):
    handlees = []

    def report(self):
        pass

    def __call__(self, line):
        # print(f"{self} for {line!r}")
        return False


class SectionNBReg(Section):
    handlees = [lexer.NBReg]

    row_divider_pattern = re.compile(r"^[-+ ]+$")
    row_data_pattern = re.compile(r"[^-\w#,+.]+")
    row_variable_pattern = re.compile(r"([/\w#]+)\s+\|$")
    row_not_estimable = re.compile(r"not estimable")
    skippable = re.compile(r"(\-\-\-)|Delta-method|(95% Conf. Interval)|(^[ \|]+$)")
    columns = {
        "iv": stat.Label,
        "coef": stat.Stat,
        "std_err": stat.Stat,
        "z": stat.Stat,
        "p_z": stat.P,
        "ci_lo": stat.Stat,
        "ci_hi": stat.Stat,
    }

    def __init__(self):
        super().__init__()
        self.header = []
        self.raw_table = []
        self.footer = []
        self.raw_table_line_counter = 0
        self.funnel = self.header
        self.table = []
        self.properties = dict()
        self._tracking_variable = None

    def __call__(self, line):
        if line.is_table:
            self.funnel = self.raw_table
        if isinstance(line, lexer.TableLineOuter):
            self.raw_table_line_counter += 1
        self.funnel.append(line)
        if self.raw_table_line_counter == 2:
            self.funnel = self.footer
        if len(self.footer) >= 1:
            self.complete()
            return False
        return True

    def complete(self):
        self.properties = self.assemble_properties()
        self.table = self.construct_table()

    def assemble_properties(self):
        auto_stats = dict(self.auto_parse_stats())
        stats = {
            "analysis": "nbreg",
            "dv": self.get_dv(),
            "alpha": self.extract_from_raw("  alpha |"),
            "/lnalpha": self.extract_from_raw("/lnalpha |"),
        }
        stats.update(auto_stats)
        return stats

    def extract_from_raw(self, s, stat_type=stat.Stat):
        matches = [l for l in self.raw_table if s in str(l)]
        assert len(matches) == 1
        line = matches[0]
        self.raw_table.remove(line)
        value = stat.FLOAT_PATTERN.search(str(line)).group(0)

        return stat_type(value)

    def auto_parse_stats(self):
        for h in self.header:
            for s in h.s.split("            "):
                raw_eq = s.split("=")
                if len(raw_eq) != 2:
                    continue
                label, raw_value = (x.strip() for x in raw_eq)
                formatted = stat.Stat.auto(label, raw_value)
                yield (label, formatted)

    def get_dv(self):
        raw_dv, *_ = str(self.raw_table[1]).split("|")
        return raw_dv.strip()

    def report(self):
        # print(self)
        # print(self.header)
        print(self.properties)
        print(*self.table, sep="\n")
        # print(self.footer)

    def construct_table(self):
        pre_table = [self.add_row(i, row) for i, row in enumerate(self.raw_table)]
        return [row for row in pre_table if row]

    def add_row(self, i, row):
        row = str(row).strip()
        if self.no_useful_values(row):
            self._tracking_variable = None
            return None
        if self.row_variable_pattern.match(row):
            self._tracking_variable = self.row_variable_pattern.match(row).group(1)
            return None
        stats = self.create_stats(row)
        stats["variable"] = self._tracking_variable
        stats["line"] = i
        return stats

    def no_useful_values(self, row):
        if self.row_divider_pattern.match(row):
            return True
        if self.skippable.search(row):
            return True
        if self.row_not_estimable.search(row):
            return True
        return False

    def create_stats(self, row):
        values = self.values_from_row(row)
        stat_classes = (v for v in self.columns.values())
        stat_labels = (k for k in self.columns)
        staticized = [c(v) for c, v in zip(stat_classes, values)]
        dictionized = {l: s for l, s in zip(stat_labels, staticized)}
        return dictionized

    def values_from_row(self, row):
        return self.row_data_pattern.split(row)


class Parser:

    section_handlers = {lexer.NBReg: SectionNBReg}

    def __init__(self, lexed):
        self.active_handler = None
        self.groups = []
        self.group(lexed)

    def report(self):
        print(self.groups)
        for g in self.groups:
            if g:
                g.report()

    def group(self, lexed):
        keep_handler = False
        # Could enumerate the following to keep line numbers
        for line in lexed:
            if not keep_handler:
                self.groups.append(self.active_handler)
                self.active_handler = Section.find(line)()
            keep_handler = self.active_handler(line)


class Equation:
    @staticmethod
    def parse_n(text):
        obs_match = re.search(r"Number of obs[\s]+=[\s]+([\d,]+)", text)
        if not obs_match:
            return None
        return N(obs_match.group(1))

    @property
    def n(self):
        return self.results["n"]
