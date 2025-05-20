from ..transients import LotteryType


class LotteryTypeConverter:
    """
    Converts between string representations of lottery types
    and their corresponding `LotteryType` enum values used in the application layer.

    This class acts as a boundary translator between the application/presentation layer.
    """

    def __init__(self):
        self._type_mapping = {
            "max": LotteryType.LOTTO_MAX,
            "grand": LotteryType.DAILY_GRAND,
            "lottario": LotteryType.LOTTARIO
        }

    def toTransient(self, value: str) -> LotteryType:
        """
        Converts a string input into its corresponding LotteryType enum value.

        Args:
            value (str): The string value, e.g., "max", "grand", "lottario"

        Returns:
            LotteryType: The corresponding enum value

        Raises:
            ValueError: If the string does not match any known type.
        """
        try:
            return self._type_mapping[value.lower()]
        except KeyError:
            raise ValueError(f"Unknown lottery type: '{value}'")

    def toString(self, lottery_type: LotteryType) -> str:
        """
        Converts a LotteryType enum value back to its string representation.

        Args:
            lottery_type (LotteryType): The enum value to convert

        Returns:
            str: The corresponding string key (e.g., "max", "grand")

        Raises:
            ValueError: If the enum value is not recognized.
        """
        for key, val in self._type_mapping.items():
            if val == lottery_type:
                return key.capitalize()
        raise ValueError(f"Unknown LotteryType: {lottery_type}")