import re
import tldextract

from typing import Dict, Set, Tuple
from abc import ABC, abstractmethod
from itertools import chain


class URLExtractor(ABC):
    @abstractmethod
    def extract_lines(self, lines: Dict[int, str]) -> Dict[int, str]:
        pass


class RegExURLExtractor:
    def __init__(self, domain: str, pattern: str):
        self._domain: str = domain
        self._pattern: str = pattern

    def extract_lines(self, lines: Dict[int, str]) -> Dict[int, str]:
        url_lines: Dict[int, str] = {}
        #remove: Set[int] = set()

        for line_index, line in lines.items():
            url = re.findall(self.pattern, line)
            if url:
                raw_url = ''.join(list(chain.from_iterable(url)))

                if self.domain == tldextract.extract(raw_url).domain:
                    url_lines[line_index] = line
                #else:
                    #remove.add(line_index)

        # Remove lines with matched urls that are irrelevant
        #for line_index in remove:
        #    del lines[line_index]

        #return url_lines, lines
        return url_lines

    @property
    def domain(self):
        return self._domain

    @property
    def pattern(self):
        return self._pattern
