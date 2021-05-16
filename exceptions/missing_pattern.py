class MissingPatternError(Exception):
    def __init__(self):
        super().__init__('Valid RegEx pattern is missing!')
