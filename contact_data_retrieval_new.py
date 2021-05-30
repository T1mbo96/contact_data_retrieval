from typing import List, Type

from contact_data import ContactData
from extractors_new.extracting_tasks import ExtractingTask
from pre_processing import PreProcessing


class ContactDataRetrieval(PreProcessing):
    def __init__(self, contact_data: ContactData, pipeline: List[Type[ExtractingTask]]):
        # Initialize superclass
        super().__init__(contact_data=contact_data)

        # Initialize instance variables
        self._contact_data: ContactData = contact_data
        self._pipeline: List[Type[ExtractingTask]] = pipeline

    def __str__(self):
        pass

    def __repr__(self):
        pass

    def _contact_data(self):
        pass

    def _accuracy(self):
        pass
