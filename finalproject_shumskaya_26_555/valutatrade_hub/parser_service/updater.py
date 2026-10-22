from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.logging_config import setup_logging
from valutatrade_hub.parser_service.config import ParserConfig
from valutatrade_hub.parser_service.storage import ParserStorage
from valutatrade_hub.parser_service.api_clients import CoinGeckoClient, ExchangeRateApiClient

logger = setup_logging()

class RatesUpdater:
    def __init__(self, config: ParserConfig, storage: ParserStorage):
        self.config = config
        self.storage = storage
        self.coingecko_client = CoinGeckoClient(config)
        self.exchangerate_client = ExchangeRateApiClient(config)

    def run_update(self, source_filter: str = None) -> int:
        print("INFO: Starting rates update...")
        logger.info("Starting rates update process")
        
        total_updated = 0
        src = source_filter.lower().strip() if source_filter else None

        if not src or src == "coingecko":
            try:
                print("INFO: Fetching from CoinGecko...")
                crypto_rates = self.coingecko_client.fetch_rates()
                for pair, rate in crypto_rates.items():
                    from_curr, to_curr = pair.split("_")
                    self.storage.save_rate_entry(from_curr, to_curr, rate, "CoinGecko")
                    total_updated += 1
                print(f"INFO: Fetching from CoinGecko... OK ({len(crypto_rates)} rates)")
                logger.info(f"CoinGecko update successful: {len(crypto_rates)} rates")
            except ApiRequestError as e:
                print(f"ERROR: Failed to fetch from CoinGecko: {e}")
                logger.error(f"CoinGecko update failed: {e}")

        if not src or src == "exchangerate":
            try:
                print("INFO: Fetching from ExchangeRate-API...")
                fiat_rates = self.exchangerate_client.fetch_rates()
                for pair, rate in fiat_rates.items():
                    from_curr, to_curr = pair.split("_")
                    self.storage.save_rate_entry(from_curr, to_curr, rate, "ExchangeRate-API")
                    total_updated += 1
                print(f"INFO: Fetching from ExchangeRate-API... OK ({len(fiat_rates)} rates)")
                logger.info(f"ExchangeRate-API update successful: {len(fiat_rates)} rates")
            except ApiRequestError as e:
                print(f"ERROR: Failed to fetch from ExchangeRate-API: {e}")
                logger.error(f"ExchangeRate-API update failed: {e}")

        return total_updated
