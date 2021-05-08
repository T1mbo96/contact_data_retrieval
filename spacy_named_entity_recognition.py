import re
import spacy
import tldextract

from typing import List, Tuple, Set, Dict
from spacy.tokens.doc import Doc
from spacy.matcher import Matcher
from itertools import chain

from data_loader import DataLoader
from natural_language_processing_utils import NaturalLanguageProcessingUtils

# Spacy models
NLP_GERMAN = spacy.load('de_core_news_lg')
NLP_ENGLISH = spacy.load('en_core_web_lg')
NLP_DUTCH = spacy.load('nl_core_news_lg')
# NLP_ITALIAN = spacy.load('it_core_news_lg')
# NLP_FRENCH = spacy.load('fr_core_news_lg')
# NLP_ROMANIAN = spacy.load('ro_core_news_lg')
# NLP_CHINESE = spacy.load('zh_core_web_lg')
# NLP_DANISH = spacy.load('da_core_news_lg')
# NLP_POLISH = spacy.load('pl_core_news_lg')
# NLP_NORWEGIAN = spacy.load('nb_core_news_lg')
# NLP_SPANISH = spacy.load('es_core_news_lg')
# NLP_MULTILINGUAL = spacy.load('xx_ent_wiki_sm')

# Spacy models for country codes
# NL = (NLP_ENGLISH, NLP_DUTCH)
# IT = (NLP_ENGLISH, NLP_ITALIAN)
# SE = (NLP_ENGLISH,)
# AU = (NLP_ENGLISH,)
# TR = (NLP_ENGLISH,)
# CH = (NLP_ENGLISH, NLP_ITALIAN, NLP_GERMAN, NLP_FRENCH)
# US = (NLP_ENGLISH,)
# RO = (NLP_ENGLISH, NLP_ROMANIAN)
# IE = (NLP_ENGLISH,)
# FR = (NLP_ENGLISH, NLP_FRENCH)
DE = {'models': (NLP_ENGLISH, NLP_GERMAN),
      'regex_patterns': {
          'phone': r'(\(?([\d \-\)\–\+\/\(]+)\)?([ .\-–\/]?)([\d]+))',
          'mail': r'"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$"',
          'url': r'(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)'
      },
      'terms_to_keep': {
          'bank_data': ['IBAN', 'SWIFT', 'BIC', 'Bank'],
          'company_data': ['Firm', 'Buchnummer', 'Gericht', 'UID', 'DVR', 'Umsatzsteuer', 'Regist',
                           'Mehrwertsteuer', 'UST'],
          'manager_data': ['Geschäftsführ', 'Inhab', 'Verwalt', 'Vorsitz', 'Mitglied', 'Vertret', 'Präsid', 'Aufsicht']
      },
      'terms_to_delete': ['Support', 'Menü']
      }

AT = {'models': (NLP_ENGLISH, NLP_GERMAN),
      'regex_patterns':
          {
              'phone': r'\+?[0-9]+([0-9]|\/|\(|\)|\-| ){6,}',
              'mail': r'[a-zA-Z0-9+_.-]+(@|\(at\))[a-zA-Z0-9.-]+',
              'url': r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
          },
      'terms_to_keep':
          {
              'bank_data':
                  {
                      'standalone': ['iban', 'swift', 'bic'],
                      'wherever': ['bank', 'konto']
                  },
              'company_data':
                  {
                      'standalone': ['uid', 'dvr', 'ust', 'atu', 'fn', 'mwst', 'nr'],
                      'wherever': ['firm', 'buchnummer', 'gericht', 'umsatzsteuer', 'register', 'mehrwertsteuernummer']
                  },
              'manager_data':
                  {
                      'standalone': [],
                      'wherever': ['geschäftsführ', 'inhab', 'verwalt', 'vorsitz', 'vertreten', 'vertreter',
                                   'vertretung', 'präsid',
                                   'aufsicht']
                  }
          },
      'terms_to_avoid': ['datenbank', 'firma']
      }


