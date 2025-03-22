# Entropy Lattice

An advanced cryptographic framework based on entropic pattern mathematics and lattice operations.

## Overview

EntropyLattice provides a framework for performing entropic mathematical operations on pattern lattices. It implements a suite of non-commutative lattice operators, entropic values, and pattern transformations that can be used for cryptographic applications, data obfuscation, and scientific computing.

The library is designed with an elegant mathematical foundation inspired by information theory and lattice-based mathematics.
Note: This is for evaluation NOT production. I'm already working on a fix for the issues with this one. So, hold up on downloading it until I do. :)
3/18/2025 - Taking a bit longer than I thought because I'm making sure the randomness was valid; the initial version was missing some values but as noted in the Evals, what I added in passed, the Dieharder 10v10.
I'm doing another pass at the functions and then doing tests to make sure nothing is broke.
3/22/2025 - The current issues, and more are solved. Now it's just getting it to build correctly.

## Features

- **Non-Commutative Lattice Operations**: Mathematical operations that don't follow the commutative property, providing unique transformations
- **Entropic Values**: A system for representing entropic relationships between mathematical values
- **Pattern Transformations**: Information-theoretic transformations including superposition, entanglement, and interference
- **Basic Encoding**: Techniques to protect data and algorithms
- **Cryptographic Utilities**: Key generation, validation, and secure hash functions

## Installation

```bash
pip install entropy-lattice
```

### Requirements

- Python 3.8+
- NumPy
- Matplotlib (for visualization examples)

## Usage Examples

### Basic Pattern Operations

```python
from lattice_framework import PatternTransformations, normalize_pattern

# Create test patterns
pattern1 = [0.1, 0.2, 0.3, 0.4, 0.5]
pattern2 = [0.5, 0.4, 0.3, 0.2, 0.1]

# Normalize a pattern
normalized = normalize_pattern(pattern1, 0.0, 1.0)
print(f"Normalized: {normalized}")

# Apply transformations
superposition = PatternTransformations.entropic_superposition(pattern1, pattern2)
entanglement = PatternTransformations.entropic_entangle(pattern1, pattern2)
interference = PatternTransformations.entropic_interference(pattern1, pattern2)

print(f"Superposition: {superposition}")
print(f"Entanglement: {entanglement}")
print(f"Interference: {interference}")
```

### Cryptographic Applications

```python
from lattice_framework import LatticeOperations, PatternTransformations

# Generate cryptographic key material
seed = 12345
key_material = LatticeOperations.generate_key_material(seed, length=32)
print(f"Key: {key_material['key_hex']}")

# Create an entropic hash
pattern = [0.1, 0.2, 0.3, 0.4, 0.5]
hash_value = PatternTransformations.entropic_hash(pattern)
print(f"Hash: {hash_value}")
```

### Basic Encoding

```python
from lattice_framework import EntropyEncoder

# Create a pattern
pattern = [0.1, 0.2, 0.3, 0.4, 0.5]

# Initialize an encoder
encoder = EntropyEncoder(entropy_seed=42)

# Encode the pattern
encoded = encoder.pattern_to_entropic_code(pattern)
print(f"Encoded pattern length: {len(encoded)} characters")
```

## Applications

EntropyLattice can be used for:

- Secure data storage and transmission
- Cryptographic key generation
- Tamper-evident data structures
- Scientific computing with information-theoretic properties

## Premium Version

For advanced features including:
- Advanced encoding capabilities
- Post-quantum cryptographic applications
- Machine learning model protection
- Self-randomizing calculations
- Context-sensitive execution

Please contact Occybyte for licensing information.

## License

Proprietary - Copyright © 2025 Occybyte

## Author

Datorien Laurae Anderson 
