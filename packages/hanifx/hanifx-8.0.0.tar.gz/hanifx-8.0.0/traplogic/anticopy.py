"""
Detect cloning and warn user or disable code.
"""

def anti_copy(file_path: str) -> None:
    try:
        with open(file_path, "r") as f:
            content = f.read()
        if "copy" in file_path.lower():
            with open(file_path, "w") as f:
                f.write("# Warning: Copy detected. Access denied.\n")
    except Exception:
        pass
