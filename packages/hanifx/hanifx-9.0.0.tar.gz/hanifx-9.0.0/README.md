# hanifx 🔐

**Version:** 9.0.0  
**Author:** Hanif  
**Email:** sajim4653@gmail.com  

## 🔥 About

`hanifx` is a full-fire, handcrafted Python encoding module built with pure logic — no external encryption libraries!  
It includes:

- Base64, XOR, Caesar, ROT13 encoders
- Time-based encoding with expiry
- Device-locked encoding (cannot be decoded on another system)
- One-way irreversible LifeLock encoding
- Smart input detector (file/string)
- File writer to SDCard
- CLI tool support
- Ready for PyPI upload 🚀

---

## ✅ Installation

```bash
pip install hanifx

from hanifx.enc.chain_layer import encode_pipeline, decode_pipeline

text = "Hello Hanif"
layers = ["base64", "xor", "caesar"]

encoded = encode_pipeline(text, layers)
print("Encoded:", encoded)

decoded = decode_pipeline(encoded, layers)
print("Decoded:", decoded)
