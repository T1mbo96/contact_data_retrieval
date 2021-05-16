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
        - contact_data: The contact data object.

    Public methods:
        - prettify_html: Prettify the html content of raw_input.
        - remove_html: Remove the html content of raw_input.
        - remove_blank_lines: Remove consecutive blank lines from text content of contact data.
    """

    def __init__(self, contact_data: ContactData):
        """
        Initialize NaturalLanguagePreprocessingUtils object.

        :param contact_data: The contact data object.
        """

        self._contact_data: ContactData = contact_data

    def prettify_html(self) -> str:
        """
        Prettify the html content of raw_input.

        :return: Prettified html content.
        """

        return BeautifulSoup(self.contact_data.raw_input, 'html.parser').prettify()

    def remove_html(self) -> str:
        """
        Remove the html content of raw_input. Remove unwanted tags and join the text content of the remaining tags joined by a \n.

        :return: Text content of contact data.
        """

        soup: BeautifulSoup = BeautifulSoup(self.contact_data.raw_input, 'lxml')

        for tag in soup(['img', 'figure', 'video', 'style', 'script', 'input', 'select', 'i', 'br']):
            tag.decompose()

        # Keep a-tags with mail, tel or url content
        for tag in soup(['a']):
            if 'mailto:' not in tag.decode() and 'tel:' not in tag.decode() and '@' not in tag.decode() and '(at)' not in tag.decode() and not re.search(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))", tag.decode()):
                tag.decompose()

        return '\n'.join(soup.stripped_strings)

    def remove_blank_lines(self) -> str:
        """
        Remove consecutive blank lines from text content of contact data.

        :return: Text content of contact data without consecutive blank lines.
        """

        return '\n'.join([line for line in self.remove_html().split('\n') if line.strip() != ''])

    def split_lines(self) -> List[str]:
        """
        Split text content of contact data at line breaks.

        :return: List of split lines of the contact data.
        """

        return self.remove_blank_lines().split('\n')

    @property
    def contact_data(self):
        return self._contact_data

    def __str__(self):
        return f'<NLP of {self.contact_data}>'


if __name__ == '__main__':
    dl = DataLoader(path='C:/Users/TimoM/PycharmProjects/ner/data/imprints_plausible.json')
    nlp = NaturalLanguageProcessingUtils(data_loader=dl)

    print(nlp.remove_html(3))
