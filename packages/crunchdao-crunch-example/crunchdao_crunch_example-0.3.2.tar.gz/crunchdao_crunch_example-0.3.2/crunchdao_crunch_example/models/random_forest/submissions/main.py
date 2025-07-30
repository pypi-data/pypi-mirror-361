#!/usr/bin/env python3
"""
Random Forest Model for Iris Classification
Implements CrunchDAO code interface with class-based model.
"""
import logging
import pandas as pd
import numpy as np
import pickle
import os
import typing
from sklearn.preprocessing import StandardScaler
from crunchdao.crunch_example.iris import IrisModelBase

logger = logging.getLogger(__name__)


class RandomForestModel(IrisModelBase):
    """
    Random Forest Model for Iris Classification
    """
    
    def train(self, train_data: pd.DataFrame):
        """
        Train Random Forest model - using pretrained models, so this is empty.
        """
        pass
    
    def infer(self, payload_stream: typing.Iterator[pd.DataFrame]):
        """
        Make predictions using trained Random Forest model.
        
        Args:
            payload_stream: Iterator of test features DataFrames
            
        Returns:
            Iterator of prediction dictionaries
        """
        
        # Get resource path from environment variable
        resource_path = os.environ.get('RESOURCE_PATH')
        if not resource_path:
            raise ValueError("RESOURCE_PATH environment variable is not set")
        
        resources_dir = os.path.join(resource_path, "random_forest", "resources")
        
        # Load model and scaler
        model_path = os.path.join(resources_dir, "random_forest_model.pkl")
        scaler_path = os.path.join(resources_dir, "scaler.pkl")
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        
        # Process each DataFrame in the stream
        for X_test in payload_stream:
            # Scale features
            X_scaled = scaler.transform(X_test)
            
            # Make predictions
            predictions = model.predict(X_scaled)
            
            # Yield prediction as dict
            yield {"prediction": int(predictions[0])}