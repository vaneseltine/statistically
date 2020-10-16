from pathlib import Path
import re


class LineLexer:
    def __init__(self, text):  # , logger=None):
        self.text = self.import_text(text)
        self.outputs = []
        self.lines = self.lex_lines(self.text)

    @classmethod
    def from_path(cls, path):
        return cls(Path(path).read_text())

    @staticmethod
    def import_text(raw_text):
        return [line.rstrip() for line in raw_text.splitlines()]

    def lex_lines(self, text):
        return {i: self.lex(s) for i, s in enumerate(text)}

    @staticmethod
    def lex(s):
        token_class = LineToken.find(s)
        token = token_class(s)
        # print(f"{str(token):<20} {s}")
        return token

    def __len__(self):
        return len(self.lines)


class LineToken:
    priority = False
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
            print(f"More than one match for {s}", *matches, sep="\n")

    @classmethod
    def ascertain_winning_match(cls, matches):
        if Command in matches:
            # overrides all others
            return Command
        winner = cls.exactly_one(matches)
        if winner is None:
            return Unknown
        return winner

    @staticmethod
    def exactly_one(matches: set):
        if not matches:
            return None
        if len(matches) > 1:
            raise ValueError("More than one match")
        return matches.pop()

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
    priority = True
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
    include = [r"^\s{0,3}-+\+-+$"]


class TableLineOuter(LineToken):
    include = [r"^\s{0,3}-+$"]
