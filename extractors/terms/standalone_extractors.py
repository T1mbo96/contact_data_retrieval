from typing import Dict, List

from abstract_classes.contact_data_retrieval_tasks import TermsContactDataRetrievalTask
from extractors.terms.utils import is_standalone, contains_complete_content


class StandaloneExtractor(TermsContactDataRetrievalTask):
    def __init__(self, terms: List[str]):
        self._terms: List[str] = terms

    def extract_lines(self, lines: Dict[int, str]) -> Dict[int, str]:
        matched_lines: Dict[int, str] = {}
        add_next_line: List[int] = []

        for term in self.terms:
            for line_index, line in lines.items():
                if term in line.lower():
                    if is_standalone(term, line.lower()):
                        if not contains_complete_content(line=line):
                            if line_index not in add_next_line:
                                add_next_line.append(line_index)

                        matched_lines[line_index] = line

        # Add next line
        for line_index in add_next_line:
            if line_index + 1 not in add_next_line:
                if line_index + 1 in lines:
                    matched_lines[line_index + 1] = lines[line_index + 1]

        return matched_lines

    @property
    def terms(self):
        return self._terms
