from extractors.extracting_tasks import RegExExtractingTask


class VATNumberExtractor(RegExExtractingTask):
    pattern = r'DE?[-\s]?[0-9]{3}[-\s]?[0-9]{3}[-\s]?[0-9]{3}'
    type = 'vat'


if __name__ == '__main__':
    vatne = VATNumberExtractor({1: 'Tiest, asva avav 1823240239, DE813992525. AT813992526 yoyoyoy DE123456789'})
    print(vatne.extracted)