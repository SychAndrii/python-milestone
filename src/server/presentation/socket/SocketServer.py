import sys
import socket
import json
from ..GenerateTicketController import GenerateTicketController


class SocketServer:
    """
    Persistent IPv6 blocking socket server for lottery ticket generation.
    """

    def __init__(self, port=None):
        """
        Initialize the server with the port to listen on.
        If port is not provided, prompt the user to enter it.
        """
        if port is None:
            try:
                while True:
                    portInput = input("Enter port number to bind to (1024–65535): ").strip()
                    port = int(portInput)
                    if port < 1024 or port > 65535:
                        print("❌ Port must be between 1024 and 65535.")
                        continue
                    break
            except ValueError:
                print("❌ Invalid input. Please enter an integer.")
                sys.exit(1)
            except KeyboardInterrupt:
                print("\n❌ User cancelled.")
                sys.exit(1)

        self.port = port
        self.sock = None

    def start(self):
        """
        Start the server:
        - Create a socket
        - Enable address and port reuse options
        - Bind to localhost
        - Listen for incoming connections
        - Process requests in an infinite loop
        """
        self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        try:
            self.sock.bind(("::1", self.port))
            self.sock.listen(5)
            print(f"Server listening on localhost:{self.port}")

            while True:
                conn, addr = self.sock.accept()
                print(f"Connection accepted from {addr}")
                with conn:
                    self.processRequest(conn)

        except Exception as e:
            print(f"Socket error: {e}")
        finally:
            if self.sock:
                self.sock.close()

    def processRequest(self, conn):
        """
        Process a single client connection:
        - Receive data
        - Parse JSON request
        - Validate request fields
        - Generate the requested tickets
        - Send back the response
        """
        try:
            raw = conn.recv(4096)
            request = json.loads(raw.decode())

            if "type" not in request:
                raise ValueError("Missing field: 'type'")
            if "requestId" not in request:
                raise ValueError("Missing field: 'requestId'")

            typeStr = request["type"]
            requestId = str(request["requestId"]).strip()
            if not requestId:
                raise ValueError("'requestId' must not be empty")

            count = request.get("count", 1)
            try:
                count = int(count)
            except (ValueError, TypeError):
                raise ValueError("'count' must be an integer")

            if count < 1:
                raise ValueError("'count' must be at least 1")

            generateTicketController = GenerateTicketController(requestId, typeStr, count)
            generationResponse = generateTicketController.execute()

            response = str(generationResponse).encode()
            conn.sendall(response)

        except Exception as e:
            errorMsg = f"[Error] {str(e)}"
            conn.sendall(errorMsg.encode())
