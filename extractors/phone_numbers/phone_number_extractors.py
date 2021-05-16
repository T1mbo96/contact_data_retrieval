from typing import Dict
from phonenumbers import PhoneNumberMatcher

from abstract_classes.contact_data_retrieval_tasks import CountrySpecificContactDataRetrievalTask


class LibPhoneNumberExtractor(CountrySpecificContactDataRetrievalTask):
    def __init__(self, country_code: str):
        self._country_code: str = country_code

    def extract_lines(self, lines: Dict[int, str]) -> Dict[int, str]:
        matched_lines: Dict[int, str] = {}

        for line_index, line in lines.items():
            if PhoneNumberMatcher(line, self.country_code).has_next():
                matched_lines[line_index] = line

        return matched_lines

    @property
    def country_code(self) -> str:
        return self._country_code
