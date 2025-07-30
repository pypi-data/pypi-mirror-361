"""
Optional UID binding for encoded keys.
"""

def check_uid(uid: str, allowed_uids: list) -> bool:
    return uid in allowed_uids
