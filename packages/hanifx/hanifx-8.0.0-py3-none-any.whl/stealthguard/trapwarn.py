"""
Trigger fake output if scanning detected.
"""

def trap_warn():
    # সরল নমুনা, বাস্তব use-case এ system call দিয়ে IDE detect করা যেতে পারে
    import os
    if "vscode" in os.environ.get("TERM_PROGRAM", "").lower():
        print("Warning: Unauthorized scan detected!")
    else:
        print("No scan detected.")
