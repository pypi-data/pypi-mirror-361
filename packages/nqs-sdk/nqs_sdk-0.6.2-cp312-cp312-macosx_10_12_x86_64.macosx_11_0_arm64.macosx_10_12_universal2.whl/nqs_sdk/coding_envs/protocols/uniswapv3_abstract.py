import datetime
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional


class UniswapV3Protocol(ABC):
    """Uniswap V3 Protocol"""

    @abstractmethod
    def dex_spot(self, lookback: Optional[datetime.timedelta] = None) -> list[Decimal]:
        """Get the price of token0 in units of token1.

        Args:
            lookback (Optional[datetime.timedelta]): Return all data included in the lookback period.
                If None, returns only the current price.

        Returns:
            list[Decimal]: the list of spot prices (i.e. the price of token0 in units of token1)
            from the oldest to the newest
        """
        pass

    @abstractmethod
    def liquidity(self, lookback: Optional[datetime.timedelta] = None) -> list[Decimal]:
        """Get the liquidity parameter in the pool for the current tick.

        Args:
            lookback (Optional[datetime.timedelta]): Return all data included in the lookback period.
                If None, returns only the current liquidity.

        Returns:
            list[Decimal]: the list of liquidity values
        """
        pass

    @abstractmethod
    def total_volume_numeraire(self, lookback: Optional[datetime.timedelta] = None) -> list[Decimal]:
        """Get the total volume of swaps in the pool in units of the user numeraire.

        Args:
            lookback (Optional[datetime.timedelta]): Return all data included in the lookback period.
            If None, returns only the current volume.

        Returns:
            Decimal: Total volume in numeraire at the requested block number
        """
        pass

    @abstractmethod
    def total_volume(self, token: bool, lookback: Optional[datetime.timedelta] = None) -> list[Decimal]:
        """Get the total volume of swaps in the pool for the specified token.

        Args:
            token (bool): False for token0, True for token1
            lookback (Optional[datetime.timedelta]): Return all data included in the lookback period.
                If None, returns only the current volume.

        Returns:
            Decimal: Total volume for the specified token at the requested block number
        """
        pass

    @abstractmethod
    def total_holdings(self, token: bool, lookback: Optional[datetime.timedelta] = None) -> list[Decimal]:
        """Get the total holdings of the specified token in the pool.

        Args:
            token (bool): False for token0, True for token1
            lookback (Optional[datetime.timedelta]): Return all data included in the lookback period.
                If None, returns only the current volume.

        Returns:
            Decimal: Total holdings for the specified token at the requested block number
        """
        pass

    @abstractmethod
    def total_fees(self, token: Optional[bool] = None, lookback: Optional[datetime.timedelta] = None) -> list[Decimal]:
        """Get the total fees in the pool.

        Args:
            token (Optional[bool]): False for token0, True for token1. If None, returns fees in numeraire.
            lookback (Optional[datetime.timedelta]): Return all data included in the lookback period.
                If None, returns only the current fees.

        Returns:
            Decimal: Total fees (in token units if token specified, otherwise in numeraire)
        """
        pass

    @abstractmethod
    def total_value_locked(self, lookback: Optional[datetime.timedelta] = None) -> list[Decimal]:
        """Get the total value locked in the pool in units of the user numeraire.

        Args:
            lookback (Optional[datetime.timedelta]): Return all data included in the lookback period.
                If None, returns only the current value locked.

        Returns:
            Decimal: Total value locked at the requested block number
        """
        pass

    @abstractmethod
    def get_tick(self, lookback: Optional[datetime.timedelta] = None) -> list[int]:
        """Get the tick of the pool.

        Args:
            lookback (Optional[datetime.timedelta]): Return all data included in the lookback period.
            If None, returns only the current tick.

        Returns:
            int: The tick value at the requested block number
        """
        pass

    @abstractmethod
    def swap(self, amount: float, token: bool) -> None:
        """Swap or exchange tokens in the pool. At least one of the arguments should be provided.

        Args:
            amount (float): The amount of token to be swapped.
            token (bool): True for swapping token1 to token0, False for swapping token0 to token1.
        """
        pass

    @abstractmethod
    def mint(self, price_lower: float, price_upper: float, max_token0: float, max_token1: float, token_id: str) -> None:
        """Uniswap V3 minting enables users to provide (add) liquidity within specific price ranges.

        Args:
            price_lower (float): The lower price of the liquidity range.
            price_upper (float): The upper price of the liquidity range.
            max_token0 (float): The maximum amount of token0 to be used.
            max_token1 (float): The maximum amount of token1 to be used.
            token_id (str): A string identifier of the position.
        """
        pass

    @abstractmethod
    def burn(self, amount_percentage: float, token_id: str) -> None:
        """Uniswap v3 burn is the burning of LP tokens, when users can effectively withdraw liquidity
        from specific price ranges within Uniswap V3 liquidity pools.

        Args:
            amount_percentage (float): Amount of liquidity to be burned (between 0.0 and 1.0 where 1.0 represent all
            the liquidity of the position).
            token_id (str): The id of position to be burned.
        """
        pass

    @abstractmethod
    def active_liquidity(self, position: Optional[str] = None) -> Decimal:
        """Get liquidity that is currently active in the pool.

        Args:
            position (str, optional): Position ID to get specific position's active liquidity.
                If None, returns user's total active liquidity.

        Returns:
            Decimal: Active liquidity amount at the requested block number
        """
        pass

    @abstractmethod
    def position_liquidity(self, position: str) -> Decimal:
        """Get total liquidity allocated in the pool

        Args:
            position (str): Position ID to get specific user position's active liquidity.

        Returns:
            Decimal: Total liquidity amount for the pool or a specific user position
        """
        pass

    @abstractmethod
    def token_amount(self, token: str, position: Optional[str] = None) -> Decimal:
        """Get actual token amount in the pool.

        Args:
            token (str): str to query amount for
            position (str, optional): Position ID to get specific position's token amount.
                If None, returns user's total token amount.

        Returns:
            Decimal: Amount of specified token at the requested block number
        """
        pass

    @abstractmethod
    def net_position(self, position: str) -> Decimal:
        """Get the value of agent's position in the pool.

        Args:
            position (str): Position ID to query

        Returns:
            Decimal: Position value in units of numeraire at the requested block number
        """
        pass

    @abstractmethod
    def fees_collected(self, token: Optional[str] = None, position: Optional[str] = None) -> Decimal:
        """Get collected fees.

        Args:
            token (str, optional): str to query fees for
            position (str, optional): Position ID to get specific position's fees.
                If None, returns user's total collected fees.

        Returns:
            Decimal: Amount of collected fees in specified token or numeraire at the requested block number
        """
        pass

    @abstractmethod
    def fees_not_collected(self, token: Optional[str] = None, position: Optional[str] = None) -> Decimal:
        """Get uncollected fees.

        Args:
            token (str, optional): str to query fees for
            position (str, optional): Position ID to get specific position's fees.
                If None, returns user's total uncollected fees.

        Returns:
            Decimal: Amount of uncollected fees in specified token or numeraire at the requested block number
        """
        pass

    @abstractmethod
    def abs_impermanent_loss(self, position: Optional[str] = None) -> Decimal:
        """Get absolute impermanent loss.

        Args:
            position (str, optional): Position ID to get specific position's IL.
                If None, returns IL for all user's open positions.

        Returns:
            Decimal: Impermanent loss in units of numeraire at the requested block number
        """
        pass

    @abstractmethod
    def perc_impermanent_loss(self, position: Optional[str] = None) -> Decimal:
        """Get impermanent loss as a percentage.

        Args:
            position (str, optional): Position ID to get specific position's IL.
                If None, returns IL percentage for all user's open positions.
        Returns:
            Decimal: Impermanent loss as a percentage
        """
        pass

    @abstractmethod
    def static_ptf_value(self, position: Optional[str] = None) -> Decimal:
        """Get value of the static portfolio.

        Args:
            position (str, optional): Position ID to get specific position's value.
                If None, returns value for all user's open positions.

        Returns:
            Decimal: Static portfolio value in numeraire at the requested block number
        """
        pass

    @abstractmethod
    def permanent_loss(self, position: Optional[str] = None) -> Decimal:
        """Get realized/permanent loss.

        Args:
            position (str, optional): Position ID to get specific position's loss.
                If None, returns loss for all user's open positions.

        Returns:
            Decimal: Permanent loss in units of numeraire at the requested block number
        """
        pass

    @abstractmethod
    def loss_versus_rebalancing(self, position: Optional[str] = None) -> Decimal:
        """Get loss compared to rebalancing strategy.

        Args:
            position (str, optional): Position ID to get specific position's LVR.
                If None, returns LVR for all user's open positions.

        Returns:
            Decimal: Loss versus rebalancing in units of numeraire at the requested block number
        """
        pass

    @abstractmethod
    def total_fees_relative_to_lvr(self, position: Optional[str] = None) -> Decimal:
        """Get total accumulated fees as percentage of LVR.

        Args:
            position (str, optional): Position ID to get specific position's relative fees.
                If None, returns relative fees for all user's open positions.

        Returns:
            Decimal: Fees as percentage of loss versus rebalancing at the requested block number
        """
        pass

    @abstractmethod
    def position_bounds(self, position: str) -> tuple[Decimal, Decimal]:
        """Get price bounds of a position.

        Args:
            position (str): Position ID to query

        Returns:
            tuple[Decimal, Decimal]: Lower and upper price bounds of the position
        """
        pass
