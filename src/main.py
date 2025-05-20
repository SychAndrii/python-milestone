import argparse
from .presentation.console import Console
from .presentation.socket import SocketDaemon

def main():
    parser = argparse.ArgumentParser(
        description="OLG Lottery Ticket Generator (Console or Socket mode)"
    )

    parser.add_argument(
        "-m", "--mode",
        choices=["console", "socket"],
        default="console",
        help="Startup mode: 'console' for CLI interaction, 'socket' to run as a TCP server (default: console)"
    )

    args, remaining_args = parser.parse_known_args()

    if args.mode == "console":
        Console().createTicket(remaining_args)
    elif args.mode == "socket":
        daemon = SocketDaemon(
            "nobody",
            "nogroup",
            "/tmp/daemon.pid"
        )
        daemon.start()
    else:
        parser.error(f"Unknown mode: {args.mode}")

if __name__ == "__main__":
    main()
