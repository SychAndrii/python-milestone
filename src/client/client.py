from . import *

def main():
    loggerService = LoggingService()
    connectionService = ConnectionService(loggerService)
    ticketService = GenerateTicketService(loggerService)

    loggerService.printInfo("OLG Lottery Ticket Client")
    connectionService.connect()
    request = ticketService.promptRequest()

    try:
        response = connectionService.sendJson(request)
        ticketService.handleResponse(request, response)
    except Exception as e:
        loggerService.printError(f"Error while communicating with server: {e}")

if __name__ == "__main__":
    main()
