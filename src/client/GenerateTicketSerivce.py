import os
import random

class GenerateTicketService:
    """
    Service to handle generating and processing lottery ticket requests,
    including random request generation and saving the server response.
    """

    def __init__(self, loggerService):
        """
        Initialize the GenerateTicketService with a logger.

        Args:
            loggerService (LoggingService): Logger instance for output messages.
        """
        self.loggerService = loggerService

    def execute(self, connection):
        """
        Generate a random request, send it via the provided connection, and handle the response.

        Args:
            connection (Connection): The established connection to the server.
        """
        data = self.__generateRequest()
        response = connection.sendJSON(data)
        self.__handleResponse(data, response, f"{connection.number}.txt")

    def __generateRequest(self):
        """
        Generate a random lottery ticket request using only the random module.

        - Randomly selects a ticket type from a predefined list.
        - Generates a random numeric request ID.
        - Randomly selects a ticket count within a specified range.

        Returns:
            dict: A dictionary containing 'type', 'requestId', and 'count' for the request.
        """
        ticketTypes = ["max", "grand", "lottario"]
        index = random.randint(0, len(ticketTypes) - 1)
        ticketType = ticketTypes[index]

        requestId = str(random.randint(100000, 999999))
        count = random.randint(1, 10)

        return {
            "type": ticketType,
            "requestId": requestId,
            "count": count
        }

    def __handleResponse(self, request, response, fileName):
        """
        Handle the server response. If it's valid, save it to a file named
        ticket_<requestId>.txt inside a 'responses' folder located in the same directory as this file.
        If the response indicates an error, log the error without creating a file.

        Args:
            request (dict): The original request object containing 'requestId'.
            response (str): The raw response received from the server.
            fileName (str): The name of the file which will contain the response (int the responses directory).

        Raises:
            KeyError: If 'requestId' is missing in the request dictionary.
        """
        if "requestId" not in request:
            raise KeyError("Missing 'requestId' in request object.")

        requestId = request["requestId"]
        response = response.strip()

        if response.startswith("[Error]"):
            message = response[len("[Error]"):].strip()
            self.loggerService.printError("No file was created due to server-side error:")
            self.loggerService.printError(message)
        else:
            currentDir = os.path.dirname(os.path.abspath(__file__))
            responseDir = os.path.join(currentDir, 'responses')
            if not os.path.exists(responseDir):
                os.makedirs(responseDir)

            filepath = os.path.join(responseDir, fileName)
            with open(filepath, "w") as f:
                f.write(response)

            self.loggerService.printInfo(f"Response saved to {filepath}\n\n")
