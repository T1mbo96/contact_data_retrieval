from extractors.extractor_templates import RegExExtractor


class RegExCompanyRegistrationNumberExtractor(RegExExtractor):
    pattern = r'(fn|FN)?\s?[0-9]{1,6}\s?[aAbBdDfFgGhHiIkKmMpPsStTvVwWxXyYzZ]$'
