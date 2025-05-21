from .transients.LotteryType import LotteryType
from ..models import *
from ..models.factories import *

class TicketService:
    """
    Service class for managing lottery tickets.

    This service generates lottery tickets by delegating to the appropriate
    factory based on the selected LotteryType.
    """

    def __init__(self):
        """
        Initialize the TicketService.
        """
        pass

    def generateTicket(self, type: LotteryType) -> Ticket:
        """
        Generate a lottery ticket for the specified type.

        Args:
            type (LotteryType): Enum value specifying the type of lottery game
                                (e.g., LOTTO_MAX, DAILY_GRAND, LOTTARIO).

        Returns:
            Ticket: A Ticket object containing randomly generated numbers
                    based on the rules of the selected lottery game.

        Raises:
            ValueError: If the given LotteryType is not supported.
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
