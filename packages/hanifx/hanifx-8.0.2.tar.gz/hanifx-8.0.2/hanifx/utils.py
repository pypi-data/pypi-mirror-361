import time
from colorama import Fore, Style, init
init(autoreset=True)

def slowprint(text, delay=0.03):
    for c in text:
        print(c, end='', flush=True)
        time.sleep(delay)
    print()

def colored(text, color):
    return getattr(Fore, color.upper(), Fore.WHITE) + text + Style.RESET_ALL
