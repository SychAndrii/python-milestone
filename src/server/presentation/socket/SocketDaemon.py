import sys
import socket
import json
from .Daemon import Daemon
from ..GenerateTicketController import GenerateTicketController


class SocketDaemon(Daemon):
    """
    Persistent IPv6 blocking daemon that listens on a socket and
    handles lottery ticket generation requests from clients.
    """

    def __init__(self, username, groupname, pidFile, port=None,
             STDIN='/dev/null', STDOUT='/dev/null', STDERR='/dev/null'):
        if port is None:
            try:
                while True:
                    port_input = input("Enter port number to bind daemon to (1024–65535): ").strip()
                    port = int(port_input)
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
        super().__init__(username, groupname, pidFile, STDIN, STDOUT, STDERR)

    def run(self):
        """
        Starts the blocking IPv6 socket server and listens for incoming connections.
        """
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock = sock

        try:
            sock.bind(("localhost", self.port))
            sock.listen(5)
            print(f"Listening on [127.0.0.1]:{self.port}")

            while self._daemonRunning:
                conn, addr = sock.accept()
                print(f"Connection accepted from {addr}")
                with conn:
                    self.generateTicket(conn)

        except Exception as e:
            print(f"Socket error: {e}")
        finally:
            sock.close()

    def generateTicket(self, conn):
        """
        Handles a single client connection.

        Clients must send a JSON request like:
        {
            "type": "max" | "grand" | "lottario",
            "requestId": "<string>",
            "count": <number of tickets>  (optional, default = 1)
        }

        The daemon responds with a formatted ticket generation response.
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
