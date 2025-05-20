import socket
import json
import sys

class ConnectionService:
    """
    Handles establishing a persistent connection to a local IPv6 server
    with optional port reuse and robust retry logic.
    """

    def __init__(self, loggingService):
        """
        Initialize the ConnectionService.

        Args:
            loggingService (LoggingService): An instance of the logging service used for output.
        """
        self.logger = loggingService
        self.socket = None

    def sendJson(self, body, payloadLength=8192):
        """
        Send a JSON-encoded request body to the connected server and receive a response.

        Args:
            body (dict): The dictionary to serialize and send as JSON.
            payloadLength (int): Max bytes to receive from server. Default is 8192.

        Returns:
            str: The decoded response from the server.

        Raises:
            Exception: If any communication or socket error occurs.
        """
        try:
            if self.socket is None:
                raise RuntimeError("Socket is not connected. Call connect() first.")

            jsonPayload = json.dumps(body)
            self.socket.sendall(jsonPayload.encode())
            self.logger.printInfo("Request sent. Awaiting response...")

            response = self.socket.recv(payloadLength).decode()
            return response

        except Exception as e:
            self.logger.printError(f"Error while communicating with server: {e}")
            raise
        finally:
            self.socket.close()
            self.socket = None

    def connect(self, port=None):
        """
        Attempt to establish a TCP connection to IPv6 localhost.
        Keeps retrying until successful or the user cancels with Ctrl+C.

        Args:
            port (int, optional): The port number to use. If None, the user will be prompted.
        """
        while True:
            try:
                if port is None:
                    port = self.__getValidPort()
                ip = "localhost"
                self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                self.logger.printInfo(f"Connecting to [{ip}]:{port} ...")
                self.socket.connect((ip, port))
                self.logger.printInfo("Connected successfully.\n")
                return

            except (socket.gaierror, ConnectionRefusedError, TimeoutError, OSError) as e:
                self.logger.printError(f"Failed to connect to server: {e}")
                try:
                    input("Press Enter to try again...")
                except KeyboardInterrupt:
                    self.logger.printError("\nCancelled by user.")
                    sys.exit(1)
                self.logger.clear()
                port = None

            except KeyboardInterrupt:
                self.logger.printInfo("\nCancelled by user.")
                sys.exit(1)

    def __getValidPort(self):
        """
        Prompt the user for a valid port number in the range 1024–65535.

        Returns:
            int: A valid port number entered by the user.
        """
        while True:
            portInput = input("Enter port number (1024–65535): ").strip()
            if portInput.isdigit():
                port = int(portInput)
                if 1024 <= port <= 65535:
                    return port
            self.logger.printError("Port must be an integer between 1024 and 65535.")
