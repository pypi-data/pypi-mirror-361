"""
Hanifx Shadowcore - Secure API Key Encode & Decode System
Pure Python implementation, no external imports.
"""

def secure_key_encode(key: str) -> str:
    encoded_chars = []
    for i, c in enumerate(key):
        val = (ord(c) ^ 17) + (i % 10)
        val = 32 + (val % 95)
        encoded_chars.append(chr(val))
    encoded_str = ''.join(encoded_chars)
    wrapped = f"🔒{encoded_str[::-1]}🔓"
    return wrapped


def secure_key_decode(wrapped_key: str) -> str:
    if not wrapped_key.startswith("🔒") or not wrapped_key.endswith("🔓"):
        raise ValueError("Invalid encoded key format")

    core = wrapped_key[1:-1][::-1]
    decoded_chars = []
    for i, c in enumerate(core):
        val = (ord(c) - (i % 10)) % 95 + 32
        val = val ^ 17
        decoded_chars.append(chr(val))
    return ''.join(decoded_chars)


if __name__ == "__main__":
    test_key = "6014096909:AAHOG-5YD8axxw6D1a0P_-yEGlSha9bHP08"
    print("Original key:", test_key)

    enc = secure_key_encode(test_key)
    print("Encoded key:", enc)

    dec = secure_key_decode(enc)
    print("Decoded key:", dec)

    assert dec == test_key, "Decode failed!"
    print("✅ Secure key encode-decode test passed.")
