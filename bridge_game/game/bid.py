from dataclasses import dataclass
from enum import Enum


class Strain(Enum):
    CLUBS = 0
    DIAMONDS = 1
    HEARTS = 2
    SPADES = 3
    NO_TRUMP = 4


@dataclass(frozen=True)
class Bid:
    level: int
    strain: Strain

    def __post_init__(self):
        if not 1 <= self.level <= 7:
            raise ValueError("Bid level must be between 1 and 7")

    @property
    def value(self) -> int:
        """
        Convert a bid to a comparable integer.

        1C  = 0
        1D  = 1
        1H  = 2
        1S  = 3
        1NT = 4
        2C  = 5
        ...
        7NT = 34
        """
        return (self.level - 1) * 5 + self.strain.value

    def __lt__(self, other):
        if not isinstance(other, Bid):
            return NotImplemented

        return self.value < other.value