# Petri Net Core

<!-- Triggering GitHub Actions workflow test -->
Core Petri net simulation and analysis framework for modeling discrete event systems.

## About

This repository contains the core Petri net functionality for simulation and analysis. It provides:

- **Basic Petri Net Implementation** (`petrinet/`)
- **Object Petri Net Support** (`object_petrinet/`)
- **Validation and Schema Support**
- **Testing Framework**

## Installation

### From Source
```bash
git clone https://github.com/lhcnetop/petri_net.git
cd petri_net
pip install -e .
```

### Development Installation
```bash
pip install -e .[dev]
```

## Usage

```python
from petrinet.pnet import PetriNet
from object_petrinet.opnet import ObjectPetriNet

# Create and use Petri nets
```

## Testing

Run tests with:
```bash
# Run all tests
python -m unittest discover -p "*_tests.py" -v

# Run specific test files
python -m unittest tests/pnet_tests.py
python -m unittest tests/opnet_tests.py
```

## Related Projects

- **[mRNA Petri Net](https://github.com/lhcnetop/mrna_petrinet)**: mRNA translation modeling using this core framework

## License

Apache-2.0 License

## Release & PyPI Publishing

PyPI publishing is now fully automated and only happens when you push a version tag (e.g., v0.2.0) to the repository. This ensures that only intentional releases are published.

### How to release a new version:
1. Bump the version in `pyproject.toml`.
2. Commit and push your changes to `main`.
3. Create and push a tag matching the new version:
   ```sh
   git tag v0.2.0
   git push origin v0.2.0
   ```
4. The GitHub Actions workflow will build and publish the package to PyPI automatically.