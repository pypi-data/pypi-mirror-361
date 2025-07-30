"""
Deep byte-level scramble encode of the token.
"""

def xray_lock(token: str) -> str:
    res = []
    for c in token:
        res.append(str(ord(c) ^ 123))  # simple XOR 123
    return " ".join(res)

def xray_unlock(encoded: str) -> str:
    parts = encoded.split()
    chars = [chr(int(p) ^ 123) for p in parts]
    return "".join(chars)
