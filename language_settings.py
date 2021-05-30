from extractors.bank_data.company_registration_number_extractors import RegExCompanyRegistrationNumberExtractor
from extractors.bank_data.dvr_number_extractors import RegExDVRNumberExtractor
from extractors.bank_data.iban_extractors import RegExIBANExtractor
from extractors.bank_data.swift_bic_extractors import RegExSWIFTBICExtractor
from extractors.bank_data.uid_number_extractors import RegExUIDNumberExtractor
from extractors.mail_addresses.mail_address_extractors import RegExMailAddressExtractor
from extractors.named_entity_recognition.ner_extractors import HuggingFaceTransformersExtractor
from extractors.phone_numbers.phone_number_extractors import LibPhoneNumberExtractor
from extractors.terms.arbitrary_position_extractors import ArbitraryPositionExtractor
from extractors.relevant_lines.relevant_lines_extractors import TFIDFLogisticRegressionExtractor, FasttextExtractor, \
    DictionaryRelevantLinesExtractor
from extractors.terms.standalone_extractors import StandaloneExtractor
from extractors.urls.url_extractors import RegExURLExtractor

# Country specific settings
DICTIONARIES = {
    'AT': {
        'avoid': [
            'haftung', 'gewähr', 'urheberrechtlich', 'streitbeilegung', 'kommerziell', 'persönlich', 'impressum',
            'newsletter', 'subscription', 'inhalt', 'einverstanden', 'einverständ', 'datenschutz'
        ],
        'match': {
            'standalone': [
                'ara'
            ],
            'arbitrary_position': [
                'konto'
            ]
        },
        'named_entity_recognition': {
            'model': 'xlm-roberta-large-finetuned-conll03-german',
            'tokenizer': 'xlm-roberta-large-finetuned-conll03-german'
        }
    },
    'DE': {
        'avoid': [
            'haftung', 'gewähr', 'urheberrechtlich', 'streitbeilegung', 'kommerziell', 'persönlich', 'impressum',
            'newsletter', 'subscription', 'inhalt', 'einverstanden', 'einverständ', 'datenschutz'
        ],
        'match': {
            'standalone': [
                'ara'
            ],
            'arbitrary_position': [
                'konto'
            ]
        },
        'named_entity_recognition': {
            'model': 'xlm-roberta-large-finetuned-conll03-german',
            'tokenizer': 'xlm-roberta-large-finetuned-conll03-german'
        }
    }
}

# Country specific pipelines
PIPELINES = {
    'AT': [
        DictionaryRelevantLinesExtractor, LibPhoneNumberExtractor, RegExMailAddressExtractor, RegExURLExtractor,
        RegExIBANExtractor, RegExSWIFTBICExtractor, RegExCompanyRegistrationNumberExtractor, RegExUIDNumberExtractor,
        RegExDVRNumberExtractor, StandaloneExtractor, ArbitraryPositionExtractor, HuggingFaceTransformersExtractor
    ],
    'DE': [
        DictionaryRelevantLinesExtractor, LibPhoneNumberExtractor, RegExMailAddressExtractor, RegExURLExtractor,
        RegExIBANExtractor, RegExSWIFTBICExtractor, RegExCompanyRegistrationNumberExtractor, RegExUIDNumberExtractor,
        RegExDVRNumberExtractor, StandaloneExtractor, ArbitraryPositionExtractor, HuggingFaceTransformersExtractor
    ],
}

# Binary Classification Training Settings
LANGUAGES = {
    ('DE',): ['german']
}
