"""
Block online scanner or regex detection by obfuscation.
"""

def scan_block(text: str) -> str:
    return "".join(["*" if c.isalnum() else c for c in text])
