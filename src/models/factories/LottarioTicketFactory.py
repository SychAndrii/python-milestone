from .ITicketFactory import ITicketFactory
from ..Ticket import Ticket
from ..Pool import Pool

class LottarioTicketFactory(ITicketFactory):
    """
    Factory for generating Lottario tickets.

    Lottario Rules:
        - Select 6 unique numbers from 1 to 45 (inclusive).
    """

    def createTicket(self, id: str) -> Ticket:
        """
        Create a Lottario ticket with the specified ID.

        Args:
            id (str): Unique identifier to assign to the ticket.

        Returns:
            Ticket: A ticket with one pool for Lottario numbers.
        """
        pools = [Pool("Lottario Numbers", 1, 45, 6)]
        return Ticket(id, pools)
