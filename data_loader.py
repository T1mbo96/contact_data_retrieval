import json
import os

from typing import List, Dict, Any

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

    def contact_data(self, index: int):
        """
        Retrieve contact data object at the specified index.

        :params index: Index of the specified contact data.
        :return: Contact data.
        """

        return self.cleansed_data[index]

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

        :return cleansed_data: Cleansed contact data.
        """

        return [ContactData({'country_code': entry['country_code'], 'raw_input': entry['raw_input']['text'],
                             'fixed_input': entry['fixed_input']['text'],
                             'crawled_imprint': entry['description']['crawledImprint'],
                             'crawled_website': entry['description']['crawledWebsite']}) for entry in self.raw_data]

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
