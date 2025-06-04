import os
import sys
import socket
import json
import signal
from logzero import logger
from ..GenerateTicketController import GenerateTicketController
from .Daemon import Daemon


class SocketServer(Daemon):
    def __init__(self, username, groupname):
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
        self.sock = None

        super().__init__(username, groupname)

    def run(self):
        """
        Override the Daemon's run() method.
        This is where the socket server runs after daemonization.
        """
        logger.info(f"Starting socket server on port {self.port}")
        self.sock = self.createServerSocket()
        self.startListeningOnServerSocket()

        try:
            while self._daemonRunning:
                clientSocket, addr = self.sock.accept()
                pid = os.fork()
                if pid == 0:
                    self.childProcessConnectionHandler(clientSocket, addr)
                else:
                    self.parentProcessConnectionHandler(clientSocket)
        except Exception as e:
            logger.error(f"Socket error: {e}")
        finally:
            if self.sock:
                self.sock.close()
                logger.info("Socket closed.")

    def createServerSocket(self):
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock

    def startListeningOnServerSocket(self):
        self.sock.bind(("::1", self.port))
        self.sock.listen(5)
        signal.signal(signal.SIGCHLD, self.childProcessCleanup)
        logger.info(f"Server listening on localhost:{self.port}")

    def childProcessCleanup(self, signum, frame):
        try:
            while True:
                pid, status = os.waitpid(-1, os.WNOHANG)
                if pid == 0:
                    break
                logger.info(f"[Parent] Reaped child process {pid}. Exit status: {status}")
        except ChildProcessError:
            pass

    def childProcessConnectionHandler(self, clientSocket, addr):
        self.sock.close()
        with clientSocket:
            logger.info(f"Connection accepted from {addr}")
            self.processRequest(clientSocket)
            os._exit(0)

    def parentProcessConnectionHandler(self, clientSocket):
        clientSocket.close()

    def processRequest(self, conn):
        try:
            raw = conn.recv(4096)
            request = json.loads(raw.decode())

            if "type" not in request or "requestId" not in request:
                raise ValueError("Missing required fields.")

            typeStr = request["type"]
            requestId = str(request["requestId"]).strip()
            if not requestId:
                raise ValueError("'requestId' must not be empty")

            count = int(request.get("count", 1))
            if count < 1:
                raise ValueError("'count' must be at least 1")

            controller = GenerateTicketController(requestId, typeStr, count)
            response = str(controller.execute()).encode()
            conn.sendall(response)
        except Exception as e:
            errorMsg = f"[Error] {str(e)}"
            conn.sendall(errorMsg.encode())
