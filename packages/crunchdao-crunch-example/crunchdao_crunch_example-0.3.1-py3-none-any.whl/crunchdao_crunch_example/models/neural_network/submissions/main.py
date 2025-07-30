#!/usr/bin/env python3
"""
Neural Network Model for Iris Classification
Implements CrunchDAO code interface with class-based model.
"""
import logging
import pandas as pd
import pickle
import os
import typing
from crunchdao.crunch_example.iris import IrisModelBase

logger = logging.getLogger(__name__)


class NeuralNetworkModel(IrisModelBase):
    """
    Neural Network Model for Iris Classification
    """
    
    def train(self, train_data: pd.DataFrame):
        """
        Train Neural Network model - using pretrained models, so this is empty.
        """
        # Using pretrained models, so training is not needed
        pass
    
    def infer(self, payload_stream: pd.DataFrame) -> pd.DataFrame:
        """
        Make predictions using trained Neural Network model.
        
        Args:
            payload_stream: DataFrame with test features, each row is one sample
            
        Returns:
            pandas DataFrame with prediction results, row indices preserved
        """
        
        # Get resource path from environment variable
        resource_path = "/workspace/resources"
        
        # Load model and scaler
        model_path = os.path.join(resource_path, "neural_network_model.pkl")
        scaler_path = os.path.join(resource_path, "scaler.pkl")
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        
        logger.info(f"Received DataFrame with shape: {payload_stream.shape}")
        logger.info(f"DataFrame columns: {payload_stream.columns.tolist()}")
        logger.info(f"First few rows:\n{payload_stream.head()}")
        
        # Ensure we have a DataFrame
        if not isinstance(payload_stream, pd.DataFrame):
            logger.error(f"Expected DataFrame, got {type(payload_stream)}")
            return pd.DataFrame({
                'prediction': []
            })
        
        X_test = payload_stream.copy()
        
        # Clean the DataFrame - remove any header rows and ensure numeric data
        try:
            # Reset column names to avoid feature name conflicts (expected 4 features)
            X_test.columns = range(len(X_test.columns))
            
            # Convert all data to numeric
            X_test_numeric = X_test.apply(pd.to_numeric, errors='coerce')
            
            # Check for rows with any NaN values
            clean_mask = ~X_test_numeric.isnull().any(axis=1)
            X_test_clean = X_test_numeric[clean_mask]
            
            if len(X_test_clean) == 0:
                logger.warning("No valid numeric data found in DataFrame")
                return pd.DataFrame({
                    'prediction': [],
                    'sample_id': [],
                    'model_name': []
                })
            
            logger.info(f"Cleaned DataFrame shape: {X_test_clean.shape}")
            logger.info(f"Processing {len(X_test_clean)} valid samples out of {len(X_test)} total")
            
            # Scale features - convert to numpy array to avoid feature name issues
            X_values = X_test_clean.values  # Convert DataFrame to numpy array
            X_scaled = scaler.transform(X_values)
            
            # Make predictions for all rows in the DataFrame
            predictions = model.predict(X_scaled)
            
            # Create result DataFrame with single prediction column
            result_df = pd.DataFrame({
                'prediction': [int(pred) for pred in predictions]
            })
            
            logger.info(f"Generated {len(predictions)} predictions")
            return result_df
                    
        except Exception as e:
            logger.error(f"Error processing DataFrame: {e}")
            return pd.DataFrame({
                'prediction': []
            })