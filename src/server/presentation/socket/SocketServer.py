import os
import sys
import socket
import json
import signal
from logzero import logger
from ..GenerateTicketController import GenerateTicketController
from .Daemon import Daemon


class SocketServer(Daemon):
    def __init__(self, username, groupname, port):
        self.sock = None
        self.port = port
        self._socketClosed = False  # Guard to prevent double-close
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
            if not self._socketClosed:
                logger.error(f"Socket error: {e}")
        finally:
            self._safeCloseSocket()

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
        self._safeCloseSocket()
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

    def _handlerSIGTERM(self, signum, frame):
        logger.info("Received SIGTERM or SIGINT. Shutting down socket server.")
        self._daemonRunning = False
        self._safeCloseSocket()

    def _safeCloseSocket(self):
        if self.sock and not self._socketClosed:
            try:
                self.sock.close()
                logger.info("Socket closed.")
            except Exception as e:
                logger.warning(f"Failed to close socket: {e}")
            finally:
                self._socketClosed = True
                self.sock = None
