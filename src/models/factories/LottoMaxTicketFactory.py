from .ITicketFactory import ITicketFactory
from ..Ticket import Ticket
from ..Pool import Pool

class LottoMaxTicketFactory(ITicketFactory):
    """
    Factory for generating Lotto Max tickets.

    Lotto Max Rules:
        - Select 7 unique numbers from 1 to 50 (inclusive).
    """

    def createTicket(self) -> Ticket:
        pools = [Pool("Lotto Max Numbers", 1, 50, 7)]
        return Ticket(pools)