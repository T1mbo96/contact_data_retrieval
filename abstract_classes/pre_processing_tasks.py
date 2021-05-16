from abc import ABC, abstractmethod
from typing import Dict, List


class PreProcessingTask(ABC):
    """
    Abstract class for pre-processing tasks for the contact data retrieval pipeline.
    """

    @abstractmethod
    def __init__(self, terms: List[str], lines: Dict[int, str]):
        """
        Instantiates an object of the class deriving from this abstract class.

        :param terms: Terms that should be avoided.
        :param lines: Lines of the contact data.
        """

        raise NotImplementedError('This method must be implemented')

    @abstractmethod
    def extract_relevant_lines(self) -> Dict[int, str]:
        """
        Extracts only relevant lines for the contact data retrieval task.

        :returns: Relevant lines.
        """

        raise NotImplementedError('This method must be implemented!')