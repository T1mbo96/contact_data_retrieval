from typing import Dict
from phonenumbers import PhoneNumberMatcher
from abc import ABC, abstractmethod


class PhoneNumberExtractor(ABC):
    @abstractmethod
    def extract_lines(self, lines: Dict[int, str]) -> Dict[int, str]:
        pass


class LibPhoneNumberExtractor(PhoneNumberExtractor):
    def __init__(self, country_code: str):
        self._country_code: str = country_code

    def extract_lines(self, lines: Dict[int, str]) -> Dict[int, str]:
        phone_number_lines: Dict[int, str] = {}

        for line_index, line in lines.items():
            for match in PhoneNumberMatcher(line, self.country_code):
                if line_index not in phone_number_lines:
                    phone_number_lines[line_index] = line

        return phone_number_lines

    @property
    def country_code(self):
        return self._country_code
