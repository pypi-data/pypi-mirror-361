"""
Wrap token inside an innocent-looking function.
"""

def silent_lock(token: str) -> str:
    code = f'''
def get_secret():
    return "{token}"
'''
    return code
