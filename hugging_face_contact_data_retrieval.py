from tabulate import tabulate

from data_loader import DataLoader
from natural_language_processing_utils import NaturalLanguageProcessingUtils
from transformers import pipeline


class HuggingFaceContactDataRetrieval(NaturalLanguageProcessingUtils):
    def __init__(self, data_loader: DataLoader):
        super().__init__(data_loader=data_loader)

    def named_entity_recognition(self, index: int):
        text: str = self.remove_blank_lines_from_text(index=index)
        ner = pipeline('ner')

        return ner(text)


if __name__ == '__main__':
    dl = DataLoader(path='C:/Users/TimoM/PycharmProjects/ner/data/imprints_plausible.json')
    hfcdr = HuggingFaceContactDataRetrieval(data_loader=dl)

    #print(hfcdr.named_entity_recognition(index=10))

    print(tabulate([element.values() for element in hfcdr.named_entity_recognition(index=10)], headers=['Entity Group', 'Score', 'Word', 'Start', 'End']))
