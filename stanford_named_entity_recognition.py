import os

from data_loader import DataLoader
from natural_language_processing_utils import NaturalLanguageProcessingUtils
from nltk.tag.stanford import StanfordNERTagger

# Settings for java
java_path = 'C:/Program Files (x86)/Java/jre1.8.0_291/bin/java.exe'
os.environ['JAVAHOME'] = java_path

# Settings for stanford ner
PATH_TO_JAR = 'stanford_ner_tagger/stanford-ner-4.2.0.jar'
PATH_TO_MODEL = 'stanford_ner_german/stanford-corenlp-4.2.0-models-german.jar'


class StanfordNamedEntityRecognition(NaturalLanguageProcessingUtils):
    def __init__(self, data_loader: DataLoader):
        super().__init__(data_loader=data_loader)
        self.__tagger: StanfordNERTagger = StanfordNERTagger(model_filename=PATH_TO_MODEL, path_to_jar=PATH_TO_JAR, encoding='utf-8')

    def tag_imprint(self, index: int):
        return self.tagger.tag(tokens=self.word_tokenization(index=index))

    @property
    def tagger(self):
        return self.__tagger


if __name__ == '__main__':
    dl = DataLoader('C:/Users/TimoM/PycharmProjects/ner/data/imprints_plausible.json')
    stanford_ner = StanfordNamedEntityRecognition(data_loader=dl)
    print(stanford_ner.tag_imprint(index=2))
