from pathlib import Path
import re

from enum import IntEnum


class Priority(IntEnum):
    HIGHEST = 1  # commands
    HIGH = 2  # analyses
    MEDIUM = 3  # default
    LOW = 4  # lines
    LOWEST = 5


class LineLexer:
    def __init__(self, text):  # , logger=None):
        self.text = self.import_text(text)
        self.outputs = []
        self.lines = self.lex_lines(self.text)

    @staticmethod
    def import_text(raw_text):
        return [line.rstrip() for line in raw_text.splitlines()]

    def lex_lines(self, text):
        return [self.lex(s) for i, s in enumerate(text)]

    @staticmethod
    def lex(s):
        token_class = LineToken.find(s)
        print(f"{str(token_class):<20} {s}")
        token = token_class(s)
        return token

    def __iter__(self):
        return iter(self.lines)

    def __len__(self):
        return len(self.lines)


class LineToken:
    priority = Priority.MEDIUM
    is_table = False
    level = 0
    include = []
    exclude = []

    def __init__(self, s):
        self.s = s

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.include = [re.compile(x) for x in cls.include]
        cls.exclude = [re.compile(x) for x in cls.exclude]

    @classmethod
    def find(cls, s):
        checks = {subc: subc.match(s) for subc in cls.__subclasses__()}
        matches = [k for k, v in checks.items() if v]
        try:
            return cls.ascertain_winning_match(matches)
        except ValueError:
            raise ValueError(f"More than one match for {s}: {matches}")

    @classmethod
    def ascertain_winning_match(cls, matches):
        if not matches:
            return Unknown
        if len(matches) > 1:
            top_priority = min(m.priority for m in matches)
            matches = [m for m in matches if m.priority == top_priority]
        if len(matches) == 1:
            return matches.pop()
        raise ValueError("Too many matches.")

    @classmethod
    def prematch(cls, s):
        return s

    @classmethod
    def match(cls, s):
        prepared = cls.prematch(s)
        patterns_including = any(x.search(prepared) for x in cls.include)
        patterns_excluding = any(x.search(prepared) for x in cls.exclude)
        is_match = patterns_including and not patterns_excluding
        return is_match

    def __len__(self):
        return len(self.s)

    def __str__(self):
        return self.s

    def __repr__(self):
        return f'<{self.__class__.__name__}:"{self.s}">'


class Command(LineToken):
    priority = Priority.HIGHEST
    include = [
        r"^\. [^\s]",
        r"^\.\s*$",
        r"^> ",
        r"^>$",
    ]


class Unknown(LineToken):
    def __str__(self):
        return "?"


class Blank(LineToken):
    include = [r"^\s*$"]


class TableRow(LineToken):
    is_table = True
    include = [r"\s+\|"]
    exclude = [r"Pr\(\|[A-z]\|"]
    ignore_absolutes = re.compile(r"\|[A-z]\|")

    @classmethod
    def prematch(cls, s):
        fixed = cls.ignore_absolutes.sub("XXX", s)
        return fixed


class TableLineDiv(LineToken):
    is_table = True
    priority = Priority.LOW
    include = [r"^\s{0,3}-+\+-+$"]


class TableLineOuter(LineToken):
    is_table = True
    priority = Priority.LOW
    include = [r"^\s{0,3}-+$"]


class AnalysisToken:
    """
    Place this as the first subclass to inherit the high priority, etc.
    """

    priority = Priority.HIGH


class Logistic(AnalysisToken, LineToken):
    include = [r"^Logistic regression\s+Number of obs\s+="]


class Margins(AnalysisToken, LineToken):
    include = [r"^Predictive margins\s+Number of obs\s+="]


class Poisson(AnalysisToken, LineToken):
    include = [r"^Poisson regression\s+Number of obs\s+="]


class NBReg(AnalysisToken, LineToken):
    include = [r"^Negative binomial regression\s+Number of obs\s+="]


class Reg(AnalysisToken, LineToken):
    include = [r"^\s+Source \|\s+SS\s+df\s+MS\s+Number of obs\s+="]


class Summarize(AnalysisToken, LineToken):
    include = [r"^    Variable \|        Obs"]


class TabStat(AnalysisToken, LineToken):
    include = [r"^.*variable \|\s+mean\s+sd\s+min\s+max\s+N$"]


class TEBalance(AnalysisToken, LineToken):
    include = [r"^\s*Covariate balance summary\s*$"]


class TEffectsEstimation(AnalysisToken, LineToken):
    include = [r"Treatment-effects estimation\s+Number of obs\s+="]


class TTest(AnalysisToken, LineToken):
    include = [r"^Two-sample t test with equal variances"]
