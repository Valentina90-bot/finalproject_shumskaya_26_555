import json
import os


class DatabaseManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._init_db()
        return cls._instance

    def _init_db(self):
        os.makedirs("data", exist_ok=True)

    def read_json(self, file_path: str):
        if not os.path.exists(file_path):
            return {} if "rates" in file_path or "portfolios" in file_path else []
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {} if "rates" in file_path or "portfolios" in file_path else []

    def write_json_atomic(self, file_path: str, data):
        dir_name = os.path.dirname(file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
            
        temp_path = f"{file_path}.tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        os.replace(temp_path, file_path)
