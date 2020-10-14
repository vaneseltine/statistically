import locale

locale.setlocale(locale.LC_ALL, "en_US.UTF8")


class Stat:

    converters = {float: locale.atof, int: locale.atoi, str: str}
    core_format = float
    str_format = "{}"

    def __init__(self, raw_value, final_value=None):
        self.raw = raw_value
        self.value = final_value or self.convert(raw_value)
        self.validate()

    def convert(self, raw):
        return self.converters[self.core_format](str(raw))

    def validate(self):
        try:
            self.make_validation_assertions()
        except AssertionError:
            raise ValueError(f"Input {self.raw!r} failed validation as {self!r}")

    def make_validation_assertions(self):
        pass

    @property
    def name(self):
        return self.__class__.__name__.lower()

    def __str__(self):
        return self.str_format.format(self.value)

    def __float__(self):
        return float(self.value)

    def __eq__(self, other):
        try:
            return float(self) == float(other)
        except ValueError:
            return str(self) == str(other)

    def __repr__(self):
        return f"{self.__class__.__name__}({self!s})"


class P(Stat):

    core_format = float

    def make_validation_assertions(self):
        assert self.value <= 1
        assert self.value >= 0

    def __str__(self):
        return "{:.3f}".format(self.value).lstrip("0")


class N(Stat):

    core_format = int

    def make_validation_assertions(self):
        assert self.value > 0

    def __str__(self):
        return "{:.3f}".format(self.value).lstrip("0")


class Label(Stat):

    core_format = str
