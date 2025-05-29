import os
from .Connection import Connection


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
        children = []

        for i in range(clientAmount):
            pid = os.fork()
            exitCode = 0
            if pid == 0:
                # In child process
                connection = None
                try:
                    connection = self.__createConnection(serverIP, serverPort, i)
                    clientConnectionHandler(connection)
                except Exception as e:
                    self.logger.printError(f"Error occurred with connection {i}:\n{e}")
                    exitCode = 1
                finally:
                    if connection is not None:
                        connection.close()
                    os._exit(exitCode)
            else:
                # Parent process
                children.append({"pid": pid, "number": i })

        self.__reapChildren(children)

    def validateIPAndPort(self, serverIP, serverPort):
        """
        Validate the IPv6 address and port by creating a temporary Connection object.

        Args:
            serverIP (str): The IPv6 address to validate.
            serverPort (int): The port number to validate.

        Raises:
            ValueError: If the IPv6 address or port are invalid.
        """
        Connection(serverIP, serverPort, 0)

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
        connection = Connection(serverIP, serverPort, connectionNumber)
        connection.connect()
        self.logger.printInfo(f"Connection {connectionNumber} successfully established with {serverIP}:{serverPort}")
        return connection

    def __reapChildren(self, children):
        """
        Reap all forked child processes to ensure no zombies are left.

        Args:
            children (list): List of dictionaries containing process IDs and numbers to wait for and reap.
        """
        for child in children:
            try:
                pid, status = os.waitpid(child["pid"], 0)
                self.logger.printInfo(f"Reaped child process ({child['number']}) with pid {pid} with exit status {status}.")
            except ChildProcessError:
                # No more children to reap
                break
