from pathlib import Path
from typing import Union
import re


class TextLog:
    def __init__(self, path: Union[Path, str]) -> None:
        self.path = Path(path)
        self.raw: str = self.path.read_text()
        print(self.raw)
        self.find_columns(self.raw)

    @staticmethod
    def find_columns(s: str):
        column_finder = re.compile(" [|+=] ")
        for line in s.splitlines():
            print(line)
            print(column_finder.search(line))
