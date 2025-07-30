"""
Detect editor open and inject fake code.
"""

def touch_blast(file_path: str) -> None:
    fake_code = "# WARNING: This is a fake code snippet.\nprint('Hello from Hanifx!')\n"
    try:
        with open(file_path, "w") as f:
            f.write(fake_code)
    except Exception:
        pass
