from extractors.extractor_templates import RegExExtractor


class RegExMailAddressExtractor(RegExExtractor):
    pattern = r'[a-zA-Z0-9\.\-+_]+(@|\(at\))[a-zA-Z0-9\.\-+_]+\.[a-z]+'
