from abc import ABC, abstractmethod
from ..Ticket import Ticket

class ITicketFactory(ABC):
    """
    Abstract base class for a lottery ticket factory.
    A factory is responsible for generating a complete Ticket for a specific game.
    """

    @abstractmethod
    def createTicket(self) -> Ticket:
        """
        Create and return a complete Ticket for this lottery game.

        Returns:
            Ticket object containing randomly generated numbers.
        """
        pass