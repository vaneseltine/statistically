"""An empty-featured Stata output scraper/parser."""
import sys
from pathlib import Path

__version__ = "0.0.4"

UserInput = str


def main() -> int:
    if check_cli_only():
        return 0
    raw_input = input_from_args()
    print("Raw input", repr(raw_input))
    return 0


def check_cli_only() -> bool:
    args = sys.argv[1:]
    if not args or "-h" in args or "--help" in args:
        report_help()
        return True
    if "-V" in args or "--version" in args:
        report_version()
        return True
    return False


def report_version() -> None:
    package = f"statistically {__version__} at {Path(__file__).parent.absolute()}"
    py_version = f"on Python {sys.version.split(' ')[0]} at {sys.executable}"
    print(f"{package}\n{py_version}")


def report_help() -> None:
    """
    Report something useful, at some point.
    """
    print("Try: statistically blah.log")


def input_from_args() -> UserInput:
    """
    Just smash together all arguments from the command line.
    """
    command_line_input: UserInput = " ".join(sys.argv[1:])
    return command_line_input


if __name__ == "__main__":
    sys.exit(main())
