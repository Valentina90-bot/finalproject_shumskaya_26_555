import os
from typing import Any


class SettingsLoader:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._init_settings()
        return cls._instance

    def _init_settings(self):
        self._config = {
            "data_dir": "data",
            "users_file": os.path.join("data", "users.json"),
            "portfolios_file": os.path.join("data", "portfolios.json"),
            "rates_file": os.path.join("data", "rates.json"),
            "rates_ttl_seconds": 300,
            "default_base_currency": "USD",
            "log_file": os.path.join("data", "actions.log"),
            "log_format": "%(levelname)s %(asctime)s %(message)s"
        }

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)
