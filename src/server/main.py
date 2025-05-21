#!/usr/bin/env python3
#==============================================================================
#   Assignment:  Milestone 1
#
#       Author:  Andrii Sych
#     Language:  Python. Libraries used: argparse, psutil
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
#                   Windows: python -m src.server.main -h
#                   Linux: sudo python3 -m src.server.main -h
#        Class:  DPI912NSA
#    Professor:  Harvey Kaduri
#     Due Date:  2025-05-21
#    Submitted:  2025-05-21
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
#       1. **Console** — one-time execution mode using command-line arguments.
#       2. **SocketDaemon** — a persistent TCP daemon that listens for client requests over IPv6.
#
#    Both modes delegate ticket generation to a shared controller class:
#    `GenerateTicketController`. This controller encapsulates common presentation logic such as:
#        - Mapping the input string to the correct lottery type
#        - Generating the requested number of tickets using domain services
#        - Constructing a `GenerationResponse` object
#
#    This structure avoids duplication and promotes separation of concerns across:
#        - Domain models (`Pool`, `Ticket`)
#        - Application services (`TicketService`)
#        - Presentation interfaces (`Console`, `SocketDaemon`)
#
#        Input:
#            Console Mode:
#                Command-line arguments:
#                    -t : type of lottery ("max", "grand", or "lottario") [required]
#                    --id : request identifier [required]
#                    -n : number of tickets to generate (default = 1) [optional]
#
#            Socket Mode:
#                JSON request sent over IPv6 socket containing:
#                    {
#                      "type": "max" | "grand" | "lottario",
#                      "requestId": "<string>",
#                      "count": <integer>
#                    }
#
#        Output:
#            Console Mode:
#                - Ticket(s) printed to the terminal.
#
#            Socket Mode:
#                - Response sent back to client.
#
#    Algorithm:
#        The program maps the selected lottery type to a specific factory class.
#        Each factory creates a Ticket object containing Pool configurations.
#        Each Pool randomly selects the specified number of unique numbers 
#        from the defined range. The Ticket object prints or returns the ticket.
#
#   Required Features Not Included: None
#
#   Known Bugs: None
#
#==============================================================================
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
        print("  python3 -m src.main -m console -t max --id abc123 -n 2")
        print("  python3 -m src.main -m socket")
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
