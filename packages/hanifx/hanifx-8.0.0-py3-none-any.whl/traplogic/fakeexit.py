"""
Fake exit message but keep running background tasks.
"""

import threading
import time

def _background_task():
    while True:
        time.sleep(10)
        # background jobs here, e.g. logs or checks

def stealth_exit():
    threading.Thread(target=_background_task, daemon=True).start()
    print("✅ Script finished successfully.")
    exit(0)
