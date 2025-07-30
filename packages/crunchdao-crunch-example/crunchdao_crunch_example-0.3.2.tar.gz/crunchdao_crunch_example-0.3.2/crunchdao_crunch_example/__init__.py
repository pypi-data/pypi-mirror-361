"""
CrunchDAO Crunch Example Package

This package provides iris classification utilities including model implementations, 
and utility scripts for CrunchDAO competitions.

Structure:
- models/: Example model implementations (neural_network, random_forest, svm)  
- scripts/: Utility scripts for training and model management

Note: The IrisModelBase abstract class is available via:
    from crunchdao.crunch_example.iris import IrisModelBase

Usage:
    # Import base class from namespace package
    from crunchdao.crunch_example.iris import IrisModelBase
    
    # Access models and scripts directly
    from crunchdao_crunch_example.models import neural_network
    from crunchdao_crunch_example.scripts import pretrain_models
"""

__version__ = "0.3.2"