from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """
    Represents a user in the system.

    Attributes:
        id (int): Primary key, unique user identifier.
        username (str): Unique username of the user.
        password (str): Hashed password of the user.
        portfolio (Portfolio): One-to-one relationship with the user's portfolio.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, unique=True)
    password = Column(String)

    # One-to-one relationship with Portfolio
    portfolio = relationship("Portfolio", back_populates="user", uselist=False)


class Portfolio(Base):
    """
    Represents a user's financial portfolio.

    Attributes:
        id (int): Primary key.
        user_id (int): Foreign key referencing the associated user.
        total_added_money (float): Total amount of money the user has added.
        available_money (float): Remaining money after investments.
        user (User): Linked User object.
        assets (List[Asset]): List of assets owned in this portfolio.
        transactions (List[Transaction]): History of buy/sell transactions.
    """

    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_added_money = Column(Float, default=0)
    available_money = Column(Float, default=0)

    user = relationship("User", back_populates="portfolio")
    assets = relationship("Asset", back_populates="portfolio")
    transactions = relationship("Transaction", back_populates="portfolio")


class Asset(Base):
    """
    Represents an asset (e.g., stock, crypto) held in a portfolio.

    Attributes:
        id (int): Primary key.
        portfolio_id (int): Foreign key referencing the associated portfolio.
        symbol (str): Symbol/ticker of the asset (e.g., 'AAPL').
        quantity (float): Number of units held.
        portfolio (Portfolio): Linked portfolio.
    """

    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    symbol = Column(String)
    quantity = Column(Float)

    portfolio = relationship("Portfolio", back_populates="assets")


class Transaction(Base):
    """
    Represents a transaction record (buy/sell) for an asset.

    Attributes:
        id (int): Primary key.
        portfolio_id (int): Foreign key referencing the portfolio.
        symbol (str): Symbol of the traded asset.
        quantity (float): Amount bought or sold.
        price (float): Price per unit at transaction time.
        timestamp (datetime): Date and time of the transaction.
        portfolio (Portfolio): Linked portfolio.
    """

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    symbol = Column(String)
    quantity = Column(Float)
    price = Column(Float)
    timestamp = Column(DateTime)

    portfolio = relationship("Portfolio", back_populates="transactions")
