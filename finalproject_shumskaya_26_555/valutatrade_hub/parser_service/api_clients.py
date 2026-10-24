from abc import ABC, abstractmethod
import requests
from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.parser_service.config import ParserConfig

class BaseApiClient(ABC):
    def __init__(self, config: ParserConfig):
        self.config = config

    @abstractmethod
    def fetch_rates(self) -> dict:
        pass

class CoinGeckoClient(BaseApiClient):
    def fetch_rates(self) -> dict:
        ids = ",".join(self.config.CRYPTO_ID_MAP.values())
        params = {"ids": ids, "vs_currencies": self.config.BASE_CURRENCY.lower()}
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        url = f"{self.config.COINGECKO_URL}/simple/price"
        
        try:
            response = requests.get(
                url, 
                params=params, 
                headers=headers,
                timeout=self.config.REQUEST_TIMEOUT
            )
            response.encoding = "utf-8"
            if response.status_code != 200:
                raise ApiRequestError(f"CoinGecko вернул статус {response.status_code}")
                
            data = response.json()
            standardized_rates = {}
            
            for code, cg_id in self.config.CRYPTO_ID_MAP.items():
                if cg_id in data and self.config.BASE_CURRENCY.lower() in data[cg_id]:
                    rate = data[cg_id][self.config.BASE_CURRENCY.lower()]
                    standardized_rates[f"{code}_{self.config.BASE_CURRENCY}"] = float(rate)
                    
            return standardized_rates
            
        except requests.exceptions.RequestException as e:
            raise ApiRequestError(f"Сбой сети при запросе к CoinGecko: {e}")

class ExchangeRateApiClient(BaseApiClient):
    def fetch_rates(self) -> dict:
        url = f"{self.config.EXCHANGERATE_API_URL}/{self.config.EXCHANGERATE_API_KEY}/latest/{self.config.BASE_CURRENCY}"
        
        try:
            response = requests.get(url, timeout=self.config.REQUEST_TIMEOUT)
            response.encoding = "utf-8"
            if response.status_code != 200:
                raise ApiRequestError(f"ExchangeRate-API вернул статус {response.status_code}. Ответ: {response.text}")
                
            data = response.json()
            if data.get("result") != "success":
                raise ApiRequestError(f"ExchangeRate-API сообщил об ошибке: {data.get('error-type', 'unknown')}")

            rates = data.get("conversion_rates", {})
            standardized_rates = {}
            
            for code in self.config.FIAT_CURRENCIES:
                if code in rates:
                    rate = rates[code]
                    standardized_rates[f"{code}_{self.config.BASE_CURRENCY}"] = 1.0 / float(rate)
                    
            return standardized_rates
            
        except requests.exceptions.RequestException as e:
            raise ApiRequestError(f"Сбой сети при запросе к ExchangeRate-API: {e}")
