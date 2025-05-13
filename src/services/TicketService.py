from .LotteryType import LotteryType
from ..models import *
from ..models.factories import *

class TicketService:
    """
    Service class for managing tickets.
    """

    def __init__(self):
        """
        Initialize the TicketService.
        """
        pass

    def generateTicket(self, type: LotteryType) -> Ticket:
        """
        Generate a ticket for the specified lottery type.

        Args:
            type: LotteryType enum value specifying the game.

        Returns:
            Ticket object containing randomly generated numbers.

        Raises:
            ValueError: if the LotteryType is unknown.
        """
        factory = None

        if type == LotteryType.LOTTO_MAX:
            factory = LottoMaxTicketFactory()
        elif type == LotteryType.DAILY_GRAND:
            factory = DailyGrandTicketFactory()
        elif type == LotteryType.LOTTARIO:
            factory = LottarioTicketFactory()
        else:
            raise ValueError(f"Unknown lottery type: {type}")

        return factory.createTicket()
