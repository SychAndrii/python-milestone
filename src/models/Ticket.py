from typing import List
from .Pool import Pool

class Ticket:
    """
    Lottery ticket class for multi-pool games.
    Holds the pool configurations and generates numbers when printed.
    """

    def __init__(self, pools: List[Pool]):
        """
        Initializes the Ticket with a list of Pool configurations.

        Args:
            pools: List of Pool objects defining the pools for this ticket.
        """
        if not pools:
            raise ValueError("Ticket must contain at least one pool.")
        self.pools = pools

    def __str__(self) -> str:
        """
        Generates and returns a human-readable string representation of the ticket.

        Always displays:
            - Ticket Type (inferred from first pool name)
            - All pool numbers with their labels

        Example output:
            Ticket Type: Lotto Max
            Lotto Max Numbers: 4 12 15 22 33 44 50

        Returns:
            A string representation of the ticket.
        """
        lines = []

        ticketType = self.pools[0].name.split()[0]
        lines.append(f"Ticket Type: {ticketType}")

        for pool in self.pools:
            numbers = pool.selectRandomly()
            numbers.sort()
            numbersStr = " ".join(str(num) for num in numbers)
            lines.append(f"{pool.name}: {numbersStr}")

        return "\n".join(lines)
