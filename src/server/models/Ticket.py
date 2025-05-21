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
        Returns a string with the generated numbers for each pool.

        Returns:
            str: Pool names and sorted numbers.
        """
        lines = []
        for pool in self.pools:
            numbers = pool.selectRandomly()
            numbers.sort()
            lines.append(f"{pool.name}: {' '.join(str(num) for num in numbers)}")
        return "\n".join(lines)
