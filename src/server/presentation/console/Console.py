import argparse
from ..GenerateTicketController import GenerateTicketController


class Console:
    """
    Command-line interface for the OLG Lottery Ticket Generator.

    This class handles user input via argparse, maps the selected game type,
    and delegates ticket generation to the TicketService.
    """

    def createTicket(self, argv):
        """
        Parses command-line arguments and generates the requested number of
        lottery tickets using the appropriate OLG game logic.

        Command-line arguments:
            -t : Type of lottery game (max, grand, or lottario) [required]
            --id : Identifier for the ticket generation request [required]
            -n : Number of tickets to generate (default = 1) [optional]

        Output:
            Prints the generated ticket(s) as part of a GenerationRequest.
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

        parser.add_argument(
            "--id",
            type=str,
            required=True,
            help="Identifier for the ticket generation request (required)"
        )

        args = parser.parse_args(argv)

        if args.n < 1:
            parser.error("The number of tickets (-n) must be at least 1.")

        generateTicketController = GenerateTicketController(args.id, args.t, args.n)
        generationResponse = generateTicketController.execute()

        print(generationResponse)
