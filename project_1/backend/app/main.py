"""
Crypto Portfolio Tracker API

This FastAPI application allows users to register, log in, and manage their cryptocurrency investments.
Users can add money to their portfolio, buy/sell assets using live prices from Binance, and track performance.

"""

import requests
import jwt
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .models import Base, User, Asset, Portfolio, Transaction
from .schemas import UserCreate, AddMoney, TradeAsset

app = FastAPI(title="Portfolio Tracker")

# OAuth2 password flow
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# SQLite database setup
engine = create_engine(
    "sqlite:///./crypto_portfolio.db", connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Secret key for JWT encoding/decoding
# SECRET_KEY = secrets.token_urlsafe(32)
SECRET_KEY = "your_secret_key_here"


def get_db():
    """
    Dependency to get a database session.
    Rolls back if any transaction is active after closing.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        if db.is_active:
            db.rollback()
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """
    Validates JWT token and fetches the associated user.
    Raises:
        HTTPException: 401 if token is invalid or user not found.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user = db.query(User).filter(User.username == payload["username"]).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid user")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_crypto_price(symbol: str) -> float:
    """
    Fetches the real-time USDT price of a cryptocurrency symbol from Binance.

    Returns:
        float: Current market price in USDT.
    """
    try:
        response = requests.get(
            f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}USDT"
        )
        return float(response.json()["price"])
    except Exception as e:
        print(f"Error fetching price for {symbol}: {e}")
        return 0.0


@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user and initializes their portfolio.

    Returns:
        dict: Confirmation message.
    """
    db_user = User(username=user.username, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    portfolio = Portfolio(user_id=db_user.id)
    db.add(portfolio)
    db.commit()

    return {"message": "Successfully created new user."}


@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Logs in a user and returns a JWT token.

    Returns:
        dict: Access token and token type.
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or user.password != form_data.password:
        raise HTTPException(status_code=400, detail="Information invalid")

    token = jwt.encode({"username": user.username}, SECRET_KEY, algorithm="HS256")

    return {"access_token": token, "token_type": "bearer"}


@app.post("/add-money")
def add_money(
    money: AddMoney,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Adds money to the user's portfolio balance.

    Returns:
        dict: Confirmation message.
    """
    portfolio = user.portfolio
    portfolio.total_added_money += money.amount
    portfolio.available_money += money.amount
    db.commit()

    return {"message": "Successfully added money"}


@app.post("/buy")
def buy_asset(
    trade: TradeAsset,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Buys a crypto asset and updates the portfolio and transaction log.

    Returns:
        dict: Confirmation message.
    """
    portfolio = user.portfolio
    price = get_crypto_price(trade.symbol)
    total_cost = price * trade.quantity

    if total_cost > portfolio.available_money:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    asset = (
        db.query(Asset)
        .filter(Asset.portfolio_id == portfolio.id, Asset.symbol == trade.symbol)
        .first()
    )

    if asset:
        asset.quantity += trade.quantity
    else:
        asset = Asset(
            portfolio_id=portfolio.id, symbol=trade.symbol, quantity=trade.quantity
        )
        db.add(asset)

    transaction = Transaction(
        portfolio_id=portfolio.id,
        symbol=trade.symbol,
        quantity=trade.quantity,
        price=price,
        timestamp=datetime.utcnow(),
    )

    db.add(transaction)
    portfolio.available_money -= total_cost
    db.commit()

    return {"message": "Asset successfully bought."}


@app.post("/sell")
def sell_asset(
    trade: TradeAsset,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Sells a crypto asset and updates the portfolio and transaction log.

    Returns:
        dict: Confirmation message.
    """
    portfolio = user.portfolio
    asset = (
        db.query(Asset)
        .filter(Asset.portfolio_id == portfolio.id, Asset.symbol == trade.symbol)
        .first()
    )

    if not asset or asset.quantity < trade.quantity:
        raise HTTPException(status_code=400, detail="Not enough to sell")

    price = get_crypto_price(trade.symbol)
    total_value = price * trade.quantity

    asset.quantity -= trade.quantity

    if asset.quantity == 0:
        db.delete(asset)

    transaction = Transaction(
        portfolio_id=portfolio.id,
        symbol=trade.symbol,
        quantity=-trade.quantity,
        price=price,
        timestamp=datetime.utcnow(),
    )

    db.add(transaction)
    portfolio.available_money += total_value
    db.commit()

    return {"message": "Asset successfully sold."}


@app.get("/portfolio")
def get_portfolio(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Retrieves current portfolio overview, including:
    - Available funds
    - Asset breakdown
    - Performance metrics

    Returns:
        dict: Portfolio summary.
    """
    portfolio = user.portfolio
    assets_response = []
    total_value = portfolio.available_money

    for asset in portfolio.assets:
        current_price = get_crypto_price(asset.symbol)
        net_quantity = asset.quantity
        asset_value = current_price * net_quantity
        total_value += asset_value

        transactions = (
            db.query(Transaction)
            .filter(
                Transaction.portfolio_id == portfolio.id,
                Transaction.symbol == asset.symbol,
            )
            .all()
        )

        total_cost = 0
        total_bought = 0

        for t in transactions:
            if t.quantity > 0:
                total_cost += t.quantity * t.price
                total_bought += t.quantity

        avg_purchase_price = total_cost / total_bought if total_bought > 0 else 0
        invested_amount = avg_purchase_price * net_quantity

        assets_response.append(
            {
                "symbol": asset.symbol,
                "quantity": asset.quantity,
                "current_price": current_price,
                "total_value": asset_value,
                "avg_purchase_price": avg_purchase_price,
                "performance_abs": asset_value - invested_amount,
                "performance_rel": (
                    ((asset_value - invested_amount) / invested_amount * 100)
                    if invested_amount != 0
                    else 0
                ),
            }
        )

    return {
        "total_added_money": portfolio.total_added_money,
        "available_money": portfolio.available_money,
        "total_value": total_value,
        "performance_abs": total_value - portfolio.total_added_money,
        "performance_rel": (
            (
                (total_value - portfolio.total_added_money)
                / portfolio.total_added_money
                * 100
            )
            if portfolio.total_added_money != 0
            else 0
        ),
        "assets": assets_response,
    }