# CN = (NLP_ENGLISH, NLP_CHINESE)
# DK = (NLP_ENGLISH, NLP_DANISH)
# BE = (NLP_ENGLISH, NLP_DUTCH, NLP_GERMAN, NLP_FRENCH)
# GB = (NLP_ENGLISH,)
# PL = (NLP_ENGLISH, NLP_POLISH)
# NO = (NLP_ENGLISH, NLP_NORWEGIAN)
# ES = (NLP_ENGLISH, NLP_SPANISH)


class SpacyContactDataRetrieval(NaturalLanguageProcessingUtils):
    def __init__(self, data_loader: DataLoader):
        # Initialize superclass
        super().__init__(data_loader=data_loader)

        # Initialize matcher
        self.__matcher_german = Matcher(self.nlp_german.vocab)
        self.__matcher_english = Matcher(self.nlp_english.vocab)

    def preprocess_text_lines(self, index: int) -> Tuple[str, Dict[int, str]]:
        # Split text in lines, replace unicode character for space with an actual space, remove duplicate lines
        lines: Dict[int, str] = {index: line.replace(u'\xa0', u' ') for index, line in
                                 enumerate(self.split_lines(index=index))}

        return self.get_country_code(index=index), lines

    def match_terms(self, country_code: str, lines: Dict[int, str]) -> Tuple[Dict[str, Dict[int, str]], Dict[int, str]]:
        terms_to_keep = globals()[country_code]['terms_to_keep']
        matched_terms: Dict[str, Dict[int, str]] = {'bank_data': {}, 'company_data': {}, 'manager_data': {}}
        add_next: Dict[int, str] = {}

        for domain, terms in terms_to_keep.items():
            for term in terms['standalone']:
                for line_index, line in lines.items():
                    if term in line.lower():
                        if self.is_standalone(term, line.lower()):
                            clean: List[str] = list(filter(None, line.split(' ')))

                            if clean[len(clean) - 1][-1] == ':' or clean[len(clean) - 1][-1] == ',':
                                if line_index not in add_next:
                                    add_next[line_index] = domain

                            matched_terms[domain][line_index] = line

            for term in terms['wherever']:
                for line_index, line in lines.items():
                    if term in line.lower():
                        clean: List[str] = list(filter(None, line.split(' ')))

                        if clean[len(clean) - 1][-1] == ':' or clean[len(clean) - 1][-1] == ',':
                            if line_index not in add_next:
                                add_next[line_index] = domain

                        matched_terms[domain][line_index] = line

            # Remove matched lines
            for matched_index in matched_terms[domain].keys():
                if matched_index in lines:
                    del lines[matched_index]

        # Remove duplicates
        matched_terms = self.remove_duplicates(data=matched_terms)

        # Add next line
        for line_index, domain in add_next.items():
            if line_index + 1 not in add_next:
                if line_index + 1 in lines:
                    matched_terms[domain][line_index + 1] = lines[line_index + 1]

        # Remove matched lines
        for domain, matched_lines in matched_terms.items():
            for line_index in matched_lines.keys():
                if line_index in lines:
                    del lines[line_index]

        return matched_terms, lines

    def match_location(self):
        pass

    def match_patterns(self, index: int, country_code: str, lines: Dict[int, str]) -> Tuple[Dict[str, Dict[int, str]], Dict[int, str]]:
        patterns = globals()[country_code]['regex_patterns']
        matched_patterns: Dict[str, Dict[int, str]] = {'phone': {}, 'mail': {}, 'url': {}}

        for line_index, line in lines.items():
            for domain, pattern in patterns.items():
                if re.search(pattern, line):
                    matched_patterns[domain][line_index] = line

        matched_patterns['url'] = self.postprocess_urls(index=index, country_code=country_code,
                                                        urls=matched_patterns['url'])

        matched_patterns = self.remove_duplicates(data=matched_patterns)

        for domain, matched_lines in matched_patterns.items():
            for line_index in matched_lines.keys():
                if line_index in lines:
                    del lines[line_index]

        return matched_patterns, lines

    def postprocess_urls(self, index: int, country_code: str, urls: Dict[int, str]) -> Dict[int, str]:
        url_pattern = globals()[country_code]['regex_patterns']['url']
        remove: List[int] = []
        domain: str = tldextract.extract(self.get_crawled_website(index=index)).domain

        # Remove anything that's not part of the url
        for line_index, url in urls.items():
            urls[line_index] = ''.join(list(chain.from_iterable(re.findall(url_pattern, url))))

        # Remove any non related url
        for line_index, url in urls.items():
            if domain != tldextract.extract(url).domain:
                remove.append(line_index)

        for line_index in remove:
            del urls[line_index]

        return urls

    def is_standalone(self, term: str, line: str) -> bool:
        if line.find(term) == 0:
            return True

        if self.is_number(line[line.index(term) - 1]) or self.is_valid_special_character(line[line.index(term) - 1]):
            return True

        if self.is_number(line[line.index(term) + len(term)]) or self.is_valid_special_character(
                line[line.index(term) + len(term)]):
            return True

        return False

    def is_number(self, character: str):
        try:
            num = float(character)
            # check for "nan" floats
            return num == num  # or use `math.isnan(num)`
        except ValueError:
            return False

    def is_valid_special_character(self, character: str):
        valid_special_characters: str = '-: /\\.'

        return character in valid_special_characters

    def remove_duplicates(self, data: Dict[str, Dict[int, str]]) -> Dict[str, Dict[int, str]]:
        for domain, matched_lines in data.items():
            remove: List[int] = []

            # Remove exact duplicate lines
            temp = {val: key for key, val in matched_lines.items()}
            unique = {val: key for key, val in temp.items()}

            for line_index in remove:
                del unique[line_index]

            data[domain] = unique

        return data

    def pipeline(self, index: int):
        # Preprocess lines
        country_code, lines = self.preprocess_text_lines(index=index)

        # Match terms
        terms_matched, terms_lines = self.match_terms(country_code=country_code, lines=lines)

        # Match patterns
        patterns_matched, patterns_lines = self.match_patterns(index=index, country_code=country_code,
                                                               lines=terms_lines)

        self.output(bank_data=terms_matched['bank_data'], company_data=terms_matched['company_data'],
                    manager_data=terms_matched['manager_data'], phone=patterns_matched['phone'],
                    mail=patterns_matched['mail'], url=patterns_matched['url'])

    def output(self, organisation=None, location=None, bank_data: Dict[int, str] = None,
               company_data: Dict[int, str] = None, manager_data: Dict[int, str] = None, phone: Dict[int, str] = None,
               mail: Dict[int, str] = None, url: Dict[int, str] = None):
        if organisation:
            print(f'Company name: {organisation}', end='\n\n')

        if location:
            print('Location:')

            for data in location.values():
                print(data)

            print()

        if bank_data:
            print('Bank data:')

            for data in self.sort_dictionary_data(key=True, data=bank_data):
                print(data[1])

            print()

        if company_data:
            print('Company data:')

            for data in self.sort_dictionary_data(key=True, data=company_data):
                print(data[1])

            print()

        if manager_data:
            print('Manager data:')

            for data in self.sort_dictionary_data(key=True, data=manager_data):
                print(data[1])

            print()

        if phone:
            print('Phone data:')

            for data in self.sort_dictionary_data(key=True, data=phone):
                print(data[1])

            print()

        if mail:
            print('Mail data:')

            for data in self.sort_dictionary_data(key=True, data=mail):
                print(data[1])

            print()

        if url:
            print('URL data:')

            for data in self.sort_dictionary_data(key=True, data=url):
                print(data[1])

            print()

    def sort_dictionary_data(self, key: bool, data: Dict[int, str]) -> List[Tuple[int, str]]:
        return sorted(data.items(), key=lambda x: x[int(not key)])

    @property
    def nlp_german(self):
        return NLP_GERMAN

    @property
    def nlp_english(self):
        return NLP_ENGLISH


if __name__ == '__main__':
    dl = DataLoader('C:/Users/TimoM/PycharmProjects/ner/data/imprints_plausible.json')
    spacy_ner = SpacyContactDataRetrieval(data_loader=dl)
    # TODO: index 13 matched too much
    # TODO: index 14 filter out google, facebook, etc. urls
    spacy_ner.pipeline(index=18)
