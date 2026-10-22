import json
import os
from datetime import datetime

class ParserStorage:
    def __init__(self, rates_path: str, history_path: str):
        self.rates_path = rates_path
        self.history_path = history_path

    def _atomic_save(self, file_path: str, data: dict | list):
        temp_path = f"{file_path}.tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        if os.path.exists(file_path):
            os.remove(file_path)
        os.rename(temp_path, file_path)

    def load_history(self) -> list:
        if not os.path.exists(self.history_path):
            return []
        with open(self.history_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def load_rates(self) -> dict:
        if not os.path.exists(self.rates_path):
            return {"pairs": {}, "last_refresh": ""}
        with open(self.rates_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {"pairs": {}, "last_refresh": ""}

    def save_rate_entry(self, from_curr: str, to_curr: str, rate: float, source: str):
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        entry_id = f"{from_curr}_{to_curr}_{timestamp}"
        
        history = self.load_history()
        history.append({
            "id": entry_id,
            "from_currency": from_curr,
            "to_currency": to_curr,
            "rate": rate,
            "timestamp": timestamp,
            "source": source,
            "meta": {
                "status_code": 200
            }
        })
        self._atomic_save(self.history_path, history)

        rates_data = self.load_rates()
        pair_key = f"{from_curr}_{to_curr}"
        rates_data["pairs"][pair_key] = {
            "rate": rate,
            "updated_at": timestamp,
            "source": source
        }
        rates_data["last_refresh"] = timestamp
        self._atomic_save(self.rates_path, rates_data)
