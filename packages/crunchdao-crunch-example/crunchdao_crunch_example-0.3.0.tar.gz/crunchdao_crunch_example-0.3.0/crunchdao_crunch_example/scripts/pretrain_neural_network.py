#!/usr/bin/env python3
"""
Pretrain only the neural network model using the training data from iris/output/train_data.csv
"""

import pandas as pd
import numpy as np
import pickle
import os
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

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
    y_train = df['target']
    
    print(f"Features shape: {X_train.shape}")
    print(f"Target shape: {y_train.shape}")
    
    print("\n=== Training Neural Network model ===")
    
    # Create resources directory if it doesn't exist
    resources_dir = os.path.join(script_dir, "models", "neural_network", "resources")
    os.makedirs(resources_dir, exist_ok=True)
    
    # Feature scaling (critical for neural networks)
    # Don't use feature names to avoid conflicts during inference
    scaler = StandardScaler()
    X_train_values = X_train.values  # Convert to numpy array to remove feature names
    X_scaled = scaler.fit_transform(X_train_values)
    
    # Train Multi-Layer Perceptron (Neural Network)
    model = MLPClassifier(
        hidden_layer_sizes=(100, 50),  # Two hidden layers
        activation='relu',
        solver='adam',
        alpha=0.01,  # L2 regularization
        learning_rate='adaptive',
        max_iter=1000,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.1
    )
    
    print("Training neural network...")
    model.fit(X_scaled, y_train)
    
    # Save model and scaler
    model_path = os.path.join(resources_dir, "neural_network_model.pkl")
    scaler_path = os.path.join(resources_dir, "scaler.pkl")
    
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    
    print(f"✓ Neural Network model trained and saved to {resources_dir}")
    print(f"  - Model saved: {model_path}")
    print(f"  - Scaler saved: {scaler_path}")
    
    # Verify the saved files
    if os.path.exists(model_path) and os.path.exists(scaler_path):
        print("✓ All files saved successfully")
    else:
        print("✗ Error: Some files were not saved properly")
    
    print("\n=== Neural Network pretraining completed ===")

if __name__ == "__main__":
    main()