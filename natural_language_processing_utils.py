import nltk
import re

from typing import List, Dict, Any, Tuple
from bs4 import BeautifulSoup

from contact_data import ContactData
from data_loader import DataLoader


class NaturalLanguageProcessingUtils:
    """
    This is a class of util functions for natural language processing tasks on the web scraped contact data.

    Instance variables:
        - file: Path of the contact data json file.
        - raw_data: Loaded data from contact data json file in raw format.
        - cleansed_data: Loaded data from contact data json file in cleansed format.

    Public methods:
        - get_actual_value: Retrieve the desired representation of the contact data.
        - prettify_html: Prettify the html content of ``raw_input``.
        - remove_html: Remove the html content of ``raw_input``.
        - remove_blank_lines_from_text: Remove consecutive blank lines from text content of contact data.
    """

    def __init__(self, data_loader: DataLoader):
        """
        Initialize NaturalLanguagePreprocessing object.

        :param data_loader: DataLoader of the contact data json file.
        """

        self._file: str = data_loader.path
        self._raw_data: List[Dict[str, Any]] = data_loader.load_raw_data()
        self._cleansed_data: List[ContactData] = data_loader.load_cleansed_data()

    def contact_data(self, index: int) -> ContactData:
        """
        Retrieve the contact data with the specified index.

        :param index: Index of the specified contact data.
        :return: The contact data.
        """

        return self.cleansed_data[index]

    def prettify_html(self, index: int) -> str:
        """
        Prettify the html content of ``raw_input``.

        :param index: Index of the specified contact data.
        :return: Prettified html content.
        """

        return BeautifulSoup(self.cleansed_data[index].raw_input, 'html.parser').prettify()

    def remove_html(self, index: int) -> str:
        """
        Remove the html content of ``raw_input``. Remove unwanted tags and join the text content of the remaining tags
        joined by a \n.

        :param index: Index of the specified contact data.
        :return: Text content of contact data.
        """

        soup: BeautifulSoup = BeautifulSoup(self.cleansed_data[index].raw_input, 'lxml')

        for tag in soup(['img', 'figure', 'video', 'style', 'script', 'input', 'select', 'i', 'br']):
            tag.decompose()

        # Keep a-tags with mail, tel or url content
        for tag in soup(['a']):
            if 'mailto:' not in tag.decode() and 'tel:' not in tag.decode() and '@' not in tag.decode() and '(at)' not in tag.decode() and not re.search(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))", tag.decode()):
                tag.decompose()

        return '\n'.join(soup.stripped_strings)

    def remove_blank_lines(self, index: int) -> str:
        """
        Remove consecutive blank lines from text content of contact data.

        :param index: Index of the specified contact data.
        :return: Text content of contact data without consecutive blank lines.
        """

        text: str = self.remove_html(index=index)

        return '\n'.join([line for line in text.split('\n') if line.strip() != ''])

    def split_lines(self, index: int) -> List[str]:
        """
        Split text content of contact data at line breaks and at character(.), character(?), character(!).

        :param index: Index of the specified contact data.
        :return: List of split lines of the contact data.
        """

        text: str = self.remove_blank_lines(index=index)

        return text.split('\n')

    def word_tokenization(self, index: int) -> List[Tuple[str, str]]:
        return nltk.word_tokenize(self.remove_html(index))

    @property
    def file(self) -> str:
        return self._file

    @property
    def raw_data(self) -> List[Dict[str, Any]]:
        return self._raw_data

    @property
    def cleansed_data(self) -> List[ContactData]:
        return self._cleansed_data

    def __str__(self):
        return f'<NLP of {self.file}>'


if __name__ == '__main__':
    dl = DataLoader(path='C:/Users/TimoM/PycharmProjects/ner/data/imprints_plausible.json')
    nlp = NaturalLanguageProcessingUtils(data_loader=dl)

    print(nlp.remove_html(3))
