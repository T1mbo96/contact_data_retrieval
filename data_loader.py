import json
import os

from typing import List, Dict, Any

from contact_data import ContactData


class DataLoader:
    """
    This is a class to load data from the contact data json file in raw or cleansed format.

    Instance variables:
        - path: Path to the contact data json file.

    Public methods:
        - load_raw_data: Load data from contact data json file whose path is specified in the class property ``path``.
        - load_cleansed_data: Cleanse raw data from contact data json file to retrieve only the content of the important fields.
    """

    def __init__(self, path: str):
        """
        Initialize DataLoader object.

        :raise FileNotFoundError: If file at ``path`` doesn't exist.
        :param path: Path to the contact data json file.
        """

        if not os.path.exists(path):
            raise FileNotFoundError(path)

        self.__path: str = path

    def load_raw_data(self) -> List[Dict[str, Any]]:
        """
        Load data from contact data json file whose path is specified in the class property ``path``.

        :return data: Raw contact data.
        """

        with open(self.path, 'r') as json_file:
            data: List[Dict[str, Any]] = json.load(json_file)

        return data

    def load_cleansed_data(self) -> List[ContactData]:
        """
        Cleanse raw data from contact data json file to retrieve only the content of the important fields.

        Important Fields:
            - country_code
            - raw_input -> text
            - fixed_input -> text
            - description -> crawledImprint
            - description -> crawledWebsite

        :return cleansed_data: Cleansed contact data.
        """

        data: List[Dict[str, Any]] = self.load_raw_data()

        cleansed_data: List[ContactData] = [ContactData(
            {'country_code': entry['country_code'], 'raw_input': entry['raw_input']['text'],
             'fixed_input': entry['fixed_input']['text'], 'crawled_imprint': entry['description']['crawledImprint'],
             'crawled_website': entry['description']['crawledWebsite']}) for entry in data]

        return cleansed_data

    @property
    def path(self) -> str:
        return self.__path

    def __str__(self):
        return f'<DataLoader of {self.path}>'
