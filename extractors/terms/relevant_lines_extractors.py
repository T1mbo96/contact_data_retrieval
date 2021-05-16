from typing import Dict, List, Set

from abstract_classes.pre_processing_tasks import PreProcessingTask


class DictionaryRelevantLinesExtractor(PreProcessingTask):
    def __init__(self, terms: List[str], lines: Dict[int, str]):
        self._terms: List[str] = terms
        self._lines: Dict[int, str] = lines

    def extract_relevant_lines(self) -> Dict[int, str]:
        # Remove lines related to Social Networks
        lines = {index: line for index, line in self.lines.items() if
                 'google' not in line.lower() and 'facebook' not in line.lower() and 'twitter' not in line.lower() and 'instagram' not in line.lower()}

        # Remove lines with content for cookies
        lines = {index: line for index, line in lines.items() if 'cookie' not in line.lower()}

        # Remove irrelevant country specific terms
        remove: Set[int] = set()

        for line_index, line in lines.items():
            for term in self.terms:
                if term in line.lower():
                    remove.add(line_index)

        for line_index in remove:
            del lines[line_index]

        return lines

    @property
    def terms(self):
        return self._terms

    @property
    def lines(self):
        return self._lines
