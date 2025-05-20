from abc import ABC, abstractmethod
from ..Ticket import Ticket

class ITicketFactory(ABC):
    """
    Abstract base class for a lottery ticket factory.

    A factory is responsible for generating a complete Ticket for a specific lottery game,
    using a provided ticket ID to uniquely identify the generated ticket.
    """

    @abstractmethod
    def createTicket(self, id: str) -> Ticket:
        """
        Create and return a complete Ticket for this lottery game.

        Args:
            id (str): Unique identifier to associate with the generated ticket.
                      This value is embedded into the Ticket object for traceability.

        Returns:
            Ticket: Object containing randomly generated numbers, tagged with the given ID.
        """
        pass
