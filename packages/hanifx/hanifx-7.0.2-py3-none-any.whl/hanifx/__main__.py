import sys
from hanifx.splash import print_splash

def main():
    if len(sys.argv) > 1:
        name = sys.argv[1].lstrip('-')
    else:
        name = "HANIFX"
    print_splash(name)
