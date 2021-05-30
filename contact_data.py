from typing import Dict, List, Any


class ContactData:
    """
    This is a class to save the contact data of website.

    Instance variables:
        - country_code: Code of the country.
        - raw_input: Scraped html content.
        - fixed_input: Desired lines of the scraped html.
        - crawled_imprint: The imprint that provides the raw_input.
        - crawled_website: The website to which the imprint belongs.
        - line_annotation: Every line with annotations.
        -
    """

    def __init__(self, data: Dict[str, Any]):
        """
        Initialize ContactData object.

        :param data: Dictionary of the loaded contact data for a website.
        """

        self._country_code: str = data['country_code']
        self._raw_input: str = data['raw_input']
        self._fixed_input: str = data['fixed_input']
        self._crawled_imprint: str = data['crawled_imprint']
        self._crawled_website: str = data['crawled_website']
        self._line_annotations: List[Dict[str, Any]] = data['line_annotations']
        self._expected_contact_data: Dict[str, Any] = data['expected_contact_data']
        self._token_annotations: List[Dict[str, str]] = data['token_annotations']

    @property
    def country_code(self):
        return self._country_code

    @property
    def raw_input(self):
        return self._raw_input

    @property
    def fixed_input(self):
        return self._fixed_input

    @property
    def crawled_imprint(self):
        return self._crawled_imprint

    @property
    def crawled_website(self):
        return self._crawled_website

    @property
    def line_annotations(self):
        return self._line_annotations

    @property
    def expected_contact_data(self):
        return self._expected_contact_data

    @property
    def token_annotations(self):
        return self._token_annotations

    def __str__(self):
        return f'<ContactData of {self.crawled_website}>'
