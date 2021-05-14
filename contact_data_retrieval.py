import re
import tldextract
import requests

from typing import Dict, Tuple, List, Set
from itertools import chain
from transformers import TokenClassificationPipeline
from bs4 import BeautifulSoup

from data_loader import DataLoader
from natural_language_processing_utils import NaturalLanguageProcessingUtils
from language_settings import UNIVERSAL, COUNTRY_SPECIFIC
from phone_number_extractor import PhoneNumberExtractor, LibPhoneNumberExtractor
from mail_address_extractor import MailAddressExtractor, RegExMailAddressExtractor
from url_extractor import URLExtractor, RegExURLExtractor


class ContactDataRetrieval(NaturalLanguageProcessingUtils):
    def __init__(self, data_loader: DataLoader, phone_number_extractor: PhoneNumberExtractor = None, mail_address_extractor: MailAddressExtractor = None, url_extractor: URLExtractor = None):
        # Initialize superclass
        super().__init__(data_loader=data_loader)

        # Initialize extractors
        # self._phone_number_extractor: PhoneNumberExtractor = phone_number_extractor
        # self._mail_address_extractor: MailAddressExtractor = mail_address_extractor
        # self._url_extractor: URLExtractor = url_extractor

    def extract_contact_data(self, index: int):
        # TODO: Post-processing false positive organisations and their contact data (index=3 e.g.)
        # TODO: Post-processing location relate to country code

        for line in sorted(self._pipeline(index=index).items()):
            print(line[1])

    def _pipeline(self, index: int) -> Dict[int, str]:
        # Get contact data
        contact_data = self.contact_data(index=index)

        # Preprocess lines
        lines = self._preprocess_lines(index=index, terms_to_avoid=COUNTRY_SPECIFIC[contact_data.country_code]['terms_to_avoid'])

        # Extract phone numbers, clean up lines and remove duplicate lines
        phone_numbers = LibPhoneNumberExtractor(country_code=contact_data.country_code).extract_lines(lines=lines)
        lines = self._clean_up_lines(lines=lines, extracted_lines=phone_numbers)
        phone_numbers = self._remove_duplicate_lines(extracted_lines=phone_numbers)

        # Extract mail, clean up lines and remove duplicate lines
        mail_addresses = RegExMailAddressExtractor(pattern=UNIVERSAL['patterns']['mail']).extract_lines(lines=lines)
        lines = self._clean_up_lines(lines=lines, extracted_lines=mail_addresses)
        mail_addresses = self._remove_duplicate_lines(extracted_lines=mail_addresses)

        # Extract urls, clean up lines and remove duplicate lines
        domain: str = tldextract.extract(contact_data.crawled_website).domain
        urls = RegExURLExtractor(domain=domain, pattern=UNIVERSAL['patterns']['url']).extract_lines(lines=lines)
        # urls, lines = self._extract_urls(domain=domain, pattern=UNIVERSAL['patterns']['url'], lines=lines)
        lines = self._clean_up_lines(lines=lines, extracted_lines=urls)
        urls = self._remove_duplicate_lines(extracted_lines=urls)

        # Extract bank data
        bank_data = self._extract_bank_data(patterns=UNIVERSAL['patterns']['bank_data'], terms=COUNTRY_SPECIFIC[contact_data.country_code]['terms']['bank_data'], lines=lines)

        # Clean up lines and remove duplicate lines
        for domain, matched_lines in bank_data.items():
            lines = self._clean_up_lines(lines=lines, extracted_lines=bank_data[domain])
            bank_data[domain] = self._remove_duplicate_lines(extracted_lines=bank_data[domain])

        # Extract company data, clean up lines and remove duplicate lines
        company_data = self._extract_company_data(patterns=COUNTRY_SPECIFIC[contact_data.country_code]['patterns']['company_data'], terms=COUNTRY_SPECIFIC[contact_data.country_code]['terms']['company_data'], lines=lines)

        # Clean up lines and remove duplicate lines
        for domain, matched_lines in company_data.items():
            lines = self._clean_up_lines(lines=lines, extracted_lines=company_data[domain])
            company_data[domain] = self._remove_duplicate_lines(extracted_lines=company_data[domain])

        # Extract location, organisation and manager data with named entity recognition
        ner_data = self._extract_ner_data(ner_pipeline=COUNTRY_SPECIFIC[contact_data.country_code]['ner_pipeline'], lines=lines)

        # Clean up lines and remove duplicate lines
        for domain, matched_lines in ner_data.items():
            ner_data[domain] = self._remove_duplicate_lines(extracted_lines=ner_data[domain])

        # Concatenate all matched lines dictionaries
        matched_lines = [[phone_numbers], [mail_addresses], [urls], list(bank_data.values()), list(company_data.values()), list(ner_data.values())]
        extracted_contact_data: Dict[int, str] = self._concatenate_data_dictionaries(matched_lines=list(chain(*matched_lines)))

        return extracted_contact_data

    def _preprocess_lines(self, index: int, terms_to_avoid: List[str]) -> Dict[int, str]:
        lines: Dict[int, str] = {index: line.replace(u'\xa0', u' ') for index, line in
                                 enumerate(self.split_lines(index=index))}

        # Remove lines related to Social Networks
        lines = {index: line for index, line in lines.items() if
                 'google' not in line.lower() and 'facebook' not in line.lower() and 'twitter' not in line.lower() and 'instagram' not in line.lower()}

        # Remove lines with content for cookies
        lines = {index: line for index, line in lines.items() if 'cookie' not in line.lower()}

        # Remove irrelevant country specific terms
        remove: Set[int] = set()

        for line_index, line in lines.items():
            for term in terms_to_avoid:
                if term in line.lower():
                    remove.add(line_index)

        for line_index in remove:
            del lines[line_index]

        return lines

    def _extract_bank_data(self, patterns: Dict[str, str], terms: Dict[str, List[str]], lines: Dict[int, str]) -> Dict[
        str, Dict[int, str]]:
        bank_data_lines: Dict[str, Dict[int, str]] = {'iban': {}, 'swift/bic': {}, 'terms': {}}

        for domain, pattern in patterns.items():
            for line_index, line in lines.items():
                if re.search(pattern, line):
                    bank_data_lines[domain][line_index] = line

        bank_data_lines['terms'] = self._match_terms(terms=terms, lines=lines)

        return bank_data_lines

    def _extract_company_data(self, patterns: Dict[str, str], terms: Dict[str, List[str]], lines: Dict[int, str]) -> \
            Dict[str, Dict[int, str]]:
        company_data_lines: Dict[str, Dict[int, str]] = {'company_book_number': {}, 'uid_number': {}, 'dvr_number': {},
                                                         'terms': {}}

        for domain, pattern in patterns.items():
            for line_index, line in lines.items():
                if re.search(pattern, line):
                    company_data_lines[domain][line_index] = line
                elif domain == 'dvr_number' and 'dvr' in line.lower():
                    if line_index + 1 in lines:
                        concatenated: str = line + '\n' + lines[line_index + 1]

                        if re.search(pattern, concatenated):
                            company_data_lines[domain][line_index] = line
                            company_data_lines[domain][line_index + 1] = lines[line_index + 1]

        company_data_lines['terms'] = self._match_terms(terms=terms, lines=lines)

        return company_data_lines

    def _extract_ner_data(self, ner_pipeline: TokenClassificationPipeline, lines: Dict[int, str]) -> Dict[str, Dict[int, str]]:
        ner_data: Dict[str, Dict[int, str]] = {'location': {}, 'organisation': {}, 'manager': {}}

        for line_index, line in lines.items():
            entities = ner_pipeline(line)

            if line_index not in ner_data['location'] and line_index not in ner_data['organisation'] and line_index not in ner_data['manager']:
                for entity in entities:
                    if entity['entity_group'] == 'ORG':
                        ner_data['organisation'][line_index] = line

                    if entity['entity_group'] == 'LOC':
                        ner_data['location'][line_index] = line

                    if entity['entity_group'] == 'PER':
                        ner_data['manager'][line_index] = line

        return ner_data

    def _match_terms(self, terms: Dict[str, List[str]], lines: Dict[int, str]) -> Dict[int, str]:
        matched_terms: Dict[int, str] = {}
        add_next_line: List[int] = []

        for term in terms['standalone']:
            for line_index, line in lines.items():
                if term in line.lower():
                    if self._is_standalone(term, line.lower()):
                        if not self._contains_complete_content(line=line):
                            if line_index not in add_next_line:
                                add_next_line.append(line_index)

                        matched_terms[line_index] = line

        for term in terms['wherever']:
            for line_index, line in lines.items():
                if term in line.lower():
                    if not self._contains_complete_content(line=line):
                        if line_index not in add_next_line:
                            add_next_line.append(line_index)

                    if line_index not in matched_terms:
                        matched_terms[line_index] = line

        # Add next line
        for line_index in add_next_line:
            if line_index + 1 not in add_next_line:
                if line_index + 1 in lines:
                    matched_terms[line_index + 1] = lines[line_index + 1]

        return matched_terms

    def _is_standalone(self, term: str, line: str) -> bool:
        if line.find(term) == 0:
            return True

        if self._is_number(line[line.index(term) - 1]) or self._is_valid_special_character_start(
                line[line.index(term) - 1]):
            return True

        if self._is_number(line[line.index(term) + len(term)]) or self._is_valid_special_character_end(
                line[line.index(term) + len(term)]):
            return True

        return False

    def _is_number(self, character: str):
        try:
            num = float(character)
            # check for "nan" floats
            return num == num  # or use `math.isnan(num)`
        except ValueError:
            return False

    def _is_valid_special_character_start(self, character: str):
        valid_special_characters: str = '-:/\\.'

        return character in valid_special_characters

    def _is_valid_special_character_end(self, character: str):
        valid_special_characters: str = '-: /\\.'

        return character in valid_special_characters

    def _contains_complete_content(self, line: str):
        clean: List[str] = list(filter(None, line.split(' ')))

        return not clean[len(clean) - 1][-1] == ':' or not clean[len(clean) - 1][-1] == ','

    def _clean_up_lines(self, lines: Dict[int, str], extracted_lines: Dict[int, str]):
        for line_index, line in extracted_lines.items():
            del lines[line_index]

        return lines

    def _remove_duplicate_lines(self, extracted_lines: Dict[int, str]) -> Dict[int, str]:
        temp = {val: key for key, val in extracted_lines.items()}
        unique = {val: key for key, val in temp.items()}

        return unique


    def _concatenate_data_dictionaries(self, matched_lines: List[Dict[int, str]]):
        data: Dict[int, str] = {}

        for lines in matched_lines:
            data.update(lines)

        return data

    #@property
    #def phone_number_extractor(self):
    #    return self._phone_number_extractor

    #@property
    #def mail_address_extractor(self):
    #    return self._mail_address_extractor

    #@property
    #def url_extractor(self):
    #    return self._url_extractor


if __name__ == '__main__':
    dl = DataLoader('C:/Users/TimoM/PycharmProjects/ner/data/imprints_plausible.json')
    cdr = ContactDataRetrieval(data_loader=dl)
    cdr.extract_contact_data(index=0)

    # TODO: Compare Swift to database
    # response = requests.get('http://www.swiftcodelist.com/search.php', params={'q': 'BFKKAT2KKLA', 'submit': 'Search'})
    # bs = BeautifulSoup(response.content, 'html.parser')
    # print(bs.prettify())
    # table = bs.find(lambda tag: tag.name == 'table' and tag.has_attr('class') and tag['class'] == 'pro magt10')
    # rows = table.find_all(lambda tag: tag.name == 'tr')
    # print(rows)
    # print(len(rows))
