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
            pools: list of Pool objects defining the pools for this ticket.
        """
        if not pools:
            raise ValueError("Ticket must contain at least one pool.")
        self.pools = pools

    def __str__(self) -> str:
        """
        Generates and returns a human-readable string representation of the ticket.

        If only one pool:
            - Print numbers only (space-separated).
        If multiple pools:
            - For each pool, print "Pool Name: numbers"

        Example single pool:
            3 8 14 22 37 44 49

        Example multiple pools:
            Main Numbers: 3 8 14 22 37
            Grand Number: 5

        Returns:
            A string representation of the ticket.
        """
        if len(self.pools) == 1:
            numbers = self.pools[0].selectRandomly()
            numbers.sort()
            return " ".join(str(num) for num in numbers)

        result = []
        for pool in self.pools:
            numbers = pool.selectRandomly()
            numbers.sort()
            numbers_str = " ".join(str(num) for num in numbers)
            result.append(f"{pool.name}: {numbers_str}")
        return "\n".join(result)
