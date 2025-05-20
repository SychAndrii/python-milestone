from typing import List
from ...models.Ticket import Ticket


class GenerationResponse:
    """
    Represents a request to generate one or more lottery tickets.

    Attributes:
        requestId (str): Identifier for this generation request.
        lotteryType (str): The type of lottery this request represents.
        tickets (List[Ticket]): List of generated tickets associated with the request.
    """

    def __init__(self, requestId: str, lotteryType: str, tickets: List[Ticket]):
        """
        Initializes the GenerationRequest with an ID, lottery type, and a list of tickets.

        Args:
            requestId (str): Unique identifier for the request.
            lotteryType (str): Name of the lottery type (e.g., "Lotto Max").
            tickets (List[Ticket]): List of Ticket objects.
        """
        if not requestId:
            raise ValueError("Request ID must not be empty.")
        if not lotteryType:
            raise ValueError("Lottery type must not be empty.")
        if not tickets:
            raise ValueError("Ticket list must not be empty.")

        self.requestId = requestId
        self.lotteryType = lotteryType
        self.tickets = tickets

    def __str__(self) -> str:
        """
        Returns a string representation of the generation request.

        Prints:
            - Request ID
            - Ticket Type (immediately below)
            - All ticket pool contents
        """
        header = f"Generation Request ID: {self.requestId}\nTicket Type: {self.lotteryType}"
        body = "\n\n".join(str(ticket) for ticket in self.tickets)
        return f"{header}\n\n{body}" if body else header
