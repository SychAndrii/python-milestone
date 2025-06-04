#!/usr/bin/env python3
#==============================================================================
#   Assignment:  Milestone 3
#
#       Author:  Andrii Sych
#     Language:  Python. Libraries used: argparse, os, socket, signal
#   To Compile:
#              - Install virtual environment support: 
#                   Windows: python -m venv venv
#                   Linux: sudo python3 -m venv venv
#              - Activate virtual environment:
#                   Windows: venv\Scripts\activate.bat
#                   Linux: source venv/bin/activate
#              - Install dependencies:
#                   Windows: pip install -r requirements.txt
#                   Linux: sudo pip install --break-system-packages -r requirements.txt
#              - Run the program: 
#                   Windows: python -m src.server.main -m socket start
#                   Linux: sudo python3 -m src.server.main -m socket start
#        Class:  DPI912NSA
#    Professor:  Harvey Kaduri
#     Due Date:  2025-06-03
#    Submitted:  2025-06-03
#
#-----------------------------------------------------------------------------
#
#  Collaboration:  None
#
#  Description:
#
#    This program is an OLG Lottery Ticket Generator implemented using 
#    Domain-Driven Design (DDD) principles. It generates random lottery 
#    tickets for one of three supported Ontario Lottery and Gaming 
#    Corporation (OLG) games:
#
#       - Lotto Max: 7 unique numbers between 1 and 50
#       - Daily Grand: 5 unique numbers between 1 and 49 plus 1 Grand Number between 1 and 7
#       - Lottario: 6 unique numbers between 1 and 45
#
#    The application supports two modes of interaction through its presentation layer:
#
#       1. Console Mode — one-time execution mode using command-line arguments.
#          - The user provides ticket type, request ID, and count via CLI.
#          - The program generates the requested tickets and prints them to the terminal.
#
#       2. Socket Server Mode — a persistent TCP socket server that listens for
#          client requests over IPv6.
#          - Takes "start" or "stop" as arguments to control the daemon.
#          - Accepts JSON-formatted requests from clients, each containing:
#                {
#                  "type": "max" | "grand" | "lottario",
#                  "requestId": "<string>",
#                  "count": <integer>
#                }
#          - Forks a child process to handle each request concurrently.
#          - Sends back a JSON response containing the generated tickets.
#          - Uses SIGCHLD to reap exited children and prevent zombies.
#
#    Both modes delegate ticket generation to a shared controller class:
#    `GenerateTicketController`. This controller encapsulates presentation logic:
#        - Mapping the input string to the correct lottery type.
#        - Generating the requested number of tickets using domain services.
#        - Constructing a `GenerationResponse` object.
#
#    Input:
#        - Console mode: Command-line arguments
#        - Socket mode: JSON-formatted request sent over an IPv6 socket
#
#    Output:
#        - Console mode: Ticket(s) printed to the terminal
#        - Socket mode: JSON-formatted response sent to client
#
#    Algorithm:
#        - Console mode: parses CLI arguments, calls GenerateTicketController, prints tickets.
#        - Socket server mode: listens on IPv6, forks children to handle requests,
#          generates tickets, and sends back responses.
#
#   Required Features Not Included: None
#
#   Known Bugs: None
#
#==============================================================================

import sys
import argparse
from .presentation.console import Console
from .presentation.socket import SocketServer


def main():
    initial_parser = argparse.ArgumentParser(add_help=False)
    initial_parser.add_argument("-m", "--mode", choices=["console", "socket"])
    args, remaining_args = initial_parser.parse_known_args()

    if args.mode is None:
        print("Usage:")
        print("  -m console   Run in command-line mode")
        print("  -m socket    Run as a TCP socket server daemon")
        print("\nExamples:")
        print("  python3 -m src.server.main -m console -t max --id abc123 -n 2")
        print("  python3 -m src.server.main -m socket start")
        print("  python3 -m src.server.main -m socket stop")
        sys.exit(0)

    if args.mode == "console":
        Console().createTicket(remaining_args)

    elif args.mode == "socket":
        if len(remaining_args) == 0 or remaining_args[0] not in ["start", "stop"]:
            print("Usage: -m socket [start|stop]")
            sys.exit(1)

        command = remaining_args[0]
        try:
            daemon = SocketServer("nobody", "nogroup")

            if command == "start":
                daemon.start()
            elif command == "stop":
                daemon.stop()

        except RuntimeError as e:
            print(f"❌ {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n❌ User cancelled.")
            sys.exit(1)


if __name__ == "__main__":
    main()
