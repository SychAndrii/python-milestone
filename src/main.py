#!/usr/bin/env python3
#==============================================================================
#   Assignment:  Milestone 0
#
#       Author:  Andrii Sych
#     Language:  Python. Libraries used: sortedcontainers, argparse
#   To Compile:
#              - Install virtual environment support: 
#                   pip install venv
#              - Activate virtual environment:
#                   Windows: venv\Scripts\activate.bat
#                   Linux/Mac: source venv/bin/activate
#              - Install dependencies: pip install -r requirements.txt
#              - Run the program: python -m src.main (see this file for flag details)
#        Class:  DPI912NSA
#    Professor:  Harvey Kaduri
#     Due Date:  2025-05-12
#    Submitted:  2025-05-12
#
#-----------------------------------------------------------------------------
#
#  Collaboration:  None
#
#  Description:
#
#    This program is an OLG Lottery Ticket Generator implemented using 
#    Domain-Driven Design (DDD) principles. It generates random lottery 
#    tickets for one of four supported Ontario Lottery and Gaming 
#    Corporation (OLG) games:
#
#       - Lotto Max: 7 unique numbers between 1 and 50
#       - Daily Grand: 5 unique numbers between 1 and 49 plus 1 Grand Number between 1 and 7
#       - Lottario: 6 unique numbers between 1 and 45
#
#    The project structure separates domain models (Pool, Ticket), 
#    application services (TicketService), factories (ITicketFactory and 
#    concrete factories), and presentation layer (command-line interface).
#
#    Users interact with the program via command-line arguments to select 
#    the game type and number of tickets to generate.
#
#        Input:
#            Command-line arguments:
#                -t : type of lottery ("max", "grand", or "lottario") [required]
#                -n : number of tickets to generate (default = 1) [optional]
#
#        Output:
#            For each generated ticket:
#                - A list of numbers is printed to the console.
#                - If the game has multiple number pools, each pool is printed separately.
#
#    Algorithm:
#        The program maps the selected lottery type to a specific factory class.
#        Each factory creates a Ticket object containing Pool configurations.
#        Each Pool randomly selects the specified number of unique numbers 
#        from the defined range. The Ticket object prints the final ticket numbers.
#
#   Required Features Not Included: None
#
#   Known Bugs: None
#
#==============================================================================

import argparse
from .services import *

def main():
    """
    OLG Lottery Ticket Generator

    This program generates random lottery tickets for one of four supported OLG lottery games:

    - Lotto Max: 7 unique numbers from 1 to 50
    - Daily Grand: 5 unique numbers from 1 to 49 plus 1 Grand Number from 1 to 7
    - Lottario: 6 unique numbers from 1 to 45

    Users select the game type and how many tickets to generate using command-line arguments.

    Example usage:
        python lottery.py -t max -n 5
    """

    parser = argparse.ArgumentParser(
        description="Generate random lottery tickets for OLG games: Lotto Max, Lotto 6/49, Daily Grand, or Lottario."
    )

    parser.add_argument(
        "-t",
        choices=["max", "grand", "lottario"],
        required=True,
        help="Type of lottery to generate: max, grand, or lottario (required)"
    )

    parser.add_argument(
        "-n",
        type=int,
        default=1,
        help="Number of tickets to generate (must be 1 or more; default is 1)"
    )

    args = parser.parse_args()

    if args.n < 1:
        parser.error("The number of tickets (-n) must be at least 1.")

    typeMapping = {
        "max": LotteryType.LOTTO_MAX,
        "grand": LotteryType.DAILY_GRAND,
        "lottario": LotteryType.LOTTARIO
    }

    selected_type = typeMapping[args.t]
    service = TicketService()

    for i in range(1, args.n + 1):
        ticket = service.generateTicket(selected_type)
        print(ticket)

if __name__ == "__main__":
    main()