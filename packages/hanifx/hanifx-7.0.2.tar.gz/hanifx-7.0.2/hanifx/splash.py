from hanifx.utils import colored, slowprint
import time
import random

def print_splash(name):
    username = ' '.join(name.upper())
    banner = f"▂▃▅▆▇█▓▒░ {username} ░▒▓█▇▆▅▃▂"

    print(colored("hanifx://boot_sequence --start", "cyan"))
    time.sleep(0.5)
    for line in [
        "[☠] Bypassing firewall layer...",
        "[☠] Injecting shell loader into RAM...",
        "[☠] Unlocking core module stack...\n"
    ]:
        slowprint(colored(line, "green"), 0.02)

    slowprint(colored(banner, "yellow"), 0.01)

    print(colored(r"""
             .-'''-.
            / .===. \
            \/ 6 6 \/
            ( \___/ )
       ___ooo__V__ooo___
""", "magenta"))

    print(colored("Welcome, Operator.", "cyan"))
    print(">> Session ID:", colored(f"#HX-{random.randint(100,999)}-{random.choice(['X','Z','K'])}-MATRIX", "green"))
    print(">> Terminal mode:", colored("Hacker CLI (offline)", "red"))
    print()
    print(colored("> Type `hanifx --start-attack` to begin.", "yellow"))
