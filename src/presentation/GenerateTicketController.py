from ..services import TicketService
from ..services.converters import LotteryTypeConverter
from ..services.transients.GenerationResponse import GenerationResponse

class GenerateTicketController:
    """
    Presentation controller responsible for generating lottery tickets.

    This class is intended to reduce code duplication across multiple
    presentation layers (e.g., Console and SocketDaemon) by encapsulating
    shared logic such as:
        - Mapping input type to LotteryType
        - Generating ticket(s)
        - Creating a GenerationResponse

    It accepts a request ID, lottery type string, and the number of tickets to generate.
    """

    def __init__(self, id, type, amount):
        self.id = id
        self.type = type
        self.amount = amount

    def execute(self):
        ticketTypeConverter = LotteryTypeConverter()
        ticketType = ticketTypeConverter.toTransient(self.type)
        ticketTypeStr = ticketTypeConverter.toString(ticketType)

        service = TicketService()
        tickets = [service.generateTicket(ticketType) for _ in range(self.amount)]

        generationRequest = GenerationResponse(self.id, ticketTypeStr, tickets)
        return generationRequest
