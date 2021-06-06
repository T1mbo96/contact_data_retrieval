import re

from typing import Any, Dict, List, Tuple, Match
from transformers import Pipeline, pipeline
from probablepeople import parse

from extractors.extracting_tasks import NERExtractingTask


class HumanNameExtractor(NERExtractingTask):
    model = 'xlm-roberta-large-finetuned-conll03-german'
    tokenizer = 'xlm-roberta-large-finetuned-conll03-german'
    _type_mappings = {
        'GivenName': 'firstName_given_name',
        'MiddleName': 'firstName_middle_name',
        'Surname': 'lastName',
        'PrefixMarital': 'title_prefix_marital',
        'PrefixOther': 'title_prefix_other'
    }
    _academic_degrees = [
        r'b\.\s*sc\.', r'bachelor\s*of\s*science',
        r'b\.\s*a\.', r'bachelor\s*of\s*arts',
        r'b\.\s*ed\.', r'bachelor\s*of\s*education',
        r'b\.\s*eng\.', r'bachelor\s*of\s*engineering',
        r'm\.\s*sc\.', r'master\s*of\s*science',
        r'm\.\s*res\.', r'master\s*of\s*research',
        r'mph', r'master\s*of\s*public\s*health',
        r'm\.\s*a\.', r'master\s*of\s*arts',
        r'm\.\s*ed\.', r'master\s*of\s*education',
        r'm\.\s*eng\.', r'master\s*of\s*engineering',
        r'm\.\s*b\.\s*eng\.', r'master\s*of\s*business\s*engineering',
        r'm\.\s*b\.\s*a\.', r'master\s*of\s*business\s*administration',
        r'dipl\.(?:-|\s*)ing\.', r'diplomingenieur',
        r'll\.\s*m\.', r'master\s*of\s*laws', r'legum\s*magister',
        r'dr\.', r'ph\.\s*d\.', r'doktor', r'doctor',
        r'prof\.', r'professor'
    ]

    def _extract(self):
        ner_pipeline: Pipeline = pipeline('ner', model=self.model, tokenizer=self.tokenizer, grouped_entities=True)
        extracted: List[Dict[str, Any]] = []

        for line_index, line in self.lines.items():
            temp: List[Dict[str, Any]] = []
            entities = ner_pipeline(line)

            delete: List[int] = []

            for index in range(len(entities)):
                if entities[index]['score'] < 0.9:
                    delete.append(index)

            for index in sorted(delete, reverse=True):
                del entities[index]

            if any(entity.get('entity_group') == 'PER' for entity in entities):
                for entity in entities:
                    if entity['entity_group'] == 'PER':
                        names: Dict[str, List[Tuple[str, str]]] = parse(entity['word'], type='person')

                        for name in names:
                            if name[1] in self._type_mappings:
                                temp.append({
                                    'type': self._type_mappings[name[1]],
                                    'match': name[0],
                                    'index': line_index
                                })

            remaining_line: str = line
            to_insert: Dict[int, Dict[str, Any]] = {}

            for index in range(len(temp)):
                degrees: List[Dict[str, Any]] = []

                if temp[index]['type'] == 'firstName_given_name' or temp[index]['type'] == 'firstName_middle_name':
                    if index == 0:
                        match: Match = re.search(temp[index]['match'], remaining_line)
                        substring: str = remaining_line[:match.start()].lower()
                        remaining_line = remaining_line[match.end() + 1:]

                        for pattern in self._academic_degrees:
                            degree: Match = re.search(pattern, substring)

                            if degree:
                                degrees.append({'start': degree.start(), 'match': degree.group(0)})
                    else:
                        match: Match = re.search(r'' + temp[index - 1]['match'] + '(.*?)' + temp[index]['match'], remaining_line)

                        if match:
                            substring: str = match.group(0).lower()
                            remaining_line = remaining_line[re.search(temp[index]['match'], remaining_line).end() + 1:]

                            for pattern in self._academic_degrees:
                                degree: Match = re.search(pattern, substring)

                                if degree:
                                    degrees.append({'start': degree.start(), 'match': degree.group(0)})

                if degrees:
                    degrees = sorted(degrees, key=lambda k: k['start'])
                    assorted: List[str] = []

                    for degree in degrees:
                        assorted.append(degree['match'])

                    to_insert[index] = {'type': 'title', 'match': ' '.join(assorted), 'index': line_index}

            counter: int = 0

            for index, entity in to_insert.items():
                temp.insert(index + counter, entity)
                counter += 1

            extracted += temp

        print(f'Human names: {extracted}')

        return extracted


if __name__ == '__main__':
    #hne = HumanNameExtractor({1: 'Prof. Dr. Toralf Haag und M. Sc. Thorsten Lohring', 2: 'Master of Science Helene Fischer'})
    print(re.search(r'Leif(.*?)Fredrik', 'Geschäftsführer: Leif Nilsson, Leif Fredrik Nilsson'))
