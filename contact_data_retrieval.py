import json
import operator
import re
import tldextract

from itertools import combinations
from difflib import SequenceMatcher
from typing import List, Type, Dict, Any
from genderize import Genderize
from fuzzywuzzy.fuzz import token_set_ratio
from pgeocode import Nominatim
from tldextract.tldextract import ExtractResult
from cleanco import prepare_terms, basename

from contact_data import ContactData
from data_loader import DataLoader
from extractors.e_mail_address_extractor import EMailAddressExtractor
from extractors.extracting_tasks import ExtractingTask
from extractors.human_name_extractor import HumanNameExtractor
from extractors.location_extractor import LocationExtractor
from extractors.organization_extractor import OrganizationExtractor
from extractors.phone_number_extractor import PhoneNumberExtractor
from extractors.url_extractor import URLExtractor
from extractors.vat_number_extractor import VATNumberExtractor
from pre_processing import PreProcessing


class ContactDataRetrieval(PreProcessing):
    _similarity_cutoff = 70

    _filter_mappings = {
        'e_mails': EMailAddressExtractor,
        'human_names': HumanNameExtractor,
        'locations': LocationExtractor,
        'organizations': OrganizationExtractor,
        'phone_numbers': PhoneNumberExtractor,
        'vat_numbers': VATNumberExtractor,
        'urls': URLExtractor,
        'positions': None,
    }

    _irrelevant_lines = [
        'gericht'
    ]

    _irrelevant_entities = [
        'chrome', 'browser', 'google', 'facebook', 'microsoft', 'apple', 'support', 'mozilla', 'firefox', 'safari',
        'opera', 'edge', 'webfonts', 'youtube'
    ]

    _top_level_domains = [
        'com', 'org', 'de', 'edu', 'info'
    ]

    def __init__(self, contact_data: ContactData, filters: List[str] = None):
        # Initialize superclass
        super().__init__(contact_data=contact_data)

        # Initialize instance variables
        lines: Dict[int, str] = {index: line.replace(u'\xa0', u' ') for index, line in enumerate(self.split_lines())}

        print('lines:')
        for line_index, line in lines.items():
            print(f'{line_index}: {line}')

        relevant_lines: Dict[int, str] = {}

        for line_index, line in lines.items():
            relevant_flag = True

            for irrelevant in self._irrelevant_lines:
                print(line)
                print(irrelevant in line.lower())
                if irrelevant in line.lower():
                    relevant_flag = False

            if relevant_flag:
                relevant_lines[line_index] = line

        print('relevant lines:')
        for line_index, line in relevant_lines.items():
            print(f'{line_index}: {line}')

        self._lines = relevant_lines
        self._filters: List[Type[ExtractingTask]] = self._prepare_filters(filters)
        self._save_blocks(self._pipeline())

    def __str__(self):
        pass

    def __repr__(self):
        pass

    def _main_organisation(self, entities: List[Dict[str, Any]]):
        #TODO: Maybe use basename for comparison, but need to combine with business type again
        umlauts = {'ä': 'ae', 'Ä': 'Ae', 'ö': 'oe', 'Ö': 'Oe', 'ü': 'ue', 'Ü': 'Ue', 'ß': 'ss'}

        organizations: List[str] = [entity['match'] for entity in entities if entity['type'] == 'organization']
        cleaned: List[str] = []

        for organization in organizations:
            replaced = organization

            for umlaut, replacement in umlauts.items():
                replaced = replaced.replace(umlaut, replacement)

            cleaned.append(replaced)

        substring_counts: Dict[str, int] = {}

        for i in range(0, len(cleaned)):
            for j in range(i + 1, len(cleaned)):
                first: str = cleaned[i]
                second: str = cleaned[j]

                match = SequenceMatcher(None, first, second).find_longest_match(0, len(first), 0, len(second))
                matching_substring = first[match.a:(match.a + match.size)]

                if matching_substring not in substring_counts:
                    substring_counts[matching_substring] = 1
                else:
                    substring_counts[matching_substring] += 1

        if '' in substring_counts:
            del substring_counts['']

        first_occurrence: str = cleaned[0]
        most_occurrences: str = max(substring_counts.items(), key=operator.itemgetter(1))[0].strip()
        website_domain: str = tldextract.extract(self.contact_data.crawled_website).domain
        imprint_domain: str = tldextract.extract(self.contact_data.crawled_imprint).domain

        token_set_ratios: List[Dict[str, Any]] = []

        for permutation in combinations([first_occurrence, most_occurrences, website_domain, imprint_domain] + cleaned, 2):
            token_set_ratios.append({'permutation': permutation, 'ratio': token_set_ratio(permutation[0], permutation[1])})

        assorted: List[Dict[str, Any]] = sorted(token_set_ratios, key=lambda k: k['ratio'], reverse=True)
        print(assorted)
        highest_ratio: int = assorted[0]['ratio']

        main: List[str] = []

        for element in assorted:
            if element['ratio'] == highest_ratio:
                main.append(element['permutation'][0])

        return sorted(main, key=len, reverse=True)[0]

    def _prepare_filters(self, filters: List[str]) -> List[Type[ExtractingTask]]:
        _filters: List[Type[ExtractingTask]] = []

        for _filter in filters:
            _filters.append(self._filter_mappings[_filter])

        return _filters

    def _pipeline(self):
        _matches: List[Dict[str, Any]] = []

        for _filter in self.filters:
            if issubclass(_filter, PhoneNumberExtractor):
                _matches = _matches + _filter(lines=self.lines, country_code=self.contact_data.country_code).extracted
            else:
                _matches = _matches + _filter(lines=self.lines).extracted

        return _matches

    def _save_blocks(self, *args):
        assorted: List[Dict[str, Any]] = sorted(args[0], key=lambda k: k['index'])

        with open('test1.json', 'w') as file:
            json.dump(assorted, file)

        with open('test1.json', 'r') as file:
            lines = json.load(file)

    def _relevant(self) -> List[Dict[str, Any]]:
        # TODO: accept lines from pipeline

        with open('test1.json', 'r') as file:
            entities = json.load(file)

        print('entities')
        for entity in entities:
            print(entity)

        relevant: List[Dict[str, Any]] = []

        for entity in entities:
            relevant_flag: bool = True

            for irrelevant in self._irrelevant_entities:
                if irrelevant in entity['match'].lower():
                    relevant_flag = False

            for irrelevant in self._top_level_domains:
                if entity['type'] == 'organization':
                    if irrelevant in entity['match'].lower():
                        relevant_flag = False

            if relevant_flag:
                relevant.append(entity)

        return relevant

    def blocks(self):
        relevant: List[Dict[str, Any]] = self._relevant()

        print('relevant')
        for element in relevant:
            print(element)

        main_organization: str = self._main_organisation(entities=relevant)
        terms = prepare_terms()
        main_organization_base_name: str = basename(main_organization, terms, prefix=False, middle=False, suffix=True)

        misleading_flag: bool = False
        blocks: Dict[str, Any] = {
            'main': {
                'fax': None,
                'vat': None,
                'zip': None,
                'city': None,
                'email': None,
                'phone': None,
                'poBox': None,
                'state': None,
                'title': None,
                'gender': None,
                'mobile': None,
                'street': None,
                'country': None,
                'street2': None,
                'website': None,
                'lastName': None,
                'position': None,
                'firstName': None,
                'organization': main_organization
            },
            'secondary': [],
            'misleading': []
        }
        temp = {
            'tag': None,
            'matches': [],
            'entities': []
        }
        reverse_umlauts = {
            'ae': 'ä',
            'Ae': 'Ä',
            'oe': 'ö',
            'Oe': 'Ö',
            'ue': 'ü',
            'Ue': 'Ü',
            'ss': 'ß'
        }

        for entity in relevant:
            print(entity)
            if misleading_flag:
                print(1)
                if entity['type'] != 'organization':
                    print(2)
                    blocks['misleading'].append(entity)
                else:
                    print(3)
                    if token_set_ratio(main_organization_base_name, basename(entity['match'], terms, prefix=False, middle=False, suffix=True)) > self._similarity_cutoff:
                        print(4)
                        misleading_flag = False
                        blocks['secondary'].append(entity)
                    else:
                        print(6)
                        blocks['misleading'].append(entity)
            else:
                print(7)
                if entity['type'] == 'organization':
                    print(8)
                    if token_set_ratio(main_organization_base_name, basename(entity['match'], terms, prefix=False, middle=False, suffix=True)) < self._similarity_cutoff:
                        print(9)
                        misleading_flag = True
                        blocks['misleading'].append(entity)
                    else:
                        print(10)
                        blocks['secondary'].append(entity)
                else:
                    print(13)
                    if '_' in entity['type']:
                        print(14)
                        tag = entity['type'].split('_')[0]

                        if temp['tag'] is None:
                            print(15)
                            temp['tag'] = tag
                            temp['matches'].append(entity['match'])
                            temp['entities'].append(entity)
                        elif tag == temp['tag']:
                            print(16)
                            temp['matches'].append(entity['match'])
                            temp['entities'].append(entity)
                        else:
                            print(17)
                            if not blocks['main'][temp['tag']]:
                                print(18)
                                blocks['main'][temp['tag']] = ' '.join(temp['matches'])
                            else:
                                print(19)
                                blocks['secondary'] += temp['entities']

                            temp = {'tag': tag, 'matches': [entity['match']], 'entities': [entity]}
                    else:
                        print(20)
                        if temp['tag'] is None:
                            print(21)
                            if not blocks['main'][entity['type']]:
                                print(22)
                                blocks['main'][entity['type']] = entity['match']
                            else:
                                print(23)
                                blocks['secondary'].append(entity)
                        else:
                            print(24)
                            print(temp['tag'])
                            print(blocks['main'])
                            print(temp)
                            print(blocks['main'][temp['tag']])
                            if not blocks['main'][temp['tag']]:
                                print(25)
                                blocks['main'][temp['tag']] = ' '.join(temp['matches'])

                                if not blocks['main'][entity['type']]:
                                    print(26)
                                    blocks['main'][entity['type']] = entity['match']
                                else:
                                    print(27)
                                    blocks['secondary'].append(entity['match'])
                            else:
                                print(28)
                                blocks['secondary'] += temp['entities']

                                if not blocks['main'][entity['type']]:
                                    print(26)
                                    blocks['main'][entity['type']] = entity['match']
                                else:
                                    print(27)
                                    blocks['secondary'].append(entity['match'])

                            temp = {'tag': None, 'matches': [], 'entities': []}

        blocks['main']['country'] = self.contact_data.country_code
        url: ExtractResult = tldextract.extract(self.contact_data.crawled_website)
        print(url)
        blocks['main']['website'] = f'{url.subdomain if url.subdomain else "www"}.{url.domain}.{url.suffix}'
        blocks['main']['gender'] = self._gender(first_name=blocks['main']['firstName']) if blocks['main']['firstName'] else None
        blocks['main']['zip'] = re.sub(r'\D', '', blocks['main']['zip']) if blocks['main']['zip'] else None
        blocks['main']['state'] = self._state(zip_code=blocks['main']['zip']) if blocks['main']['zip'] else None
        blocks['main']['vat'] = blocks['main']['vat'].replace(' ', '').replace('-', '') if blocks['main']['vat'] else None

        organization = blocks['main']['organization']

        for replacement, umlaut in reverse_umlauts.items():
            organization = organization.replace(replacement, umlaut)

        blocks['main']['organization'] = organization

        for key, value in blocks['main'].items():
            if key == 'gender':
                print(f'"{key}": {value}')
            else:
                print(f'"{key}": "{value}"')

    def _contact_data(self):
        pass

    def _accuracy(self):
        pass

    def _gender(self, first_name: str):
        gender = Genderize().get([first_name])[0]['gender']

        return 0 if gender == 'male' else 1 if gender == 'female' else ""

    def _state(self, zip_code: str):
        nomi = Nominatim(self.contact_data.country_code.lower())

        return nomi.query_postal_code(zip_code).state_code

    @property
    def lines(self):
        return self._lines

    @property
    def filters(self):
        return self._filters


if __name__ == '__main__':
    # test = 1200, test1 = 1481, test2 = 876, test3 = 538, test4 = 564, test5 = 187, test6 = 231, test7 = 347
    dl = DataLoader('data/imprints_plausible_v2.json')
    print(dl.contact_data(index=1481))
    cdr = ContactDataRetrieval(contact_data=dl.contact_data(index=1481), filters=['e_mails', 'human_names', 'locations', 'phone_numbers', 'organizations', 'phone_numbers', 'vat_numbers'])
    #cdr = ContactDataRetrieval(contact_data=dl.contact_data(index=347), filters=[])
    cdr.blocks()
    # TODO: for organization use probablepeople to split in name and type (e.g. cubewerk and GmbH), use only name for main organization but concatenate in final contact data
    # TODO: und teste organizations für misleading auch nur gegen den name also cubewerk GmbH und exali GmbH -> cubewerk vs exali
    # TODO: street missing at 538