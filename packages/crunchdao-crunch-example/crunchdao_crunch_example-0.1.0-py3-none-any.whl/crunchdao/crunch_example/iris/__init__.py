"""
Iris classification utilities for CrunchDAO competitions.

This package provides base classes, model implementations, and utilities for building 
iris classification models that integrate with the CrunchDAO platform.

Available submodules:
- model_base: Base class for iris models
- models: Example model implementations (neural_network, random_forest, svm)
- scripts: Utility scripts for training and model management
"""

from .model_base import IrisModelBase

__all__ = ["IrisModelBase"]
__version__ = "0.1.0"