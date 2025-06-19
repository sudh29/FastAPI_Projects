from pydantic import BaseModel


class UserCreate(BaseModel):
    """
    Schema for creating a new user account.

    Attributes:
        username (str): Desired unique username for the user.
        password (str): Password for the account (should be hashed before storage).
    """

    username: str
    password: str


class AddMoney(BaseModel):
    """
    Schema for adding money to a user's portfolio.

    Attributes:
        amount (float): The amount of money to be added.
    """

    amount: float


class TradeAsset(BaseModel):
    """
    Schema for buying or selling an asset in the portfolio.

    Attributes:
        symbol (str): The asset symbol (e.g., 'AAPL', 'BTC').
        quantity (float): The quantity to buy or sell (positive for buy, negative for sell).
    """

    symbol: str
    quantity: float
