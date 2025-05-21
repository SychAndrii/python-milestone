import sys
import argparse
from .presentation.console import Console
from .presentation.socket import SocketDaemon

def main():
    initial_parser = argparse.ArgumentParser(add_help=False)
    initial_parser.add_argument("-m", "--mode", choices=["console", "socket"])
    args, remaining_args = initial_parser.parse_known_args()

    if args.mode is None:
        print("Usage:")
        print("  -m console   Run in command-line mode")
        print("  -m socket    Run as a TCP socket daemon")
        print("\nExamples:")
        print("  python -m src.main -m console -t max --id abc123 -n 2")
        print("  python -m src.main -m socket")
        sys.exit(0)

    if args.mode == "console":
        Console().createTicket(remaining_args)

    elif args.mode == "socket":
        try:
            daemon = SocketDaemon(
                username="nobody",
                groupname="nogroup",
                pidFile="/tmp/ticket_daemon.pid"
            )
            daemon.start()

        except RuntimeError as e:
            print(f"❌ {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n❌ User cancelled.")
            sys.exit(1)

if __name__ == "__main__":
    main()
