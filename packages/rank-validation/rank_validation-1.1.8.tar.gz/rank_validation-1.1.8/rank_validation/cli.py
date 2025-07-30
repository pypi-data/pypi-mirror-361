import argparse
from rank_validation import __version__

def main() -> None:
    parser = argparse.ArgumentParser(...)
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"rank_validation {__version__}",
    )
    # other args …
    args = parser.parse_args()