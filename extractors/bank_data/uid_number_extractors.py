from extractors.extractor_templates import RegExExtractor


class RegExUIDNumberExtractor(RegExExtractor):
    pattern = r'ATU[-\s]?[0-9]{8}'
