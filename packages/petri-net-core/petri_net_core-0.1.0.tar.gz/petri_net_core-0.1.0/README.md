# Petri Net Core

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