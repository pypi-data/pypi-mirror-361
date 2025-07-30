# CrunchDAO Crunch Example

This package provides example utilities and base classes for CrunchDAO machine learning competitions.

## Installation

```bash
pip install crunchdao-crunch-example
```

## Usage

### Iris Classification

The `crunchdao.crunch_example.iris` package provides base classes for iris classification models:

```python
from crunchdao.crunch_example.iris import IrisModelBase
import pandas as pd

class MyIrisModel(IrisModelBase):
    def train(self, train_data: pd.DataFrame) -> None:
        # Implement your training logic here
        # train_data contains features and target labels
        pass
    
    def infer(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        # Implement your inference logic here
        # dataframe contains features to predict on
        predictions = [0, 1, 2]  # Your model predictions
        
        return pd.DataFrame({
            'prediction': predictions
        })

# Use your model
model = MyIrisModel()

# Training data with features and target
train_data = pd.DataFrame({
    'sepal_length': [5.1, 4.9, 4.7],
    'sepal_width': [3.5, 3.0, 3.2],
    'petal_length': [1.4, 1.4, 1.3],
    'petal_width': [0.2, 0.2, 0.2],
    'species': [0, 0, 0]  # 0=setosa, 1=versicolor, 2=virginica
})

model.train(train_data)

# Test data with just features
test_data = pd.DataFrame({
    'sepal_length': [6.1, 5.9],
    'sepal_width': [2.9, 3.0],
    'petal_length': [4.7, 4.2],
    'petal_width': [1.4, 1.5]
})

predictions = model.infer(test_data)
print(predictions)
```

## Package Structure

This package uses namespace packaging to allow for future expansion:

- `crunchdao.crunch_example.iris` - Iris classification utilities
- Future: `crunchdao.crunch_example.forex` - Forex prediction utilities
- Future: `crunchdao.crunch_example.crypto` - Cryptocurrency utilities

## Development

### Requirements

- Python 3.11+
- uv (for dependency management)

### Setup

```bash
# Clone the repository
git clone https://github.com/crunchdao/coordinator-setup
cd coordinator-setup/examples/crunch_examples

# Install dependencies
uv sync

# Install in development mode
uv pip install -e .
```

### Testing

```bash
uv run pytest
```

### Building

```bash
# Build the package
uv build

# Upload to PyPI (requires authentication)
uv publish
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.