from abc import ABC, abstractmethod

from valutatrade_hub.core.exceptions import CurrencyNotFoundError


class Currency(ABC):
    def __init__(self, name: str, code: str):
        if not name or not name.strip():
            raise ValueError("РРјСЏ РІР°Р»СЋС‚С‹ РЅРµ РјРѕР¶РµС‚ Р±С‹С‚СЊ РїСѓСЃС‚С‹Рј")
        
        cleaned_code = code.upper().strip()
        if not (2 <= len(cleaned_code) <= 5) or " " in cleaned_code:
            raise ValueError("РљРѕРґ РІР°Р»СЋС‚С‹ РґРѕР»Р¶РµРЅ Р±С‹С‚СЊ РґР»РёРЅРѕР№ РѕС‚ 2 РґРѕ 5 СЃРёРјРІРѕР»РѕРІ Р±РµР· РїСЂРѕР±РµР»РѕРІ")
            
        self.name = name.strip()
        self.code = cleaned_code

    @abstractmethod
    def get_display_info(self) -> str:
        pass


class FiatCurrency(Currency):
    def __init__(self, name: str, code: str, issuing_country: str):
        super().__init__(name, code)
        self.issuing_country = issuing_country.strip()

    def get_display_info(self) -> str:
        return f"[FIAT] {self.code} вЂ” {self.name} (Issuing: {self.issuing_country})"


class CryptoCurrency(Currency):
    def __init__(self, name: str, code: str, algorithm: str, market_cap: float):
        super().__init__(name, code)
        self.algorithm = algorithm.strip()
        self.market_cap = float(market_cap)

    def get_display_info(self) -> str:
        return f"[CRYPTO] {self.code} вЂ” {self.name} (Algo: {self.algorithm}, MCAP: {self.market_cap:.2e})"


def get_currency(code: str) -> Currency:
    cleaned = code.upper().strip()
    registry = {
        "USD": FiatCurrency("US Dollar", "USD", "United States"),
        "EUR": FiatCurrency("Euro", "EUR", "Eurozone"),
        "RUB": FiatCurrency("Russian Ruble", "RUB", "Russia"),
        "BTC": CryptoCurrency("Bitcoin", "BTC", "SHA-256", 1.12e12),
        "ETH": CryptoCurrency("Ethereum", "ETH", "Ethash", 4.5e11)
    }
    if cleaned not in registry:
        raise CurrencyNotFoundError(cleaned)
    return registry[cleaned]
