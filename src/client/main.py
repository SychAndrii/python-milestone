#!/usr/bin/env python3
#==============================================================================
#   Assignment:  Milestone 1
#
#       Author:  Andrii Sych
#     Language:  Python. Libraries used: argparse, socket
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
#                   Windows: python -m src.client.main --amount 5 --ip ::1 --port 5000
#                   Linux: sudo python3 -m src.client.main --amount 5 --ip ::1 --port 5000
#        Class:  DPI912NSA
#    Professor:  Harvey Kaduri
#     Due Date:  2025-06-04
#    Submitted:  2025-06-04
#
#-----------------------------------------------------------------------------
#
#  Collaboration:  None
#
#  Description:
#
#    This is the main entry point for the OLG Lottery Ticket Client application.
#    It parses command-line arguments for:
#        - Number of child connections to create (--amount)
#        - Server IPv6 address (--ip)
#        - Server port number (--port)
#
#    The client validates these inputs using the ConnectionService’s built-in
#    validation, ensuring:
#        - A positive integer for the number of clients
#        - A valid IPv6 address
#        - A port number between 1024 and 65535
#
#    It then launches multiple client connections using the ConnectionService,
#    each of which:
#        - Generates a random lottery ticket request
#        - Sends it to the server
#        - Saves the response to a file
#
#    This script ties together the LoggingService, ConnectionService, and
#    GenerateTicketService classes.
#
#    Input:
#        Command-line arguments:
#            --amount : number of child connections to create (default: 1)
#            --ip : IPv6 address of the server (required)
#            --port : port number of the server (required)
#
#    Output:
#        - Response file saved in 'responses' directory (one per request)
#        - Informational and error logs printed to the console
#
#   Required Features Not Included: None
#
#   Known Bugs: None
#
#==============================================================================

import argparse
from . import *

def parse_arguments(connectionService):
    """
    Parse and validate command-line arguments for the client.

    - Validates that --amount is a positive integer.
    - Validates that --ip is a valid IPv6 address.
    - Validates that --port is an integer within 1024-65535.
    - Delegates IP and port validation to the ConnectionService for consistency.

    If validation fails, prints usage information and exits the program.

    Args:
        connectionService (ConnectionService): The service used to validate IP and port.

    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="OLG Lottery Ticket Client (IPv6 Only)")

    parser.add_argument("--amount", type=int, default=1,
                        help="Number of child connections to create (positive integer). 1 by default.")
    parser.add_argument("--ip", type=str, required=True,
                        help="Server IPv6 address (IPv6 only).")
    parser.add_argument("--port", type=int, required=True,
                        help="Server port number (1024-65535).")

    args = parser.parse_args()

    if args.amount < 1:
        parser.error("--amount must be a positive integer.")

    try:
        connectionService.validateIPAndPort(args.ip, args.port)
    except Exception as e:
        parser.error(str(e))

    return args

def main():
    loggerService = LoggingService()
    connectionService = ConnectionService(loggerService)
    ticketService = GenerateTicketService(loggerService)

    args = parse_arguments(connectionService)

    loggerService.printInfo("OLG Lottery Ticket Client (IPv6 Only)")

    connectionService.batchRequest(
        clientAmount=args.amount,
        serverIP=args.ip,
        serverPort=args.port,
        clientConnectionHandler=ticketService.execute
    )

    loggerService.printInfo("Finished executing all clients")

if __name__ == "__main__":
    main()
