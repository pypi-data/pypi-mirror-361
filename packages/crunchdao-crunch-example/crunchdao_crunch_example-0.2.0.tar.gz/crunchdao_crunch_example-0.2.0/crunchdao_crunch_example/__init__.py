"""
CrunchDAO Crunch Example Package

This package provides iris classification utilities including base classes, 
model implementations, and utility scripts for CrunchDAO competitions.

Structure:
- model_base.py: IrisModelBase abstract class
- models/: Example model implementations (neural_network, random_forest, svm)
- scripts/: Utility scripts for training and model management

Usage:
    from crunchdao_crunch_example import IrisModelBase
    
    class MyModel(IrisModelBase):
        def train(self, train_data): ...
        def infer(self, dataframe): ...
"""

from .model_base import IrisModelBase

__all__ = ["IrisModelBase"]
__version__ = "0.2.0"