from typing import List, Dict, Any, Tuple
from postal.parser import parse_address
from transformers import Pipeline, pipeline

from extractors.extracting_tasks import NERExtractingTask


class LocationExtractor(NERExtractingTask):
    model = 'xlm-roberta-large-finetuned-conll03-german'
    tokenizer = 'xlm-roberta-large-finetuned-conll03-german'
    type_mappings = {
        'po_box': 'poBox',
        'postcode': 'zip',
        'house_number': 'street_house_number',
        'road': 'street_road',
        'unit': 'street2_unit',
        'level': 'street2_level',
        'staircase': 'street2_staircase',
        'entrance': 'street2_entrance',
        'house': 'street2_house',
        'category': 'street2_category',
        'near': 'street2_near',
        'suburb': 'city_suburb',
        'city_district': 'city_city_district',
        'city': 'city_city',
        'state': 'state',
        'state_district': 'state',
        'country': 'country'
    }

    def _extract(self):
        ner_pipeline: Pipeline = pipeline('ner', model=self.model, tokenizer=self.tokenizer, grouped_entities=True)
        extracted: List[Dict[str, Any]] = []

        for line_index, line in self.lines.items():
            entities = ner_pipeline(line)

            delete: List[int] = []

            for index in range(len(entities)):
                if entities[index]['score'] < 0.9:
                    delete.append(index)

            for index in sorted(delete, reverse=True):
                del entities[index]

            print(line)
            print(entities)

            if any(entity.get('entity_group') == 'LOC' for entity in entities):
                locations: List[Tuple[str, str]] = parse_address(line)

                print(locations)

                for location in locations:
                    if location[1] in self.type_mappings:
                        extracted.append({
                            'type': self.type_mappings[location[1]],
                            'match': location[0],
                            'index': line_index
                        })

        print(f'Locations: {extracted}')

        return extracted


if __name__ == '__main__':
    le = LocationExtractor({1: 'P.O.Box 2000'})