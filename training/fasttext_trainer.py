import os
import fasttext
import logging
import pandas as pd
import numpy as np

from typing import Tuple
from datetime import date
from sklearn import model_selection

from data_loader import DataLoader


class FasttextTrainer:
    def __init__(self, data_loader: DataLoader, languages: Tuple[str, ...]):
        self._dataset: pd.DataFrame = pd.DataFrame(data_loader.misleading_training_data(languages=languages), columns=['line', 'is_misleading'])
        self._train_x, self._train_y, self._valid_x, self._valid_y = self._train_valid_split()
        self._train_file, self._valid_file = '../fasttext_data/contact_data_train.txt', '../fasttext_data/contact_data_valid.txt'
        self._remove_train_valid_file()
        self._create_train_valid_file()
        self._classifier, self._accuracy = self._train()
        self._save_classifier()

    def _train_valid_split(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        logging.info('Start train validation split.')

        train_x, valid_x, train_y, valid_y = model_selection.train_test_split(self.dataset[['line']], self.dataset[['is_misleading']], test_size=0.2)

        logging.info('End train validation split.')

        return train_x, train_y, valid_x, valid_y

    def _remove_train_valid_file(self):
        logging.info('Start remove train valid file.')

        self._remove_file(self.train_file)
        self._remove_file(self.valid_file)

        logging.info('End remove train valid file.')

    def _create_train_valid_file(self):
        logging.info('Start create train valid file.')

        self._create_file(self.train_file, self.train_x, self._train_y)
        self._create_file(self.valid_file, self.valid_x, self.valid_y)

        logging.info('End create train valid file.')

    def _remove_file(self, path: str):
        if os.path.exists(path):
            os.remove(path)

    def _create_file(self, path: str, features: pd.DataFrame, labels: np.array):
        with open(path, 'a+') as file:
            for (f_index, f_row), (l_index, l_row) in zip(features.iterrows(), labels.iterrows()):
                file.seek(0)

                if len(file.read(1)) > 0:
                    file.write('\n')

                file.write(f'__label__{"misleading" if l_row["is_misleading"] == True else "relevant"} {f_row["line"].encode("utf-8")}')

    def _train(self):
        classifier = fasttext.train_supervised(input='../fasttext_data/contact_data_train.txt')
        accuracy = classifier.test(path='../fasttext_data/contact_data_valid.txt')

        return classifier, accuracy

    def _save_classifier(self):
        logging.info(f'Start saving {str(self.classifier)}.')

        self.classifier.save_model(f'{self.accuracy}.bin')

        logging.info(f'End saving {str(self.classifier)}.')

    @property
    def dataset(self):
        return self._dataset

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
    def train_file(self):
        return self._train_file

    @property
    def valid_file(self):
        return self._valid_file

    @property
    def classifier(self):
        return self._classifier

    @property
    def accuracy(self):
        return self._accuracy


if __name__ == '__main__':
    dl = DataLoader('../data/imprints_plausible_v2.json')
    ftt = FasttextTrainer(data_loader=dl, languages=('DE',))
