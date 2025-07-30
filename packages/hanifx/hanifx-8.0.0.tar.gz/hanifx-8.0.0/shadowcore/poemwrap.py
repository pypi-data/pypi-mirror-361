"""
Encode token into a Bengali/English poem disguised string.
"""

def poem_encode(token: str) -> str:
    lines = [
        "তুমি আকাশের তারারা,",
        "চুপচাপ বাতাসের মাঝে,",
        token,
        "মধুর স্বপ্নের আঁধারে,",
        "লুকানো গোপন কথা।"
    ]
    return "\n".join(lines)
