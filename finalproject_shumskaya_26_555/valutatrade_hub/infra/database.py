import os
import json
from valutatrade_hub.infra.settings import SettingsLoader

class DatabaseManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._init_db()
        return cls._instance

    def _init_db(self):
        settings = SettingsLoader()
        self._users_file = settings.get("users_file")
        self._portfolios_file = settings.get("portfolios_file")
        self._rates_file = settings.get("rates_file")
        self._init_storage()

    def _init_storage(self):
        data_dir = SettingsLoader().get("data_dir")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        for file_path in [self._users_file, self._portfolios_file, self._rates_file]:
            if not os.path.exists(file_path):
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump([] if file_path != self._rates_file else {}, f, ensure_ascii=False, indent=2)

    def read_json(self, file_type: str):
        file_path = getattr(self, f"_{file_type}_file")
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return [] if file_type != "rates" else {}

    def write_json(self, file_type: str, data):
        file_path = getattr(self, f"_{file_type}_file")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
