import abc
import pandas as pd


class IrisModelBase:

    @abc.abstractmethod
    def train(self,
              train_data: pd.DataFrame
              ):
        pass

    @abc.abstractmethod
    def infer(self,
              dataframe: pd.DataFrame
              ) -> pd.DataFrame:
        pass