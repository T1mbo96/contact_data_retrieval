import json
import os

from typing import List, Dict, Any, Tuple

from contact_data import ContactData


class DataLoader:
    """
    This is a class to load data from the contact data json file in raw and cleansed format.

    Instance variables:
        - path: Path to the contact data json file.
        - raw_data: Raw contact data.
        - cleansed_data: Contact data in cleansed format saved as instances of ContactData.

    Public methods:
        - contact_data: Retrieve contact data object at the specified index.
    """

    def __init__(self, path: str):
        """
        Initialize DataLoader object.

        :raise FileNotFoundError: If file at path doesn't exist.
        :param path: Path to the contact data json file.
        """

        if not os.path.exists(path):
            raise FileNotFoundError(path)

        self._path: str = path
        self._raw_data: List[Dict[str, Any]] = self._load_raw_data()
        self._cleansed_data: List[ContactData] = self._load_cleansed_data()

    def _load_raw_data(self) -> List[Dict[str, Any]]:
        """
        Load data from contact data json file whose path is specified in the class property ``path``.

        :return data: Raw contact data.
        """

        with open(self.path, 'r') as json_file:
            data: List[Dict[str, Any]] = json.load(json_file)

        return data

    def _load_cleansed_data(self) -> List[ContactData]:
        """
        Cleanse raw data from contact data json file to retrieve only the content of the important fields.

        Important Fields:
            - country_code
            - raw_input -> text
            - fixed_input -> text
            - description -> crawledImprint
            - description -> crawledWebsite
            - lineAnnotation
            - expectedContact
            - tokenAnnotation

        :return cleansed_data: Cleansed contact data.
        """

        return [ContactData({'country_code': entry['country_code'], 'raw_input': entry['raw_input']['text'],
                             'fixed_input': entry['fixed_input']['text'],
                             'crawled_imprint': entry['description']['crawledImprint'],
                             'crawled_website': entry['description']['crawledWebsite'],
                             'line_annotations': entry['lineAnnotation'],
                             'expected_contact_data': entry['expectedContact'],
                             'token_annotations': entry['tokenAnnotation']}) for entry in self.raw_data]

    def contact_data(self, index: int):
        """
        Retrieve contact data object at the specified index.

        :params index: Index of the specified contact data.
        :return: Contact data.
        """

        return self.cleansed_data[index]

    def language_counts(self) -> Dict[str, int]:
        """
        Calculate count of contact data objects for each country.

        :return language_counts: Count of contact data objects for each country.
        """

        language_counts: Dict[str, int] = {}

        for data in self.cleansed_data:
            if data.country_code in language_counts:
                language_counts[data.country_code] += 1
            else:
                language_counts[data.country_code] = 1

        return language_counts

    def misleading_training_data(self, languages: Tuple[str, ...]) -> List[Dict[str, Any]]:
        """
        Prepare and retrieve relevant data for training of the binary classifier.

        :params languages: Languages that should be taken into account.
        :return data: Sentences and classifications of the contact data lines.
        """

        data: List[Dict[str, Any]] = []

        for index, contact_data in enumerate(self.cleansed_data):
            if contact_data.line_annotations and contact_data.country_code in languages:
                for line in contact_data.line_annotations:
                    if 'text' in line and 'blockId' in line:
                        data.append({'line': line['text'], 'is_misleading': True if line['isMisleading'] is True else False})

        return data

    def classification_test_data(self, languages: Tuple[str, ...]) -> List[int]:
        data: List[int] = []

        for index, contact_data in enumerate(self.cleansed_data):
            if not contact_data.line_annotations and contact_data.country_code in languages:
                data.append(index)

        return data

    @property
    def path(self) -> str:
        return self._path

    @property
    def raw_data(self) -> List[Dict[str, Any]]:
        return self._raw_data

    @property
    def cleansed_data(self) -> List[ContactData]:
        return self._cleansed_data

    def __str__(self):
        return f'<DataLoader of {self.path}>'


if __name__ == '__main__':
    dl = DataLoader('C:/Users/TimoM/PycharmProjects/contact_data_retrieval/data/imprints_plausible_v2.json')
    print(dl.language_counts())
