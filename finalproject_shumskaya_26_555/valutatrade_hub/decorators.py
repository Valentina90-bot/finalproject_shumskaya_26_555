import functools
from valutatrade_hub.logging_config import setup_logging

logger = setup_logging()

def log_action(action_name: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            username = "unknown"
            from valutatrade_hub.core import usecases
            if usecases.CURRENT_USER:
                username = usecases.CURRENT_USER.username
            elif action_name in ["REGISTER", "LOGIN"] and len(args) > 0:
                username = args[0]

            currency_code = kwargs.get("currency_code")
            if not currency_code:
                currency_code = args[0] if action_name not in ["REGISTER", "LOGIN"] and len(args) > 0 else "N/A"

            amount = kwargs.get("amount")
            if amount is None:
                amount = args[1] if action_name not in ["REGISTER", "LOGIN"] and len(args) > 1 else "N/A"
            
            try:
                res = func(*args, **kwargs)
                logger.info(f"{action_name} user='{username}' currency='{currency_code}' amount={amount} result=OK")
                return res
            except Exception as e:
                error_type = e.__class__.__name__
                logger.info(f"{action_name} user='{username}' currency='{currency_code}' amount={amount} result=ERROR error_type='{error_type}'")
                raise
        return wrapper
    return decorator
