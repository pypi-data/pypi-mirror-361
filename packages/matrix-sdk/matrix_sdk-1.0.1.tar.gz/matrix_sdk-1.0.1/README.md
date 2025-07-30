# Matrix SDK

A Python SDK for AI, System and Web developers to interact easily with the Matrix repository to build and convert their codes to API endpoints.

## Installation

```bash
pip install matrix-sdk
```

## Quick Start

```python
import matrix
from matrix.utils import auxiliary
from matrix.manager import test

# Check package availability
print(f"TensorFlow available: {auxiliary.is_tf_available()}")
print(f"PyTorch available: {auxiliary.is_torch_available()}")
print(f"Scikit-learn available: {auxiliary.is_sklearn_available()}")
```

## Features

- **Package Management**: Easy package availability checking
- **Version Control**: Runtime dependency version validation
- **Project Management**: Tools for managing Matrix repository projects
- **Testing Framework**: Automated testing utilities
- **Cross-Platform**: Works on Python 3.6+

## Requirements

- Python 3.6 or higher
- requests>=2.31.0
- tqdm>=4.66.2
- packaging>=20.0

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


