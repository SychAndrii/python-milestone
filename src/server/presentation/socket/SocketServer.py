import os
import sys
import socket
import json
import signal
from ..GenerateTicketController import GenerateTicketController


class SocketServer:
    """
    Persistent IPv6 blocking socket server for lottery ticket generation.
    """

    def __init__(self, port=None):
        """
        Initialize the SocketServer instance.

        Args:
            port (int, optional): The port number to bind the server socket to.
                If None, prompts the user for a valid port number in the 1024–65535 range.
                Exits the program if the input is invalid or if interrupted by the user.
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

    def childProcessCleanup(signum, frame):
        """
        Signal handler for SIGCHLD.

        Reaps zombie child processes to prevent resource leaks.
        Uses a loop with waitpid and the WNOHANG flag to reap all terminated children.
        """
        try:
            while True:
                pid, status = os.waitpid(-1, os.WNOHANG)
                if pid == 0:
                    break
                print(f"[Parent] Reaped child process {pid}. Exit status: {status}")
        except ChildProcessError:
            pass

    def start(self):
        """
        Start the socket server.

        - Creates the server socket.
        - Configures it to allow address and port reuse.
        - Binds to the specified port and begins listening.
        - Accepts incoming client connections in an infinite loop.
        - Forks a new child process for each client connection.
        - Parent immediately closes the client socket and continues listening.
        - Handles socket errors and ensures the socket is properly closed on exit.
        """
        self.sock = self.createServerSocket()

        try:
            self.startListeningOnServerSocket()

            while True:
                clientSocket, addr = self.sock.accept()
                pid = os.fork()

                if pid == 0:
                    self.childProcessConnectionHandler(clientSocket, addr)
                else:
                    self.parentProcessConnectionHandler(clientSocket)

        except Exception as e:
            print(f"Socket error: {e}")
        finally:
            if self.sock:
                self.sock.close()

    def childProcessConnectionHandler(self, clientSocket, addr):
        """
        Handle a client connection in a forked child process.

        - Closes the server's listening socket (not needed in child).
        - Processes the client's request.
        - Closes the client socket and exits the child process cleanly.

        Args:
            clientSocket (socket.socket): The socket connected to the client.
            addr (tuple): The address of the connected client.
        """
        self.sock.close()
        with clientSocket:
            print(f"Connection accepted from {addr}")
            self.processRequest(clientSocket)
            os._exit(0)

    def parentProcessConnectionHandler(self, clientSocket):
        """
        Handle the parent-side cleanup of a client connection.

        - Closes the connected client socket immediately after forking.
        - Parent remains in the loop to continue accepting new connections.

        Args:
            clientSocket (socket.socket): The socket connected to the client.
        """
        clientSocket.close()

    def startListeningOnServerSocket(self):
        """
        Configure the server socket to bind and listen.

        - Binds the socket to the IPv6 localhost address (::1) and the specified port.
        - Starts listening for incoming connections.
        - Registers the SIGCHLD handler for reaping child processes.
        """
        self.sock.bind(("::1", self.port))
        self.sock.listen(5)
        print(f"Server listening on localhost:{self.port}")
        signal.signal(signal.SIGCHLD, self.childProcessCleanup)

    def createServerSocket(self):
        """
        Create and configure the server socket.

        - Uses IPv6 and TCP (stream) protocol.
        - Sets socket options to allow reuse of address and port.
        
        Returns:
            socket.socket: Configured server socket ready for binding.
        """
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        return sock

    def processRequest(self, conn):
        """
        Process a single client request.

        - Receives the request data from the client.
        - Parses the data as a JSON object and validates required fields.
        - Uses the GenerateTicketController to generate lottery tickets.
        - Sends the generated ticket data back to the client.
        - If an error occurs, sends an error message back to the client.

        Args:
            conn (socket.socket): The socket connected to the client.
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
