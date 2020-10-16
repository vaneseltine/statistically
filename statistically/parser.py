import locale
import logging
import re

from .stat import Label, N, P, Stat

locale.setlocale(locale.LC_ALL, "en_US.UTF8")


class Parser:
    def __init__(self, lexed):
        print(lexed)
        exit()


class Analysis:

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

    def report(self):
        INDENT = "   "
        HEADER = "==="
        for attr in ("raw_header", "raw_table", "raw_footer"):
            print(HEADER, attr)
            print(*(INDENT + " " + x for x in getattr(self, attr)), sep="\n")
        print(HEADER, "analysis properties")
        print(INDENT, self.results)
        print(HEADER, "tables rows")
        for row in self.table:
            print(INDENT, row)

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
