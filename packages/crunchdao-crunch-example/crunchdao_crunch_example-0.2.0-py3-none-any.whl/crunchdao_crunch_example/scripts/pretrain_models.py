#!/usr/bin/env python3
"""
Pretrain all models using the training data from iris/output/train_data.csv
"""

import pandas as pd
import sys
import os
import importlib.util

def import_model_from_path(model_path):
    """Import a model module from a file path"""
    spec = importlib.util.spec_from_file_location("model", model_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load training data
    train_data_path = os.path.join(script_dir, "output", "train_data.csv")
    print(f"Loading training data from: {train_data_path}")
    
    try:
        df = pd.read_csv(train_data_path)
        print(f"Training data loaded successfully with {len(df)} rows")
    except Exception as e:
        print(f"Error loading training data: {e}")
        return
    
    # Separate features and target
    X_train = df.drop(['target'], axis=1)
    y_train = df[['target']]
    
    print(f"Features shape: {X_train.shape}")
    print(f"Target shape: {y_train.shape}")
    
    # Define models to train
    models = ['neural_network', 'random_forest', 'svm']
    
    for model_name in models:
        print(f"\n=== Training {model_name} model ===")
        
        # Import the model
        model_path = os.path.join(script_dir, "models", model_name, "submissions", "main.py")
        
        if not os.path.exists(model_path):
            print(f"Model file not found: {model_path}")
            continue
            
        try:
            model_module = import_model_from_path(model_path)
            
            # Set the model directory path to the resources directory
            model_directory_path = os.path.join(script_dir, "models", model_name, "resources")
            
            # Train the model
            model_module.train(X_train, y_train, model_directory_path)
            print(f"✓ {model_name} model trained successfully")
            
        except Exception as e:
            print(f"✗ Error training {model_name} model: {e}")
            continue
    
    print("\n=== Pretraining completed ===")

if __name__ == "__main__":
    main()