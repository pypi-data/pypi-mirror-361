"""
Internal runtime decoder for secure keys.
"""

from hanifx.shadowcore.securekey import secure_key_decode

def load_key(encoded_key: str) -> str:
    # Could add UID bind or fallback here if needed
    return secure_key_decode(encoded_key)
