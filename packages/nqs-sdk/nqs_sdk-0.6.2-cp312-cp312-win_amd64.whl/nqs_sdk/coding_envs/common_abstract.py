from abc import ABC, abstractmethod
from decimal import Decimal


class CommonAbstract(ABC):
    @abstractmethod
    def get_wallet_holdings(self, token: str) -> Decimal:
        """Get the wallet holdings for a given token

        Args:
            token (str): The token to get the wallet holdings for

        Returns:
            Decimal: The wallet holdings for the given token
        """
        pass
