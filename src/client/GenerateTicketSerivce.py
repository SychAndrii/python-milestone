import os
import sys

class GenerateTicketService:
    """
    Service to handle generating and processing lottery ticket requests,
    including user prompts and saving the server response.
    """

    def __init__(self, loggerService):
        """
        Initialize the service with a logger.

        Args:
            loggerService (LoggingService): Logger for output.
        """
        self.loggerService = loggerService

    def promptRequest(self):
        """
        Prompt the user to enter ticket request information.

        Returns:
            dict: A dictionary containing ticket type, requestId, and count.
        """
        try:
            ticketType = input("Enter ticket type: ").strip()
            requestId = input("Enter request ID: ").strip()
            count = input("Enter number of tickets: ").strip()
            return {
                "type": ticketType,
                "requestId": requestId,
                "count": count
            }
        except (KeyboardInterrupt, EOFError):
            print("\n❌ User cancelled.")
            sys.exit(1)

    def handleResponse(self, request, response):
        """
        Handle the server response. If it's valid, save it to a file named 
        ticket_<requestId>.txt inside a "responses" folder located in the same directory as this file.
        Otherwise, print an error message.

        Args:
            request (dict): The original request object containing 'requestId'.
            response (str): The raw response received from the server.

        Raises:
            KeyError: If 'requestId' is not present in the request.
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
            filename = f"ticket_{requestId}.txt"
            filepath = os.path.join(responseDir, filename)
            with open(filepath, "w") as f:
                f.write(response)
            self.loggerService.printInfo(f"Response saved to {filepath}")
