from typing import Dict, List, Set, Type, Any

from abstract_classes.pre_processing_tasks import PreProcessingTask
from contact_data import ContactData
from data_loader import DataLoader
from extractors.terms.arbitrary_position_extractors import ArbitraryPositionExtractor
from extractors.terms.standalone_extractors import StandaloneExtractor
from natural_language_processing_utils import NaturalLanguageProcessingUtils
from language_settings import PIPELINES, DICTIONARIES
from abstract_classes.contact_data_retrieval_tasks import ContactDataRetrievalTask, \
    CountrySpecificContactDataRetrievalTask, NamedEntityRecognitionContactDataRetrievalTask


class ContactDataRetrieval(NaturalLanguageProcessingUtils):
    def __init__(self, contact_data: ContactData, pipeline: List[Type[ContactDataRetrievalTask]] = None):
        # Initialize superclass
        super().__init__(contact_data=contact_data)

        # Initialize extractors
        self._pipeline: List[Type[ContactDataRetrievalTask]] = pipeline if pipeline else PIPELINES[self.contact_data.country_code]

    def output(self):
        # TODO: Post-processing false positive organisations and their contact data (index=3 e.g.)
        # TODO: Post-processing location relate to country code

        for line in sorted(self._extract_contact_data().items()):
            print(line[1])

    def _extract_contact_data(self) -> Dict[int, str]:
        matched_lines: Dict[int, str] = {}
        settings: Dict[str, Any] = DICTIONARIES[self.contact_data.country_code]
        lines: Dict[int, str] = {index: line.replace(u'\xa0', u' ') for index, line in enumerate(self.split_lines())}

        for task in self.pipeline:
            if issubclass(task, PreProcessingTask):
                extractor: PreProcessingTask = task(terms=settings['avoid'], lines=lines)

                lines = extractor.extract_relevant_lines()
            else:
                if issubclass(task, CountrySpecificContactDataRetrievalTask):
                    extractor: ContactDataRetrievalTask = task(country_code=self.contact_data.country_code)
                elif issubclass(task, StandaloneExtractor):
                    extractor: ContactDataRetrievalTask = task(terms=settings['match']['standalone'])
                elif issubclass(task, ArbitraryPositionExtractor):
                    extractor: ContactDataRetrievalTask = task(terms=settings['match']['arbitrary_position'])
                elif issubclass(task, NamedEntityRecognitionContactDataRetrievalTask):
                    extractor: ContactDataRetrievalTask = task(model=settings['named_entity_recognition']['model'], tokenizer=settings['named_entity_recognition']['tokenizer'])
                else:
                    extractor: ContactDataRetrievalTask = task()

                extracted_lines: Dict[int, str] = extractor.extract_lines(lines)
                lines = self._clean_up_lines(lines=lines, extracted_lines=extracted_lines)
                extracted_lines = self._remove_duplicate_lines(extracted_lines=extracted_lines)
                matched_lines.update(extracted_lines)

        return matched_lines

    def _clean_up_lines(self, lines: Dict[int, str], extracted_lines: Dict[int, str]):
        for line_index, line in extracted_lines.items():
            del lines[line_index]

        return lines

    def _remove_duplicate_lines(self, extracted_lines: Dict[int, str]) -> Dict[int, str]:
        temp = {val: key for key, val in extracted_lines.items()}
        unique = {val: key for key, val in temp.items()}

        return unique

    @property
    def pipeline(self):
        return self._pipeline


if __name__ == '__main__':
    dl = DataLoader('C:/Users/TimoM/PycharmProjects/ner/data/imprints_plausible.json')
    cdr = ContactDataRetrieval(contact_data=dl.contact_data(index=0))
    cdr.output()

    # TODO: Compare Swift to database
    # response = requests.get('http://www.swiftcodelist.com/search.php', params={'q': 'BFKKAT2KKLA', 'submit': 'Search'})
    # bs = BeautifulSoup(response.content, 'html.parser')
    # print(bs.prettify())
    # table = bs.find(lambda tag: tag.name == 'table' and tag.has_attr('class') and tag['class'] == 'pro magt10')
    # rows = table.find_all(lambda tag: tag.name == 'tr')
    # print(rows)
    # print(len(rows))
