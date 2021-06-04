"""An empty-featured Stata output scraper/parser."""
import logging
import sys
from glob import glob
from pathlib import Path
from typing import Optional

from .log import TextLog

__version__ = "0.1.0dev0"

UserInput = str


def main() -> int:
    logger = create_logger()

    if handle_cli_only():
        return 0
    raw_input = input_from_args()
    logger.debug(f"Raw input {raw_input!r}")
    for filename in glob(raw_input):
        print("\n", filename, "\n")
        print(Path(filename).read_text())
        TextLog(filename)
    return 0


def handle_cli_only() -> bool:
    args = sys.argv[1:]
    if not args or "-h" in args or "--help" in args:
        report_help()
        return True
    if "-V" in args or "--version" in args:
        report_version()
        return True
    return False


def input_from_args() -> UserInput:
    """
    Just smash together all arguments from the command line.
    """
    command_line_input: UserInput = " ".join(sys.argv[1:])
    return command_line_input


def report_help() -> None:
    """
    Report something useful, at some point.
    """
    print("Try: statistically blah.log")


def report_version() -> None:
    package = f"statistically {__version__} at {Path(__file__).parent.absolute()}"
    py_version = f"on Python {sys.version.split(' ')[0]} at {sys.executable}"
    print(f"{package}\n{py_version}")


def create_logger(log_file: Optional[str] = None) -> logging.Logger:
    """

    Another option:
        sfmt="{asctime} {levelname:>7} {message}", style="{", datefmt=r"%H:%M:%S"
    """

    formatter = logging.Formatter(
        fmt="{asctime} {name:<20} {lineno:>3}:{levelname:<7} {message}",
        style="{",
        datefmt=r"%Y%m%d-%H%M%S",
    )
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    handlers = [stream_handler]
    if log_file is not None:
        file_handler = logging.FileHandler(filename=log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    logging.basicConfig(level=logging.DEBUG, handlers=handlers)

    new_logger = logging.getLogger(__name__)
    if log_file:
        new_logger.debug(f"Logging to {log_file}")
    return new_logger
