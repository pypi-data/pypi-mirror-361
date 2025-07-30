"""
Base class for Iris classification models in CrunchDAO platform.

This module provides the abstract base class that all iris classification models
must inherit from to ensure consistent interface across different model implementations.
"""

import abc
import pandas as pd


class IrisModelBase(abc.ABC):
    """
    Abstract base class for Iris classification models.
    
    All iris classification models must inherit from this class and implement
    the required abstract methods for training and inference.
    
    Example:
        ```python
        from crunchdao.crunch_example.iris import IrisModelBase
        import pandas as pd
        
        class MyIrisModel(IrisModelBase):
            def train(self, train_data: pd.DataFrame) -> None:
                # Implement your training logic here
                pass
            
            def infer(self, dataframe: pd.DataFrame) -> pd.DataFrame:
                # Implement your inference logic here
                # Return predictions as DataFrame with single column
                return pd.DataFrame({
                    'prediction': [0, 1, 2]  # Your predictions (0=setosa, 1=versicolor, 2=virginica)
                })
        ```
    """

    @abc.abstractmethod
    def train(self, train_data: pd.DataFrame) -> None:
        """
        Train the model using the provided training data.
        
        Args:
            train_data: A pandas DataFrame containing the training data.
                       Expected to have features for sepal length, sepal width,
                       petal length, petal width, and target species labels.
        
        Returns:
            None: This method should save the trained model internally
                  or to persistent storage.
        
        Raises:
            NotImplementedError: If the method is not implemented by subclass.
        """
        raise NotImplementedError("Subclasses must implement the train method")

    @abc.abstractmethod
    def infer(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Make predictions on the provided data.
        
        Args:
            dataframe: A pandas DataFrame containing the features to predict on.
                      Expected to have columns for sepal length, sepal width,
                      petal length, and petal width measurements.
        
        Returns:
            pd.DataFrame: A DataFrame with a single 'prediction' column containing:
                Integer predictions (0=setosa, 1=versicolor, 2=virginica).
                The DataFrame should have the same number of rows as the input dataframe,
                with predictions in the same order as the input rows.
        
        Raises:
            NotImplementedError: If the method is not implemented by subclass.
        """
        raise NotImplementedError("Subclasses must implement the infer method")