import os
from dataclasses import dataclass, field


@dataclass
class ParserConfig:
    EXCHANGERATE_API_KEY: str = os.getenv("EXCHANGERATE_API_KEY", "3b47a9b92e1b14c1f1234567")

    COINGECKO_URL: str = "https://coingecko.com"
    EXCHANGERATE_API_URL: str = "https://exchangerate-api.com"

    BASE_CURRENCY: str = "USD"
    FIAT_CURRENCIES: tuple = ("EUR", "GBP", "RUB")
    CRYPTO_CURRENCIES: tuple = ("BTC", "ETH", "SOL")
    CRYPTO_ID_MAP: dict = field(default_factory=lambda: {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
    })

    RATES_FILE_PATH: str = "data/rates.json"
    HISTORY_FILE_PATH: str = "data/exchange_rates.json"

    REQUEST_TIMEOUT: int = 10
