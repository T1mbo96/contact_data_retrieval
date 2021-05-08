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

        self.__country_code = data['country_code']
        self.__raw_input = data['raw_input']
        self.__fixed_input = data['fixed_input']
        self.__crawled_imprint = data['crawled_imprint']
        self.__crawled_website = data['crawled_website']

    @property
    def country_code(self):
        return self.__country_code

    @property
    def raw_input(self):
        return self.__raw_input

    @property
    def fixed_input(self):
        return self.__fixed_input

    @property
    def crawled_imprint(self):
        return self.__crawled_imprint

    @property
    def crawled_website(self):
        return self.__crawled_website

    def __str__(self):
        return f'<ContactData of {self.crawled_website}>'
