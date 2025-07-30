"""
Encode string to look like common config or random data.
"""

def ghost_mask(data: str) -> str:
    fake = "[config]\n"
    fake += "\n".join(f"{chr(65+i)}={ord(c)%10}" for i, c in enumerate(data))
    return fake
