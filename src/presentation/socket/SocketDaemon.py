import socket
import json
from .Daemon import Daemon
from ...services import TicketService
from ...services.converters import LotteryTypeConverter
from ...services.transients.GenerationResponse import GenerationResponse


class SocketDaemon(Daemon):
    """
    Persistent IPv6 blocking daemon that listens on a specified socket and
    processes client requests to generate lottery tickets.
    """

    def __init__(self, newUID, newGID, pidFile, STDIN='/dev/null', STDOUT='/dev/null', STDERR='/dev/null', port=5000):
        super().__init__(newUID, newGID, pidFile, STDIN, STDOUT, STDERR)
        self.port = port

    def run(self):
        """
        Start the persistent IPv6 blocking socket server.
        """
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            sock.bind(("::1", self.port))
            sock.listen(5)
            print(f"[Daemon] Listening on [::1]:{self.port}")

            while self._daemonRunning:
                conn, addr = sock.accept()
                print(f"[Daemon] Connection accepted from {addr}")
                with conn:
                    self._handleClient(conn)

        except Exception as e:
            print(f"[Daemon] Socket error: {e}")
        finally:
            sock.close()

    def _handleClient(self, conn):
        """
        Handles a single client request from the blocking socket.
        Expects JSON data from client:
            {
                "type": "max" | "grand" | "lottario",
                "count": <number of tickets>,
                "requestId": "<string>"
            }
        Sends back formatted ticket string.
        """
        try:
            raw = conn.recv(4096)
            request = json.loads(raw.decode())

            typeStr = request["type"]
            count = int(request["count"])
            requestId = request["requestId"]

            if count < 1:
                raise ValueError("count must be >= 1")

            ticketType = LotteryTypeConverter().toTransient(typeStr)
            service = TicketService()
            tickets = [service.generateTicket(ticketType) for _ in range(count)]
            generationRequest = GenerationRequest(requestId, typeStr.capitalize(), tickets)

            response = str(generationRequest).encode()
            conn.sendall(response)

        except Exception as e:
            errorMsg = f"Error: {str(e)}"
            conn.sendall(errorMsg.encode())
