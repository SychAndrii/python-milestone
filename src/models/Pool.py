from typing import List
import random

class Pool:
    """
    Represents a lottery number pool.
    """

    def __init__(self, name: str, startNumber: int, endNumber: int, pickCount: int):
        """
        Initializes a Pool object and performs validation.

        Args:
            name: descriptive name for the pool
            startNumber: smallest possible number (inclusive)
            endNumber: largest possible number (inclusive)
            pick_count: how many unique numbers to pick

        Raises:
            ValueError: if configuration is invalid
        """
        if startNumber >= endNumber:
            raise ValueError(
                f"start_number ({startNumber}) must be less than end_number ({endNumber})."
            )

        if pickCount > (endNumber - startNumber + 1):
            raise ValueError(
                f"Cannot pick {pickCount} unique numbers from range {startNumber}-{endNumber}."
            )

        self.name = name
        self.startNumber = startNumber
        self.endNumber = endNumber
        self.pickCount = pickCount

    def selectRandomly(self) -> List[int]:
        """
        Randomly select unique numbers according to the pool's configuration.

        Returns:
            A list of unique randomly selected integers within the pool's range.
        """
        pool = list(range(self.startNumber, self.endNumber + 1))
        selected = []

        for _ in range(self.pickCount):
            index = random.randint(0, len(pool) - 1)
            selected.append(pool.pop(index))

        return selected
