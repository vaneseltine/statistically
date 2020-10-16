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
        return {i: self.lex(s) for i, s in enumerate(text)}

    @staticmethod
    def lex(s):
        token_class = LineToken.find(s)
        print(f"{str(token_class):<20} {s}")
        token = token_class(s)
        return token

    def __len__(self):
        return len(self.lines)


class LineToken:
    priority = Priority.MEDIUM
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
        return self.__class__.__name__

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
    include = [r"\s+\|"]
    exclude = [r"Pr\(\|[A-z]\|"]
    ignore_absolutes = re.compile(r"\|[A-z]\|")

    @classmethod
    def prematch(cls, s):
        fixed = cls.ignore_absolutes.sub("XXX", s)
        return fixed


class TableLineDiv(LineToken):
    priority = Priority.LOW
    include = [r"^\s{0,3}-+\+-+$"]


class TableLineOuter(LineToken):
    priority = Priority.LOW
    include = [r"^\s{0,3}-+$"]


class AnalysisToken:
    """
    Place this as the first subclass to inherit the high priority.
    """

    priority = Priority.HIGH


class AnalysisLogistic(AnalysisToken, LineToken):
    include = [r"^Logistic regression\s+Number of obs\s+="]


class AnalysisMargins(AnalysisToken, LineToken):
    include = [r"^Predictive margins\s+Number of obs\s+="]


class AnalysisPoisson(AnalysisToken, LineToken):
    include = [r"^Poisson regression\s+Number of obs\s+="]


class AnalysisNBReg(AnalysisToken, LineToken):
    include = [r"^Negative binomial regression\s+Number of obs\s+="]


class AnalysisReg(AnalysisToken, LineToken):
    include = [r"^\s+Source \|\s+SS\s+df\s+MS\s+Number of obs\s+="]


class AnalysisSummarize(AnalysisToken, LineToken):
    include = [r"^    Variable \|        Obs"]


class AnalysisTabStat(AnalysisToken, LineToken):
    include = [r"^.*variable \|\s+mean\s+sd\s+min\s+max\s+N$"]


class AnalysisTEBalance(AnalysisToken, LineToken):
    include = [r"^\s*Covariate balance summary\s*$"]


class AnalysisTEffectsEstimation(AnalysisToken, LineToken):
    include = [r"Treatment-effects estimation\s+Number of obs\s+="]


class AnalysisTTest(AnalysisToken, LineToken):
    include = [r"^Two-sample t test with equal variances"]
