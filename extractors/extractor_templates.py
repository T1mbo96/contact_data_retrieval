import re
import pickle
import pandas as pd

from typing import Dict, List

from abstract_classes.contact_data_retrieval_tasks import ContactDataRetrievalTask
from abstract_classes.pre_processing_tasks import PreProcessingTask
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


class MLPVectorizationExtractor(PreProcessingTask):
    classifier_path = None
    vectorizer_path = None

    def __init__(self, lines: Dict[int, str]):
        self._lines: Dict[int, str] = lines

    def _prepare_line(self, line: str) -> pd.DataFrame:
        df: pd.DataFrame = pd.DataFrame([line], columns=['line'])

        # TODO: Check if paths are set and then continue or skip

        with open(self.vectorizer_path, 'rb') as file:
            vectorizer = pickle.load(file)
            vector = vectorizer.transform(df['line'])

        return vector

    def extract_relevant_lines(self) -> Dict[int, str]:
        relevant_lines: Dict[int, str] = {}

        with open(self.classifier_path, 'rb') as file:
            classifier = pickle.load(file)

        for line_index, line in self.lines.items():
            vector = self._prepare_line(line=line)
            print(classifier.predict(vector))
            if classifier.predict(vector) == [1]:
                relevant_lines[line_index] = line

        return relevant_lines

    @property
    def lines(self):
        return self._lines


if __name__ == '__main__':
    pass
