import locale
import re
from typing import Any, Callable, Dict, Optional, Type, Union

locale.setlocale(locale.LC_ALL, "en_US.UTF8")

FLOAT_PATTERN = re.compile(r"([-\de.]+)")

AmbiguousValue = Union[str, float, int]


class Stat:

    converters: Dict[Type[Any], Callable[[str], AmbiguousValue]] = {
        float: locale.atof,
        int: locale.atoi,
        str: str,
    }
    core_format: Type[Any] = float
    default_name = None
    str_format = "{}"

    def __init__(
        self,
        raw_value: AmbiguousValue,
        *,
        name: Optional[str] = None,
        core_format: Optional[Type[Any]] = None,
    ) -> None:
        self.raw = raw_value
        self.core_format = core_format or self.core_format
        self.value: AmbiguousValue = self.convert(raw_value)
        self.name = name or self.default_name or self.__class__.__name__
        self.validate()

    def convert(self, raw: AmbiguousValue) -> AmbiguousValue:
        return self.converters[self.core_format](str(raw))

    def validate(self) -> None:
        try:
            self.make_validation_assertions()
        except AssertionError as err:
            invalid_msg = f"Input {self.raw!r} failed validation as {self!r}"
            raise ValueError(invalid_msg) from err

    def make_validation_assertions(self) -> None:
        pass

    def __str__(self) -> str:
        return self.str_format.format(self.value)

    def __float__(self) -> float:
        return float(self.value)

    def __eq__(self, other: object) -> bool:
        try:
            return float(self) == float(other)  # type: ignore
        except ValueError:
            return str(self) == str(other)

    def __repr__(self) -> str:
        print(self.name)
        return f"{str(self.name)}({self.value!r})"


class N(Stat):

    core_format = int
    default_name = "n"

    def make_validation_assertions(self) -> None:
        assert isinstance(self.value, int)
        assert self.value > 0

    def __str__(self) -> str:
        return "{:,}".format(self.value)


class P(Stat):

    core_format = float
    default_name = "P"

    def make_validation_assertions(self) -> None:
        assert isinstance(self.value, float)
        assert 0 <= self.value <= 1

    def __str__(self) -> str:
        return "{:.3f}".format(self.value).lstrip("0")  # type: ignore


class Group(Stat):

    core_format = str


class Label(Stat):

    core_format = str


class Parameter(Stat):

    core_format = str


class Text(Stat):

    core_format = str


class Variable(Stat):

    core_format = str
