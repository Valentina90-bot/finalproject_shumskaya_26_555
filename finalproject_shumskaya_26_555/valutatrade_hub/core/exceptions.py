class InsufficientFundsError(Exception):
    def __init__(self, available: float, required: float, code: str):
        self.available = available
        self.required = required
        self.code = code
        super().__init__(f"РќРµРґРѕСЃС‚Р°С‚РѕС‡РЅРѕ СЃСЂРµРґСЃС‚РІ: РґРѕСЃС‚СѓРїРЅРѕ {available:.4f} {code}, С‚СЂРµР±СѓРµС‚СЃСЏ {required:.4f} {code}")


class CurrencyNotFoundError(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(f"РќРµРёР·РІРµСЃС‚РЅР°СЏ РІР°Р»СЋС‚Р° '{code}'")


class ApiRequestError(Exception):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"РћС€РёР±РєР° РїСЂРё РѕР±СЂР°С‰РµРЅРёРё Рє РІРЅРµС€РЅРµРјСѓ API: {reason}")
