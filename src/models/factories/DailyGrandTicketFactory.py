from .ITicketFactory import ITicketFactory
from ..Ticket import Ticket
from ..Pool import Pool

class DailyGrandTicketFactory(ITicketFactory):
    """
    Factory for generating Daily Grand tickets.

    Daily Grand Rules:
        - Select 5 unique main numbers from 1 to 49 (inclusive).
        - Select 1 Grand Number from 1 to 7 (inclusive).
    """

    def createTicket(self, id: str) -> Ticket:
        """
        Create a Daily Grand ticket with the specified ID.

        Args:
            id (str): Unique identifier to assign to the ticket.

        Returns:
            Ticket: A ticket with two pools: main numbers and grand number.
        """
        pools = [
            Pool("Main Numbers", 1, 49, 5),
            Pool("Grand Number", 1, 7, 1)
        ]
        return Ticket(id, pools)
