from pathlib import Path
import re


class Token:
    priority = False
    include = [re.compile(x) for x in [r"^\. [^\s]", r"^\.\s*$", r"^> ", r"^>$",]]
    exclude = []

    def __init__(self, s):
        self.s = s

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
    def match(self, s):
        includes = any(x.search(s) for x in self.include)
        excludes = any(x.search(s) for x in self.exclude)
        is_match = includes and not excludes
        return is_match

    def __str__(self):
        return self.__class__.__name__


# todo: @register to re.compile everything together
class Command(Token):
    priority = True
    include = [re.compile(x) for x in [r"^\. [^\s]", r"^\.\s*$", r"^> ", r"^>$",]]


class Blank(Token):
    include = [re.compile(x) for x in [r"^\s*$"]]


class Unknown(Token):
    include = []


class TableRow(Token):
    include = [re.compile(x) for x in [r"\s+\|"]]


class TableLineDiv(Token):
    include = [re.compile(x) for x in [r"^-+\+-+$"]]


class TableLineOut(Token):
    include = [re.compile(x) for x in [r"^-+$"]]


class Lexer:
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
        token = Token.find(s)
        if token:
            token = token(s)
        token = token or "-"
        # if "|" in s:
        # print(token)
        print(f"{line:<6} {str(token):<20} {s}")
        # print(line, token, s)
        if line > 100:
            return None
        return line + 1

    def __len__(self):
        return len(self.text)

    def __str__(self):
        return f'{self.__class__.__name__}("something or other")'
