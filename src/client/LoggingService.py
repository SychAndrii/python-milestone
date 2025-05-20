import os

class LoggingService:
    """
    A simple logging utility for printing styled messages to the console.

    Features:
    - Info messages in bold blue
    - Error messages in bold red
    - Cross-platform console clearing
    """

    def __init__(self):
        self.RED_BOLD = "\033[1;91m"
        self.BLUE_BOLD = "\033[1;94m"
        self.RESET = "\033[0m"

    def printInfo(self, message: str) -> None:
        """
        Print an informational message in bold blue.

        Args:
            message (str): The message to display.
        """
        print(f"{self.BLUE_BOLD}{message}{self.RESET}")

    def printError(self, message: str) -> None:
        """
        Print an error message in bold red.

        Args:
            message (str): The error message to display.
        """
        print(f"{self.RED_BOLD}{message}{self.RESET}")

    def clear(self) -> None:
        """
        Clear the console screen. Supports Windows and Unix-based systems.
        """
        os.system("cls" if os.name == "nt" else "clear")
