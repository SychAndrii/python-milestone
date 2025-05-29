import json
import socket

class Connection:
    """
    Represents a TCP client connection to an IPv6 server.
    
    Validates the IPv6 address and port upon instantiation.
    Provides methods to connect, send JSON data, and close the connection.
    """

    def __init__(self, serverIP, serverPort, number):
        """
        Initialize the Connection instance and validate the IPv6 address and port.

        Args:
            serverIP (str): The IPv6 address of the server.
            serverPort (int): The port number of the server.
            number (int): Identifier of this connection. Can be duplicate across different connections.

        Raises:
            ValueError: If the serverIP is not a valid IPv6 address.
            ValueError: If the port is not within the valid range (1024-65535).
        """
        self.socket = None
        self.serverIP = serverIP
        self.serverPort = serverPort
        self.number = number

        try:
            addrinfo = socket.getaddrinfo(self.serverIP, None, socket.AF_INET6)
            if not addrinfo:
                raise ValueError(f"Invalid IPv6 address: {self.serverIP}")
        except socket.gaierror:
            raise ValueError(f"Invalid IPv6 address: {self.serverIP}")

        if not isinstance(self.serverPort, int) or not (1024 <= self.serverPort <= 65535):
            raise ValueError("Port must be an integer between 1024 and 65535.")

    def connect(self):
        """
        Establish a TCP connection to the specified IPv6 server.
        """
        self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.socket.connect((self.serverIP, self.serverPort))

    def sendJSON(self, data, payloadLength=8192):
        """
        Send JSON-encoded data to the server and receive the response.

        Args:
            data (dict): The data to serialize and send as JSON.
            payloadLength (int, optional): Maximum number of bytes to receive in the response.
                Default is 8192.

        Returns:
            str: The decoded response from the server.
        """
        jsonPayload = json.dumps(data)
        self.socket.sendall(jsonPayload.encode())

        response = self.socket.recv(payloadLength).decode()
        return response

    def close(self):
        """
        Close the socket connection if it is open.
        """
        if self.socket:
            self.socket.close()
