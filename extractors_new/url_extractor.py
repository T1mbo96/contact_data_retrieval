from extracting_tasks import RegExExtractingTask


class URLExtractor(RegExExtractingTask):
    pattern = r"(?i)\b(?:(?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(?:(?:[^\s()<>]+|(?:\(?:[^\s()<>]+\)))*\))+(?:\(?:(?:[^\s()<>]+|(?:\(?:[^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    type = 'website'


if __name__ == '__main__':
    urle = URLExtractor({1: 'Dies ist ein Test. https://stackoverflow.com/questions/8297526/proper-exception-to-raise-if-none-encountered-as-argument. hahaha. www.google.de'})
    print(urle.extracted)

