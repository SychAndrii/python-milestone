#!/usr/bin/env python3

import argparse
from .presentation.console import Console
from .presentation.socket import SocketDaemon

def main():
    """
    Entry point for OLG Lottery Ticket Generator.

    Depending on the selected mode (`console` or `socket`), it starts the appropriate interface.

    Example usage:
        python -m src.main --mode console
    """

    parser = argparse.ArgumentParser(
        description="OLG Lottery Ticket Generator (Console or Socket mode)"
    )

    parser.add_argument(
        "-m", "--mode",
        choices=["console", "socket"],
        default="console",
        help="Startup mode: 'console' for CLI interaction, 'socket' to run as a TCP server (default: console)"
    )

    args, _ = parser.parse_known_args()

    if args.mode == "console":
        Console().createTicket()
    elif args.mode == "socket":
        SocketDaemon().start()
    else:
        parser.error(f"Unknown mode: {args.mode}")

if __name__ == "__main__":
    main()