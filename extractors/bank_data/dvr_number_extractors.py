import re

from typing import Dict

from exceptions.missing_pattern import MissingPatternError
from extractors.extractor_templates import RegExExtractor


class RegExDVRNumberExtractor(RegExExtractor):
    pattern = r'(dvr|DVR).+\n?[0-9]{7}'

    def extract_lines(self, lines: Dict[int, str]) -> Dict[int, str]:
        if not self.pattern:
            raise MissingPatternError()

        matched_lines: Dict[int, str] = {}

        for line_index, line in lines.items():
            if re.findall(self.pattern, line):
                matched_lines[line_index] = line
            elif 'dvr' in line.lower():
                if line_index + 1 in lines:
                    concatenated: str = line + '\n' + lines[line_index + 1]

                    if re.search(self.pattern, concatenated):
                        matched_lines[line_index] = line
                        matched_lines[line_index + 1] = lines[line_index + 1]

        return matched_lines
