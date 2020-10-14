"""An empty-featured Stata output scraper/parser."""
import logging
import sys
from pathlib import Path

from .output import Output

__version__ = "0.0.4"

UserInput = str


class Log:
    """A full Stata Log, parsable into separate Outputs"""

    def __init__(self, text, logger=None):
        self.text = self.import_text(text)
        self.logger = logger or create_logger()
        self.outputs = []
        self.parse()

    @staticmethod
    def import_text(raw_text):
        return [line.rstrip() for line in raw_text.splitlines()]

    @classmethod
    def from_path(cls, path, logger=None):
        return cls(Path(path).read_text(), logger=logger)

    def parse(self):
        line = 0
        while line is not None and line < len(self.text):
            line = self.continue_from(line)

    def continue_from(self, line):
        handler = Output.find_handler(self.text[line])
        if handler is None:
            self.logger.debug(f"No handler for {self.text[line]}")
            return line + 1
        output = handler(self.text, line, logger=self.logger)
        self.outputs.append(output)
        return output.end

    def __len__(self):
        return len(self.text)

    def __str__(self):
        return f'{self.__class__.__name__}("something or other")'


def main() -> int:
    logger = create_logger()

    if check_cli_only():
        return 0
    raw_input = input_from_args()
    logger.debug(f"Raw input {raw_input!r}")
    if raw_input:
        path = Path(raw_input)
    else:
        path = Path(r"./test/examples/members.log")
    assert path.exists()
    log = Log.from_path(path)
    print("= Begin")
    for i, output in enumerate(log.outputs):
        print(f"== {i+1} of {len(log.outputs)}: {output}")
        output.report()
    logger.debug(f"Total table count: {len(log.outputs)}")
    print("= End")

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


def create_logger(log_file=None):
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


if __name__ == "__main__":
    sys.exit(main())
