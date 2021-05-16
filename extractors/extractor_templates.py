import re

from typing import Dict

from abstract_classes.contact_data_retrieval_tasks import ContactDataRetrievalTask
from exceptions.missing_pattern import MissingPatternError


class RegExExtractor(ContactDataRetrievalTask):
    pattern = None

    def extract_lines(self, lines: Dict[int, str]) -> Dict[int, str]:
        if not self.pattern:
            raise MissingPatternError()

        matched_lines: Dict[int, str] = {}

        for line_index, line in lines.items():
            if re.findall(self.pattern, line):
                matched_lines[line_index] = line

        return matched_lines
