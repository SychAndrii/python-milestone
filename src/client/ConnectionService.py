import os
from Connection import Connection


class ConnectionService:
    """
    Manages creating multiple concurrent connections to an IPv6 server
    and reaps child processes to avoid zombies.
    """

    def __init__(self, loggingService):
        """
        Initialize the ConnectionService.

        Args:
            loggingService (LoggingService): Logging service instance.
        """
        self.logger = loggingService

    def batchRequest(self, clientAmount, serverIP, serverPort, clientConnectionHandler):
        """
        Forks child processes to create multiple simultaneous client connections.
        Each child handles its own connection and then exits.
        The parent process reaps all child processes to avoid zombies.

        Args:
            clientAmount (int): Number of client connections to create.
            serverIP (str): The IPv6 server IP address to connect to.
            serverPort (int): The port number on the server to connect to.
            clientConnectionHandler (function): Function to handle the client connection logic.
        """
        childPIDs = []

        for i in range(clientAmount):
            pid = os.fork()
            if pid == 0:
                # In child process
                try:
                    connection = self.__createConnection(serverIP, serverPort, i)
                    clientConnectionHandler(connection)
                except Exception as e:
                    self.logger.printError(f"Error occurred with connection {i}: {e}")
                finally:
                    connection.close()
                    os._exit(0)
            else:
                # Parent process
                childPIDs.append(pid)

        self.__reapChildren(childPIDs)

    def validateIPAndPort(self, serverIP, serverPort):
        """
        Validate the IPv6 address and port by creating a temporary Connection object.

        Args:
            serverIP (str): The IPv6 address to validate.
            serverPort (int): The port number to validate.

        Raises:
            ValueError: If the IPv6 address or port are invalid.
        """
        Connection(serverIP, serverPort)

    def __createConnection(self, serverIP, serverPort, connectionNumber):
        """
        Create and establish a TCP connection to the specified server.

        Args:
            serverIP (str): The IPv6 server IP address to connect to.
            serverPort (int): The port number on the server to connect to.
            connectionNumber (int): Index number for logging purposes.

        Returns:
            Connection: An established and connected socket wrapper.
        """
        connection = Connection(serverIP, serverPort)
        connection.connect()
        self.logger.printInfo(f"Connection {connectionNumber} successfully established with {serverIP}:{serverPort}")
        return connection

    def __reapChildren(self, childPIDs):
        """
        Reap all forked child processes to ensure no zombies are left.

        Args:
            childPIDs (list): List of child process IDs to wait for and reap.
        """
        for _ in childPIDs:
            try:
                pid, status = os.wait()
                self.logger.printInfo(f"[Parent] Reaped child process {pid} with exit status {status}.")
            except ChildProcessError:
                # No more children to reap
                break
