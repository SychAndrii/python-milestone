#!/usr/bin/env python3
#==============================================================================
#   Assignment:  Milestone 1
#
#       Author:  Andrii Sych
#     Language:  Python. Libraries used: none (all standard)
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
#                   Windows: python -m src.client.main
#                   Linux: sudo python3 -m src.client.main
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
#    This is a command-line client for the OLG Lottery Ticket Generator system.
#    It connects to a locally running IPv6 daemon over TCP, sends a JSON-based
#    ticket generation request, and handles the response accordingly.
#
#    The client prompts the user to enter:
#        - The type of lottery ticket to generate (e.g., "max", "grand", "lottario")
#        - A request ID (used to name the output file)
#        - The number of tickets to generate
#        - The port number to connect to (optional, can be prompted)
#
#    If the request is successful, the returned ticket(s) are saved to a file named
#    `ticket_<requestId>.txt` inside a `responses/` directory. If the server returns
#    an error, the client displays the error message instead.
#
#    The program is structured into three main services:
#
#        - `ConnectionService`: handles connecting to the server, sending the request,
#                               and receiving the response.
#
#        - `GenerateTicketService`: handles user prompts and saves the response to disk.
#
#        - `LoggingService`: provides styled terminal output for info and error messages.
#
#        Input:
#            - Ticket type (e.g., "max", "grand", "lottario")
#            - Request ID (string)
#            - Ticket count (integer)
#            - Port number to connect to
#
#        Output:
#            - File: `responses/ticket_<requestId>.txt` containing generated ticket(s)
#            - Error messages printed to the terminal if communication fails
#
#   Required Features Not Included: None
#
#   Known Bugs: None
#
#==============================================================================
from . import *

def main():
    loggerService = LoggingService()
    connectionService = ConnectionService(loggerService)
    ticketService = GenerateTicketService(loggerService)

    loggerService.printInfo("OLG Lottery Ticket Client")
    connectionService.connect()
    request = ticketService.promptRequest()

    try:
        response = connectionService.sendJson(request)
        ticketService.handleResponse(request, response)
    except Exception as e:
        loggerService.printError(f"Error while communicating with server: {e}")

if __name__ == "__main__":
    main()
