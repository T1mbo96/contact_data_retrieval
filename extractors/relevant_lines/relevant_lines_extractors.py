from typing import Dict, List, Set

import fasttext

from abstract_classes.pre_processing_tasks import PreProcessingTask
from extractors.extractor_templates import MLPVectorizationExtractor


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


class TFIDFLogisticRegressionExtractor(MLPVectorizationExtractor):
    classifier_path = 'C:/Users/TimoM/PycharmProjects/contact_data_retrieval/classifiers/2021-05-28/LogisticRegression(max_iter=1000)_0.9845263157894737.pkl'
    vectorizer_path = 'C:/Users/TimoM/PycharmProjects/contact_data_retrieval/vectorizers/2021-05-28/tf_idf.pkl'


class FasttextExtractor(PreProcessingTask):
    path = 'C:/Users/TimoM/PycharmProjects/contact_data_retrieval/classifiers/2021-05-28/fasttext/(28500, 0.9856842105263158, 0.9856842105263158).bin'

    def __init__(self, lines: Dict[int, str]):
        self._lines: Dict[int, str] = lines

    def extract_relevant_lines(self) -> Dict[int, str]:
        relevant_lines: Dict[int, str] = {}
        classifier = fasttext.load_model(self.path)

        for line_index, line in self.lines.items():
            print(classifier.predict(line))
            if classifier.predict(line)[0][0] == '__label__relevant':
                relevant_lines[line_index] = line

        return relevant_lines

    @property
    def lines(self):
        return self._lines


if __name__ == '__main__':
    FasttextExtractor({0: 'Demenz'}).extract_relevant_lines()
