from extractors.extracting_tasks import RegExExtractingTask


class EMailAddressExtractor(RegExExtractingTask):
    pattern = r'[a-zA-Z0-9\.\-+_]+(?:@|\(at\))[a-zA-Z0-9\.\-+_]+\.[a-z]+'
    type = 'email'


if __name__ == '__main__':
    emae = EMailAddressExtractor({1: 'Dies ist eine Email: timom96@mail.de. Dies ist keine E-Mail tt@34. aber dies ist wieder eine timom96@outlook.de'})
    print(emae.extracted)