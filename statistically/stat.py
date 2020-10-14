import locale

locale.setlocale(locale.LC_ALL, "en_US.UTF8")


class Stat:

    converters = {float: locale.atof, int: locale.atoi, str: str}
    preferred = None

    def __init__(self, raw_value):
        self.raw = raw_value
        self.value = self.convert(raw_value)

    def convert(self, raw_value):
        converter = self.converters[self.preferred]
        return converter(raw_value)

    def pretty(self):
        pass

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.raw})=={self.value}"


class P(Stat):

    short = "p"
    long = "p-value"
    preferred = float

    @property
    def pretty(self):
        return f"p={self.value}"


# ("p", "p-value", float)

print(P)
p1 = P("034.3")
print(p1)
print(repr(p1))
print(p1.pretty)
