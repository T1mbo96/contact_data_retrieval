import re

from typing import Dict
from abc import ABC, abstractmethod


class MailAddressExtractor(ABC):
    @abstractmethod
    def extract_lines(self, lines: Dict[int, str]) -> Dict[int, str]:
        pass


class RegExMailAddressExtractor(MailAddressExtractor):
    def __init__(self, pattern: str):
        self._pattern: str = pattern

    def extract_lines(self, lines: Dict[int, str]) -> Dict[int, str]:
        mail_address_lines: Dict[int, str] = {}

        for line_index, line in lines.items():
            if re.findall(self.pattern, line):
                mail_address_lines[line_index] = line

        return mail_address_lines

    @property
    def pattern(self):
        return self._pattern
