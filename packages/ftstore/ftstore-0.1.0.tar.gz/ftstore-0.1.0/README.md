# ftstore - Dataset Management for Machine Learning

[![PyPI Version](https://img.shields.io/pypi/v/ftstore.svg)](https://pypi.org/project/ftstore/)
[![Python Versions](https://img.shields.io/pypi/pyversions/ftstore.svg)](https://pypi.org/project/ftstore)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`ftstore` is a Python package for managing and loading local datasets in machine learning projects, inspired by scikit-learn's dataset API.

## Features

- 🗂️ Organize datasets in a structured directory
- ⚡️ Fast loading of CSV, Parquet, Feather, HDF5 and other formats
- 🔄 Automatic dataset caching for faster reloads
- 🌐 Auto-download datasets from remote sources
- 📊 Metadata management with JSON files

## Installation

```bash
pip install ftstore
```

For full format support:

```bash
pip install ftstore[full]
```

## Quick Start

```python
from ftstore import load_data

# Load a dataset
iris = load_data("iris")

# Access features and target
print("Features:", iris.feature_names)
print("Target:", iris.target_name)
print("Data shape:", iris.data.shape)

# Load as DataFrame
df = load_data("iris", as_frame=True)

# Load as NumPy arrays
X, y = load_data("breast_cancer", return_X_y=True)
```

## Documentation

See the [Getting Started Guide](docs/getting_started.md) for detailed usage instructions.