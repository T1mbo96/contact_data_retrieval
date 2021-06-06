import re

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class ExtractingTask(ABC):
    @property
    @abstractmethod
    def extracted(self) -> List[Dict[str, Any]]:
        """
        Returns the extracted matches from all lines.

        :returns: The matches.
        """

        raise NotImplementedError('This method must be implemented!')


class RegExExtractingTask(ExtractingTask):
    pattern = None
    type = None

    def __init__(self, lines: Dict[int, str]):
        self._lines: Dict[int, str] = lines
        self._extracted: List[Dict[str, Any]] = self._extract()

    def _extract(self):
        if self.pattern is None:
            raise TypeError('No pattern specified!')

        extracted: List[Dict[str, Any]] = []

        for line_index, line in self.lines.items():
            matches: List[str] = re.findall(self.pattern, line)

            for match in matches:
                extracted.append({
                    'type': self.type,
                    'match': match,
                    'index': line_index
                })

        return extracted

    @property
    def lines(self) -> Dict[int, str]:
        return self._lines

    @property
    def extracted(self) -> List[Dict[str, Any]]:
        return self._extracted


class NERExtractingTask(ExtractingTask):
    model = None
    tokenizer = None

    def __init__(self, lines: Dict[int, str]):
        self._lines: Dict[int, str] = lines
        self._extracted: List[Dict[str, Any]] = self._extract()

    @abstractmethod
    def _extract(self):
        raise NotImplementedError('This method must be implemented!')

    @property
    def lines(self):
        return self._lines

    @property
    def extracted(self) -> List[Dict[str, Any]]:
        return self._extracted
