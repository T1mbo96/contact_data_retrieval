from transformers import pipeline

# Universal settings for any country
UNIVERSAL = {
    'patterns':
        {
            'mail': r'[a-zA-Z0-9\.\-+_]+(@|\(at\))[a-zA-Z0-9\.\-+_]+\.[a-z]+',
            'url': r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))",
            'bank_data':
                {
                    'iban': r'([A-Z]{2}[ \-]?[0-9]{2})(?=(?:[ \-]?[A-Z0-9]){9,30}$)((?:[ \-]?[A-Z0-9]{3,5}){2,7})([ \-]?[A-Z0-9]{1,3})?',
                    'swift/bic': r'[A-Z]{4}[-\s\\\/]?[A-Z]{2}[-\s\\\/]?[A-Z0-9]{2}[-\s\\\/]?([A-Z0-9]{3})?$'
                },
        }
}

# Country specific settings
COUNTRY_SPECIFIC = {
    'AT': {
        'ner_pipeline': pipeline('ner', model='xlm-roberta-large-finetuned-conll03-german',
                                 tokenizer='xlm-roberta-large-finetuned-conll03-german', grouped_entities=True),
        'patterns':
            {
                'company_data':
                    {
                        'company_book_number': r'(fn|FN)?\s?[0-9]{1,6}\s?[aAbBdDfFgGhHiIkKmMpPsStTvVwWxXyYzZ]$',
                        'uid_number': r'ATU[-\s]?[0-9]{8}',
                        'dvr_number': r'(dvr|DVR).+\n?[0-9]{7}'
                    }
            },
        'terms':
            {
                'bank_data':
                    {
                        'standalone': [],
                        'wherever': ['konto']
                    },
                'company_data':
                    {
                        'standalone': ['ara'],
                        'wherever': []
                    },
            },
        'terms_to_avoid': ['haftung', 'gewähr', 'urheberrechtlich', 'streitbeilegung', 'kommerziell', 'persönlich',
                           'impressum', 'newsletter', 'subscription', 'inhalt', 'einverstanden', 'einverständ',
                           'datenschutz']
    }
}
