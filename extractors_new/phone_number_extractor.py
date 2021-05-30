from typing import Dict, List, Any
from phonenumbers import PhoneNumberMatcher, PhoneNumberFormat, number_type, format_number

from extracting_tasks import ExtractingTask


class PhoneNumberExtractor(ExtractingTask):
    type_mappings = {
        0: 'phone',
        1: 'mobile',
        2: 'phone',
    }

    def __init__(self, lines: Dict[int, str], country_code: str = None):
        self._country_code: str = country_code
        self._lines: Dict[int, str] = lines
        self._extracted: List[Dict[str, Any]] = self._extract()

    def _extract(self) -> List[Dict[str, Any]]:
        phone_numbers: List[Dict[str, Any]] = []

        for line_index, line in self.lines.items():
            for match in PhoneNumberMatcher(line, self.country_code):
                phone_number_type: int = number_type(match.number)
                # TODO: distinct between fax and phone
                phone_numbers.append({
                    'type': self.type_mappings[phone_number_type] if phone_number_type in self.type_mappings else self.type_mappings[0],
                    'match': format_number(match.number, PhoneNumberFormat.E164),
                    'index': line_index
                })

        return phone_numbers

    @property
    def country_code(self):
        return self._country_code

    @property
    def lines(self):
        return self._lines

    @property
    def extracted(self):
        return self._extracted


if __name__ == '__main__':
    pne = PhoneNumberExtractor({1: 'adw 09331 87400, 08 06 32, 77694 Kehl. Fax: 09331 874044'}, 'DE')
    print(pne.extracted)
