import argparse
from ...services import TicketService
from ...services.LotteryType import LotteryType

class Console:
    """
    Command-line interface for the OLG Lottery Ticket Generator.

    This class handles user input via argparse, maps the selected game type,
    and delegates ticket generation to the TicketService.
    """

    def createTicket(self):
        """
        Parses command-line arguments and generates the requested number of
        lottery tickets using the appropriate OLG game logic.

        Command-line arguments:
            -t : Type of lottery game (max, grand, or lottario) [required]
            -n : Number of tickets to generate (default = 1) [optional]

        Output:
            Prints the generated ticket(s) to the console.
        """
        parser = argparse.ArgumentParser(
            description="Generate random lottery tickets for OLG games: Lotto Max, Daily Grand, or Lottario."
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

        selectedType = typeMapping[args.t]
        service = TicketService()

        for i in range(1, args.n + 1):
            ticket = service.generateTicket(selectedType)
            print(ticket)
