"""
Exports core domain models for the lottery system.
"""

from .Pool import Pool
from .Ticket import Ticket

__all__ = [
    "Pool",
    "Ticket"
]