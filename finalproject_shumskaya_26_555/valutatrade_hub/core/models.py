import hashlib
from datetime import datetime
from valutatrade_hub.core.exceptions import InsufficientFundsError


class User:
    def __init__(self, user_id: int, username: str, hashed_password: str, salt: str, registration_date: str | None = None):
        self._user_id = user_id
        self._username = None  
        self.username = username 
        self._hashed_password = hashed_password
        self._salt = salt
        
        if registration_date is None:
            self._registration_date = datetime.now()
        elif isinstance(registration_date, datetime):
            self._registration_date = registration_date
        else:
            self._registration_date = datetime.fromisoformat(registration_date)


    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, value: str):
        if not value or not value.strip():
            raise ValueError("Имя пользователя не может быть пустым!")
        self._username = value.strip()

    @property
    def registration_date(self) -> datetime:
        return self._registration_date

    def get_user_info(self) -> str:
        date_str = self._registration_date.strftime("%Y-%m-%d %H:%M:%S")
        return f"ID: {self._user_id} | Логин: {self._username} | Дата регистрации: {date_str}"

    @staticmethod
    def hash_password(password: str, salt: str) -> str:
        salted = password + salt
        return hashlib.sha256(salted.encode('utf-8')).hexdigest()

    def change_password(self, new_password: str):
        if len(new_password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов!")
        self._hashed_password = self.hash_password(new_password, self._salt)

    def verify_password(self, password: str) -> bool:
        return self._hashed_password == self.hash_password(password, self._salt)


class Wallet:
    def __init__(self, currency_code: str, balance: float = 0.0):
        self.currency_code = currency_code.upper().strip()
        self.balance = balance

    @property
    def balance(self) -> float:
        return self._balance

    @balance.setter
    def balance(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("Баланс должен быть числом!")
        if value < 0:
            raise ValueError("Баланс не может быть отрицательным!")
        self._balance = float(value)

    def deposit(self, amount: float):
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительным числом!")
        self.balance += amount

    def withdraw(self, amount: float):
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Сумма снятия должна быть положительным числом!")
        if amount > self._balance:
            raise InsufficientFundsError(self._balance, amount, self.currency_code)
        self.balance -= amount

    def get_balance_info(self) -> str:
        return f"Валюта: {self.currency_code} | Баланс: {self._balance:.4f}"


class Portfolio:
    def __init__(self, user_id: int, wallets: dict[str, Wallet] | None = None):
        self._user_id = user_id
        self._wallets = wallets if wallets is not None else {}

    @property
    def user(self) -> int:
        return self._user_id

    @property
    def wallets(self) -> dict[str, Wallet]:
        return self._wallets.copy()

    def add_currency(self, currency_code: str):
        code = currency_code.upper().strip()
        if code in self._wallets:
            raise ValueError(f"Кошелек для валюты {code} уже существует!")
        self._wallets[code] = Wallet(currency_code=code)

    def get_wallet(self, currency_code: str) -> Wallet | None:
        code = currency_code.upper().strip()
        return self._wallets.get(code)


    def get_total_value(self, base_currency: str = 'USD') -> float:
        base = base_currency.upper().strip()
        exchange_rates = {
            'USD': 1.0,
            'EUR': 1.0786,
            'BTC': 59337.21,
            'RUB': 0.01016,
            'ETH': 3720.00
        }
        if base not in exchange_rates:
            raise ValueError(f"Неизвестная базовая валюта '{base}'")
        
        total_in_usd = 0.0
        for code, wallet in self._wallets.items():
            if code in exchange_rates:
                total_in_usd += wallet.balance * exchange_rates[code]
        
        return total_in_usd / exchange_rates[base]
