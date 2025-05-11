# src/mypkg/cli.py (argparse version)
import argparse
from .player import MusicPlayer

def main():
    parser = argparse.ArgumentParser(prog="mypkg")
    parser.add_argument("input", help="Input value")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        print(f"[DEBUG] Received input: {args.input}")
    print(do_something(args.input))

if __name__ == "__main__":
    main()
