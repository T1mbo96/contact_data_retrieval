import re

from typing import Dict, List, Any
from phonenumbers import PhoneNumberMatcher, PhoneNumberFormat, number_type, format_number

from extractors.extracting_tasks import ExtractingTask


class PhoneNumberExtractor(ExtractingTask):
    type_mappings = {
        0: 'phone',
        1: 'mobile',
        2: 'phone',
        3: 'fax'
    }

    def __init__(self, lines: Dict[int, str], country_code: str = None):
        self._country_code: str = country_code
        self._lines: Dict[int, str] = lines
        self._extracted: List[Dict[str, Any]] = self._extract()

        print(lines)

    def _extract(self) -> List[Dict[str, Any]]:
        extracted: List[Dict[str, Any]] = []

        for line_index, line in self.lines.items():
            for match in PhoneNumberMatcher(line, self.country_code):
                phone_number_type: int = number_type(match.number)
                print(match.raw_string)

                if 'fax' in re.search(r'[^\d]*?' + match.raw_string.replace('+', '\+'), line).group(0).lower():
                    phone_number_type = 3

                extracted.append({
                    'type': self.type_mappings[phone_number_type] if phone_number_type in self.type_mappings else self.type_mappings[0],
                    'match': format_number(match.number, PhoneNumberFormat.E164),
                    'index': line_index
                })

        print(f'Phone numbers: {extracted}')

        return extracted

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
    pne = PhoneNumberExtractor({1: 'Telefon: +49 40 500250', 2: 'Telefax: +49 40 50025111', 3: 'Telefon: +49 40 500250, Telefax: +49 40 50025111'}, 'DE')
    print(pne.extracted)
    print(re.sub(r'(?<=\d)\s*(?=\d)', '', 'Telefon: +49 40 500250, Telefax: +49 40 50025111'))
