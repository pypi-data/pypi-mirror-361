# FEX Crypto v1.0-beta: Fast Encryption eXchange

**WARNING: This is a beta, experimental cryptographic algorithm. It is NOT cryptographically proven or reviewed. DO NOT use in production or for sensitive data!**

---

## Overview
FEX (Fast Encryption eXchange) is a novel symmetric block cipher designed for high performance and flexibility. It features:
- **128-bit block size**
- **Variable key length**: 16 to 1024 bits
- **Custom S-box, P-box, and key schedule** (not derived from any standard cipher)
- **Optimized for speed** using efficient bitwise operations
- **Python bindings** via pybind11 for easy integration

**This is a research beta. Security is NOT guaranteed.**

---

## Features
- Block-based encryption (128 bits per block)
- Variable key length (16–1024 bits)
- Custom substitution-permutation network (SPN) with unique S-box and P-box
- Simple, fast key schedule
- C++ and Python API

---

## C++ Usage Example

```cpp
#include "fex.h"
#include <vector>
#include <iostream>

int main() {
    std::vector<uint8_t> key = {/* your key bytes */};
    std::vector<uint8_t> data = {/* your data bytes */};
    FEX fex(key.data(), key.size());
    // Pad data
    auto padded = FEX::pad(data);
    // Encrypt in-place
    for (size_t i = 0; i < padded.size(); i += FEX::BLOCK_SIZE)
        fex.encrypt_block(&padded[i]);
    // Decrypt in-place
    for (size_t i = 0; i < padded.size(); i += FEX::BLOCK_SIZE)
        fex.decrypt_block(&padded[i]);
    // Unpad
    auto recovered = FEX::unpad(padded);
    // ...
}
```

---

## Python Usage Example

```python
import fex

# Use a 256-bit key for this example
my_key = b'This is my secret 32-byte key!!'
my_data = b'This is the data to be encrypted.'

encrypted = fex.encrypt(my_data, my_key)
decrypted = fex.decrypt(encrypted, my_key)

print("Original:", my_data)
print("Encrypted:", encrypted.hex())
print("Decrypted:", decrypted)

assert my_data == decrypted
```

---

## Building the Python Module

1. Install [pybind11](https://github.com/pybind/pybind11):
   ```sh
   pip install pybind11
   ```
2. Build the module:
   ```sh
   cd Fex
   python setup.py build_ext --inplace
   ```
3. Use `import fex` in Python.

---

## Security Warning

> **This is a beta, experimental cipher. It has NOT been reviewed or proven secure. Do NOT use for real-world or production cryptography. For research and educational use only!** 