from abc import ABC, abstractmethod
from typing import Dict, List


class ContactDataRetrievalTask(ABC):
    """
    Abstract class for tasks for the contact data retrieval pipeline.
    """

    @abstractmethod
    def extract_lines(self, lines: Dict[int, str]) -> Dict[int, str]:
        """
        Extract specific lines from a given dictionary with an arbitrary number of lines.

        :param lines: Arbitrary number of lines
        :returns: Extracted lines.
        """

        raise NotImplementedError('This method must be implemented!')


class CountrySpecificContactDataRetrievalTask(ContactDataRetrievalTask):
    @abstractmethod
    def __init__(self, country_code: str):
        """
        Instantiates an object of the class deriving from this abstract class.

        :param country_code: Country code of the specific contact data.
        """

        raise NotImplementedError('This method must be implemented')


class TermsContactDataRetrievalTask(ContactDataRetrievalTask):
    @abstractmethod
    def __init__(self, terms: List[str]):
        """
        Instantiates an object of the class deriving from this abstract class.

        :param terms: Terms to match.
        """

        raise NotImplementedError('This method must be implemented')


class NamedEntityRecognitionContactDataRetrievalTask(ContactDataRetrievalTask):
    @abstractmethod
    def __init__(self, model: str, tokenizer: str):
        """
        Instantiates an object of the class deriving from this abstract class.

        :param model: Name of the model.
        :param tokenizer: Name of the tokenizer.
        """

        raise NotImplementedError('This method must be implemented')
