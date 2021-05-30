# https://www.analyticsvidhya.com/blog/2018/04/a-comprehensive-guide-to-understand-and-implement-text-classification-in-python/
import pickle
import logging
import os
import fasttext_trainer
import pandas as pd
import advertools as adv
import xgboost as xgboost

from typing import Tuple, List, Any, Dict
from datetime import date
from sklearn import model_selection, preprocessing, metrics, naive_bayes, linear_model, svm, ensemble
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from prettytable import PrettyTable

from data_loader import DataLoader
from language_settings import LANGUAGES

ALLOWED_CLASSIFIERS = (
    'naive_bayes',
    'linear',
    'svm',
    'bagging',
    'boosting',
    'shallow_nn',
    'cnn',
    'lstm',
    'gru',
    'bidirectional_rnn',
    'rcnn'
)

ALLOWED_FEATURE_TYPES = (
    'count',
    'tf_idf',
    'word_embeddings'
)

logging.basicConfig(format='%(asctime)s %(message)s')


class TextClassification:
    def __init__(self, data_loader: DataLoader, languages: Tuple[str, ...], feature_types: List[str], classifiers: List[str]):
        self._dataset: pd.DataFrame = pd.DataFrame(data_loader.misleading_training_data(languages=languages), columns=['line', 'is_misleading'])
        self._feature_types = feature_types
        self._train_x, self._train_y, self._valid_x, self._valid_y = self._train_val_split()
        self._country_codes: Tuple[str] = languages
        self._stop_words: List[str] = [stop_word for sublist in [stop_words for language in LANGUAGES[self.country_codes] for stop_words in adv.stopwords[language]] for stop_word in sublist]
        self._trained_classifiers: List[Dict[str, Any]] = []
        self._train_vector_features = pd.DataFrame()
        self._valid_vector_features = pd.DataFrame()

        if any(feature_type not in ALLOWED_FEATURE_TYPES for feature_type in feature_types):
            raise ValueError(f'Allowed features types: {ALLOWED_FEATURE_TYPES}')

        if any(classifier not in ALLOWED_CLASSIFIERS for classifier in classifiers):
            raise ValueError(f'Allowed classifiers: {ALLOWED_CLASSIFIERS}')

        for feature_type in feature_types:
            feature_function = getattr(TextClassification, '_' + feature_type)
            feature_function(self)

        for classifier in classifiers:
            classifier_function = getattr(TextClassification, '_' + classifier)
            trained_classifier, accuracy = classifier_function(self)

            self._trained_classifiers.append({'classifier_type': classifier, 'trained_classifier': trained_classifier, 'accuracy': accuracy})
            self._save_classifier(trained_classifier, accuracy)

    def __str__(self):
        print(self.feature_types)
        table = PrettyTable()
        table.field_names = ['classifier_type', 'trained_classifier', 'accuracy']

        for classifier in self.trained_classifiers:
            table.add_row([classifier['classifier_type'], classifier['trained_classifier'], classifier['accuracy']])

        return str(table)

    def _train_val_split(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        logging.info('Start train validation split.')

        train_x, valid_x, train_y, valid_y = model_selection.train_test_split(self.dataset[['line']], self.dataset[['is_misleading']], test_size=0.2)

        encoder = preprocessing.LabelEncoder()
        train_y = encoder.fit_transform(train_y['is_misleading'])
        valid_y = encoder.fit_transform(valid_y['is_misleading'])

        logging.info('End train validation split.')

        return train_x, train_y, valid_x, valid_y

    def _count(self):
        logging.info('Start count vectorization.')

        count_doc = CountVectorizer(analyzer='word', token_pattern=r'\w{1,}', max_features=2500, stop_words=self.stop_words)
        count_doc.fit(self.train_x['line'])
        self._save_vectorizer(count_doc, 'count')

        train_x_count_vector = count_doc.transform(self.train_x['line'])
        valid_x_count_vector = count_doc.transform(self.valid_x['line'])

        train_x_count_vector = pd.DataFrame(train_x_count_vector.toarray(), columns=count_doc.get_feature_names())
        valid_x_count_vector = pd.DataFrame(valid_x_count_vector.toarray(), columns=count_doc.get_feature_names())

        if self._train_vector_features.empty and self._valid_vector_features.empty:
            self._train_vector_features = train_x_count_vector
            self._valid_vector_features = valid_x_count_vector
        else:
            self._train_vector_features = pd.concat([self._train_vector_features, train_x_count_vector], axis=1)
            self._valid_vector_features = pd.concat([self._valid_vector_features, valid_x_count_vector], axis=1)

        logging.info('End count vectorization.')

    def _tf_idf(self):
        logging.info('Start tf-idf vectorization.')

        tf_idf_doc = TfidfVectorizer(analyzer='word', token_pattern=r'\s', stop_words=self.stop_words)
        tf_idf_doc.fit(self.train_x['line'])
        self._save_vectorizer(tf_idf_doc, 'tf_idf')

        self._train_x_tf_idf_vector = tf_idf_doc.transform(self.train_x['line'])
        self._valid_x_tf_idf_vector = tf_idf_doc.transform(self.valid_x['line'])

        logging.info('End tf-idf vectorization.')

    def _train_model(self, classifier, is_neural_net: bool = False):
        classifier.fit(self._train_x_tf_idf_vector, self.train_y)
        predictions = classifier.predict(self._valid_x_tf_idf_vector)

        if is_neural_net:
            predictions = predictions.argmax(axis=-1)

        return classifier, metrics.accuracy_score(predictions, self.valid_y)

    def _naive_bayes(self):
        logging.info('Start training naive bayes.')

        classifier, accuracy = self._train_model(naive_bayes.MultinomialNB())

        logging.info('End training naive bayes.')

        return classifier, accuracy

    def _linear(self):
        logging.info('Start training linear.')

        classifier, accuracy = self._train_model(linear_model.LogisticRegression(max_iter=1000))

        logging.info('End training linear.')

        return classifier, accuracy

    def _svm(self):
        logging.info('Start training svm.')

        classifier, accuracy = self._train_model(svm.SVC())

        logging.info('End training svm.')

        return classifier, accuracy

    def _bagging(self):
        logging.info('Start training bagging.')

        classifier, accuracy = self._train_model(ensemble.RandomForestClassifier())

        logging.info('End training bagging.')

        return classifier, accuracy

    def _boosting(self):
        logging.info('Start training boosting.')

        classifier, accuracy = self._train_model(xgboost.XGBClassifier())

        logging.info('End training boosting.')

        return classifier, accuracy

    def _save_vectorizer(self, vectorizer, vectorizer_type):
        logging.info(f'Start saving {vectorizer.__class__}.')

        try:
            os.mkdir(f'C:/Users/TimoM/PycharmProjects/contact_data_retrieval/vectorizers/{date.today()}')
        except FileExistsError:
            logging.info(f'Folder {date.today()} in vectorizers already exists. Skipping.')

        with open(f'C:/Users/TimoM/PycharmProjects/contact_data_retrieval/vectorizers/{date.today()}/{vectorizer_type}.pkl', 'wb') as file:
            pickle.dump(vectorizer, file)

        logging.info(f'End saving {vectorizer.__class__}')

    def _save_classifier(self, classifier, accuracy):
        logging.info(f'Start saving {str(classifier)}.')

        try:
            os.mkdir(f'C:/Users/TimoM/PycharmProjects/contact_data_retrieval/classifiers/{date.today()}')
        except FileExistsError:
            logging.info(f'Folder {date.today()} in classifiers already exists. Skipping.')

        with open(f'C:/Users/TimoM/PycharmProjects/contact_data_retrieval/classifiers/{date.today()}/{str(classifier)}_{accuracy}.pkl', 'wb') as file:
            pickle.dump(classifier, file)

        logging.info(f'End saving {str(classifier)}.')

    @property
    def dataset(self):
        return self._dataset

    @property
    def feature_types(self):
        return self._feature_types

    @property
    def train_x(self):
        return self._train_x

    @property
    def train_y(self):
        return self._train_y

    @property
    def valid_x(self):
        return self._valid_x

    @property
    def valid_y(self):
        return self._valid_y

    @property
    def country_codes(self):
        return self._country_codes

    @property
    def stop_words(self):
        return self._stop_words

    @property
    def trained_classifiers(self):
        return self._trained_classifiers


if __name__ == '__main__':
    dl = DataLoader('C:/Users/TimoM/PycharmProjects/contact_data_retrieval/data/imprints_plausible_v2.json')
    tc = TextClassification(dl, ('DE',), ['tf_idf'], ['linear'])
    #print(tc)

