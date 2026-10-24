import os
import json
import secrets
from datetime import datetime

from valutatrade_hub.core.currencies import get_currency
from valutatrade_hub.core.exceptions import ApiRequestError, InsufficientFundsError, CurrencyNotFoundError
from valutatrade_hub.core.models import Portfolio, User, Wallet
from valutatrade_hub.decorators import log_action
from valutatrade_hub.infra.database import DatabaseManager

CURRENT_USER = None
db_manager = DatabaseManager()

USERS_FILE = "data/users.json"
PORTFOLIOS_FILE = "data/portfolios.json"
RATES_FILE = "data/rates.json"


def load_users() -> list:
    return db_manager.read_json(USERS_FILE)


def save_users(users_data: list):
    db_manager.write_json_atomic(USERS_FILE, users_data)


def load_portfolios() -> list:
    return db_manager.read_json(PORTFOLIOS_FILE)


def save_portfolios(portfolios_data: list):
    db_manager.write_json_atomic(PORTFOLIOS_FILE, portfolios_data)


@log_action("REGISTER")
def register_user(username: str, password: str) -> str:
    if len(password) < 4:
        raise ValueError("Пароль должен быть не короче 4 символов")

    users = load_users()
    for u in users:
        if u["username"].lower() == username.lower():
            raise ValueError(f"Имя пользователя '{username}' уже занято")

    user_id = max([u["user_id"] for u in users], default=0) + 1
    salt = secrets.token_hex(4)
    
    temp_user = User(user_id, username, "", salt, datetime.now())
    temp_user.change_password(password)

    new_user = {
        "user_id": user_id,
        "username": username,
        "hashed_password": temp_user._hashed_password,
        "salt": salt,
        "registration_date": temp_user.registration_date.isoformat(),
    }
    users.append(new_user)
    save_users(users)

    portfolios = load_portfolios()
    portfolios.append({"user_id": user_id, "wallets": {}})
    save_portfolios(portfolios)

    return f"Пользователь '{username}' зарегистрирован (id={user_id}). Войдите: login --username {username} --password ****"


@log_action("LOGIN")
def login_user(username: str, password: str) -> str:
    global CURRENT_USER
    users = load_users()

    found_user_data = None
    for u in users:
        if u["username"].lower() == username.lower():
            found_user_data = u
            break

    if not found_user_data:
        raise ValueError(f"Пользователь '{username}' не найден")

    user_obj = User(
        user_id=found_user_data["user_id"],
        username=found_user_data["username"],
        hashed_password=found_user_data["hashed_password"],
        salt=found_user_data["salt"],
        registration_date=datetime.fromisoformat(found_user_data["registration_date"]),
    )

    if not user_obj.verify_password(password):
        raise ValueError("Неверный пароль")

    CURRENT_USER = user_obj
    return f"Вы вошли как '{user_obj.username}'"


def load_current_portfolio() -> Portfolio:
    if not CURRENT_USER:
        raise ValueError("Сначала выполните login")

    portfolios = load_portfolios()
    for p in portfolios:
        if p["user_id"] == CURRENT_USER.user_id:
            wallets_dict = {}
            for code, w_data in p["wallets"].items():
                wallets_dict[code] = Wallet(
                    currency_code=code, balance=w_data["balance"]
                )
            return Portfolio(
                user_id=CURRENT_USER.user_id, wallets=wallets_dict
            )

    return Portfolio(user_id=CURRENT_USER.user_id)


def save_current_portfolio(portfolio: Portfolio):
    portfolios = load_portfolios()
    wallets_json = {}
    for code, wallet in portfolio.wallets.items():
        wallets_json[code] = {
            "currency_code": wallet.currency_code,
            "balance": wallet.balance,
        }

    for p in portfolios:
        if p["user_id"] == portfolio.user:
            p["wallets"] = wallets_json
            break
    save_portfolios(portfolios)


def get_exchange_rate(from_curr: str, to_curr: str) -> float:
    f = get_currency(from_curr).code
    t = get_currency(to_curr).code

    if f == t:
        return 1.0

    rates_data = db_manager.read_json(RATES_FILE)
    pairs = rates_data.get("pairs", {})

    def get_rate_to_usd(code: str) -> float:
        if code == "USD":
            return 1.0
        pair_key = f"{code}_USD"
        if pair_key in pairs:
            return float(pairs[pair_key]["rate"])
        raise ApiRequestError(f"Курс {code}→USD временно недоступен в кэше. Запустите update-rates.")

    rate_f_usd = get_rate_to_usd(f)
    rate_t_usd = get_rate_to_usd(t)

    return rate_f_usd / rate_t_usd


@log_action("BUY")
def buy_currency(currency_code: str, amount: float) -> str:
    if amount <= 0:
        raise ValueError("'amount' должен быть положительным числом")

    currency = get_currency(currency_code)
    portfolio = load_current_portfolio()

    rate = get_exchange_rate(currency.code, "USD")

    if currency.code not in portfolio.wallets:
        portfolio.add_currency(currency.code)

    wallet = portfolio.get_wallet(currency.code)
    old_balance = wallet.balance
    wallet.deposit(amount)

    save_current_portfolio(portfolio)

    cost = amount * rate
    return (
        f"Покупка выполнена: {amount:.4f} {currency.code} по курсу {rate:.2f} USD/{currency.code}\n"
        f"Изменения в портфеле:\n"
        f"- {currency.code}: было {old_balance:.4f} → стало {wallet.balance:.4f}\n"
        f"Оценочная стоимость покупки: {cost:.2f} USD"
    )


@log_action("SELL")
def sell_currency(currency_code: str, amount: float) -> str:
    if amount <= 0:
        raise ValueError("'amount' должен быть положительным числом")

    currency = get_currency(currency_code)
    portfolio = load_current_portfolio()

    if currency.code not in portfolio.wallets:
        raise ValueError(
            f"У вас нет кошелька '{currency.code}'. Добавьте валюту: она создаётся автоматически при первой покупке."
        )

    wallet = portfolio.get_wallet(currency.code)
    if wallet.balance < amount:
        raise InsufficientFundsError(wallet.balance, amount, currency.code)

    rate = get_exchange_rate(currency.code, "USD")

    old_balance = wallet.balance
    wallet.withdraw(amount)

    save_current_portfolio(portfolio)

    revenue = amount * rate
    return (
        f"Продажа выполнена: {amount:.4f} {currency.code} по курсу {rate:.2f} USD/{currency.code}\n"
        f"Изменения в портфеле:\n"
        f"- {currency.code}: было {old_balance:.4f} → стало {wallet.balance:.4f}\n"
        f"Оценочная выручка: {revenue:.2f} USD"
    )
