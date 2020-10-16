from pathlib import Path
import re


class Token:
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
        if Command in matches:
            # overrides other potential matches, since they could have anything
            return Command
        try:
            winner = cls.return_exactly_one(matches)
        except ValueError as err:
            print(s, matches)
            raise (err)
        if winner is None:
            return Unknown
        return winner

    @staticmethod
    def return_exactly_one(matches: set):
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
        s = cls.prematch(s)
        patterns_including = any(x.search(s) for x in cls.include)
        patterns_excluding = any(x.search(s) for x in cls.exclude)
        is_match = patterns_including and not patterns_excluding
        return is_match

    def __str__(self):
        return self.__class__.__name__


# todo: @register to re.compile everything together
class Command(Token):
    priority = True
    include = [
        r"^\. [^\s]",
        r"^\.\s*$",
        r"^> ",
        r"^>$",
    ]


class Blank(Token):
    include = [r"^\s*$"]


class Unknown(Token):
    def __str__(self):
        return "?"


class TableRow(Token):
    include = [r"\s+\|"]
    exclude = [r"Pr\(\|[A-z]\|"]
    ignore_absolutes = re.compile(r"\|[A-z]\|")

    @classmethod
    def prematch(cls, s):
        fixed = cls.ignore_absolutes.sub("XXX", s)
        return fixed


class TableLineDiv(Token):
    include = [r"^\s{0,3}-+\+-+$"]


class TableLineOuter(Token):
    include = [r"^\s{0,3}-+$"]


class LineLexer:
    def __init__(self, text):  # , logger=None):
        self.text = self.import_text(text)
        self.outputs = []
        self.lex()

    @staticmethod
    def import_text(raw_text):
        return [line.rstrip() for line in raw_text.splitlines()]

    @classmethod
    def from_path(cls, path):
        return cls(Path(path).read_text())

    def lex(self):
        line = 0
        while line is not None and line < len(self.text):
            line = self.continue_from(line)

    def continue_from(self, line):
        s = self.text[line]
        token_class = Token.find(s)
        token = token_class(s)
        print(f"{line:<6} {str(token):<20} {s}")
        # if line >= 500:
        #     return None
        return line + 1

    def __len__(self):
        return len(self.text)

    def __str__(self):
        return f'{self.__class__.__name__}("something or other")'
