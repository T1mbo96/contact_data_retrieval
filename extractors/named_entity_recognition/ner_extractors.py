from typing import Dict

from transformers import pipeline, Pipeline

from abstract_classes.contact_data_retrieval_tasks import NamedEntityRecognitionContactDataRetrievalTask


class HuggingFaceTransformersExtractor(NamedEntityRecognitionContactDataRetrievalTask):
    def __init__(self, model: str, tokenizer: str):
        self._model: str = model
        self._tokenizer: str = tokenizer

    def extract_lines(self, lines: Dict[int, str]) -> Dict[int, str]:
        ner_pipeline: Pipeline = pipeline('ner', model=self.model, tokenizer=self.tokenizer, grouped_entities=True)
        matched_lines: Dict[int, str] = {}

        for line_index, line in lines.items():
            entities = ner_pipeline(line)

            if line_index not in matched_lines:
                for entity in entities:
                    if entity['entity_group'] == 'ORG':
                        matched_lines[line_index] = line

                    if entity['entity_group'] == 'LOC':
                        matched_lines[line_index] = line

                    if entity['entity_group'] == 'PER':
                        matched_lines[line_index] = line

        return matched_lines

    @property
    def model(self):
        return self._model

    @property
    def tokenizer(self):
        return self._tokenizer
