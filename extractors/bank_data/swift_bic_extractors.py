from extractors.extractor_templates import RegExExtractor


class RegExSWIFTBICExtractor(RegExExtractor):
    pattern = r'[A-Z]{4}[-\s\\\/]?[A-Z]{2}[-\s\\\/]?[A-Z0-9]{2}[-\s\\\/]?([A-Z0-9]{3})?$'
