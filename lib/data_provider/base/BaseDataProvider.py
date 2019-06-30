from enum import Enum
from datetime import datetime
from abc import ABCMeta, abstractmethod

import pandas as pd


class ProviderDateFormat(Enum):
    TIMESTAMP_UTC = 1
    TIMESTAMP_MS = 2
    DATETIME = 3
    DATE = 4


class BaseDataProvider(object, metaclass=ABCMeta):
    __data_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    __date_column = 'Date'

    @abstractmethod
    def __init__(self, __data_columns: list = None, __date_column: str = None):
        if __data_columns is not None:
            self.__data_columns = __data_columns

        if __date_column is not None:
            self.__date_column = __date_column

    @abstractmethod
    def __date_format(self) -> ProviderDateFormat:
        raise NotImplementedError

    @abstractmethod
    def historical_ohclv(self) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def next(self) -> pd.DataFrame:
        raise NotImplementedError

    def prepare_data(self, data_frame: pd.DataFrame, inplace: bool = True) -> pd.DataFrame:
        formatted = self.__format_date_column(
            data_frame=data_frame, inplace=inplace)
        formatted = self.__sort_by_date(data_frame=data_frame, inplace=inplace)

        return formatted

    def __sort_by_date(self, data_frame: pd.DataFrame, inplace: bool = True) -> pd.DataFrame:
        final_format = '%Y-%m-%d %H:%M'

        if self.__date_format() is ProviderDateFormat.DATE:
            final_format = '%Y-%m-%d'

        if inplace is True:
            formatted = data_frame
        else:
            formatted = data_frame.copy()

        formatted[self.__date_column] = formatted[self.__date_column].astype(
            str)
        formatted = formatted.sort_values([self.__date_column])
        formatted[self.__date_column] = pd.to_datetime(
            formatted[self.__date_column], format=final_format)

        return formatted

    def __format_date_column(self, data_frame: pd.DataFrame, inplace: bool = True) -> pd.DataFrame:
        date_format = self.__date_format()

        if inplace is True:
            formatted = data_frame
        else:
            formatted = data_frame.copy()

        if date_format is ProviderDateFormat.TIMESTAMP_UTC:
            formatted[self.__date_column] = formatted[self.__date_column].apply(
                lambda x: datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M'))
            formatted[self.__date_column] = pd.to_datetime(
                formatted[self.__date_column], format='%Y-%m-%d %H:%M')
        elif date_format is ProviderDateFormat.TIMESTAMP_MS:
            formatted[self.__date_column] = formatted[self.__date_column] = pd.to_datetime(
                formatted[self.__date_column], unit='ms')
        elif date_format is ProviderDateFormat.DATETIME:
            formatted[self.__date_column] = pd.to_datetime(
                formatted[self.__date_column], format='%Y-%m-%d %H:%M')
        elif date_format is ProviderDateFormat.DATE:
            formatted[self.__date_column] = pd.to_datetime(
                formatted[self.__date_column], format='%Y-%m-%d')
        else:
            raise NotImplementedError

        return formatted
