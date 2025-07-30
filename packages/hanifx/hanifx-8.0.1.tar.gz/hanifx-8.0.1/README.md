# Hanifx

Next-gen encoding and security toolkit for Python.

## Features

- Secure key encoding & decoding
- Anti-scan stealth guards
- Clone detection traps
- Runtime internal decode support
- Ready for PyPI upload

## Installation

```bash
pip install hanifx


#....................#

from hanifx.shadowcore.securekey import secure_key_encode, secure_key_decode

encoded = secure_key_encode("your_api_key")
print(encoded)

decoded = secure_key_decode(encoded)
print(decoded)
