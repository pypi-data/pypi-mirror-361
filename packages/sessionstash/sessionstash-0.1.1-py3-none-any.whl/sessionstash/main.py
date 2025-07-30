import argparse
import sys
from pathlib import Path

from .core import save_workspace, load_workspace


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="sessionstash",
        description="Snapshot and restore Python interpreter sessions.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # save sub‑command
    save_parser = subparsers.add_parser("save", help="Save current session to a file.")
    save_parser.add_argument("file", type=Path, help="Output pickle file.")

    # load sub‑command
    load_parser = subparsers.add_parser("load", help="Load a session from a file.")
    load_parser.add_argument("file", type=Path, help="Pickle file to load.")
    load_parser.add_argument(
        "--shell",
        action="store_true",
        help="Enter an IPython shell after loading the session (if IPython is available).",
    )

    return parser.parse_args()


def cli_entry() -> None:
    args = _parse_args()

    if args.command == "save":
        save_workspace(args.file)
        return

    if args.command == "load":
        load_workspace(args.file)
        if args.shell:
            try:
                import IPython  # type: ignore

                IPython.embed(colors="neutral")
            except ImportError:
                print("IPython is not installed. Session loaded; falling back to standard REPL.")
                import code

                code.interact(local=dict(globals(), **locals()))
        return

    # Should never reach here
    sys.exit("Unknown command")


if __name__ == "__main__":
    cli_entry()
