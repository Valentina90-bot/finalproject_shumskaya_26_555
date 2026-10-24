import logging
from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.logging_config import setup_logging
from valutatrade_hub.parser_service.storage import ParserStorage

logger = setup_logging()

class RatesUpdater:
    def __init__(self, clients: list, storage: ParserStorage):
        self.clients = clients
        self.storage = storage

    def run_update(self, target_source: str | None = None) -> int:
        print("INFO: Starting rates update...")
        logger.info("Starting rates update process")
        
        total_updated = 0
        src = target_source.lower().strip() if target_source else None

        for client in self.clients:
            client_name = type(client).__name__
            if "CoinGeckoClient" in client_name:
                source_label = "CoinGecko"
                filter_key = "coingecko"
            else:
                source_label = "ExchangeRate-API"
                filter_key = "exchangerate"

            if src and src != filter_key:
                continue

            try:
                print(f"INFO: Fetching from {source_label}...")
                rates = client.fetch_rates()
                
                for pair, rate in rates.items():
                    from_curr, to_curr = pair.split("_")
                    self.storage.save_rate_entry(from_curr, to_curr, rate, source_label)
                    total_updated += 1
                    
                print(f"INFO: Fetching from {source_label}... OK ({len(rates)} rates)")
                logger.info(f"{source_label} update successful: {len(rates)} rates")
                
            except ApiRequestError as e:
                print(f"ERROR: Failed to fetch from {source_label}: {e}")
                logger.error(f"{source_label} update failed: {e}")

        return total_updated
