from typing import Dict


class ContactData:
    """
    This is a class to save the contact data of website.

    Instance variables:
        - country_code: Code of the country.
        - raw_input: Scraped html content.
        - fixed_input: Desired content of the scraped html.
        - crawled_imprint: The imprint that provides the raw_input.
        - crawled_website: The website to which the imprint belongs.
    """

    def __init__(self, data: Dict[str, str]):
        """
        Initialize ContactData object.

        :param data: Dictionary of the loaded contact data for a website.
        """

        self._country_code = data['country_code']
        self._raw_input = data['raw_input']
        self._fixed_input = data['fixed_input']
        self._crawled_imprint = data['crawled_imprint']
        self._crawled_website = data['crawled_website']

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

    def __str__(self):
        return f'<ContactData of {self.crawled_website}>'
