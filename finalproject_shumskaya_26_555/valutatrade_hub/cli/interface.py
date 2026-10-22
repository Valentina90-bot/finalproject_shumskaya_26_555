import sys

from valutatrade_hub.core import usecases
from valutatrade_hub.core.currencies import get_currency
from valutatrade_hub.core.exceptions import (
    ApiRequestError,
    CurrencyNotFoundError,
    InsufficientFundsError,
)
from valutatrade_hub.parser_service.config import ParserConfig
from valutatrade_hub.parser_service.storage import ParserStorage
from valutatrade_hub.parser_service.updater import RatesUpdater


def parse_args(args: list) -> dict:
    parsed = {}
    current_key = None
    for arg in args:
        if arg.startswith("--"):
            current_key = arg[2:]
            parsed[current_key] = True
        elif current_key:
            if parsed[current_key] is True:
                parsed[current_key] = arg
            else:
                if not isinstance(parsed[current_key], list):
                    parsed[current_key] = [parsed[current_key]]
                parsed[current_key].append(arg)
            current_key = None
    return parsed

def run_cli():
    if len(sys.argv) < 2:
        print("Использование: main.py <команда> [аргументы]")
        return

    command = sys.argv[1].lower()
    parsed_args = parse_args(sys.argv[2:])

    try:
        if command == "register":
            username = parsed_args.get("username")
            password = parsed_args.get("password")
            if not username or username is True or not password or password is True:
                print("Ошибка: Требуются аргументы --username <str> и --password <str>")
                return
            res = usecases.register_user(username, password)
            print(res)

        elif command == "login":
            username = parsed_args.get("username")
            password = parsed_args.get("password")
            if not username or username is True or not password or password is True:
                print("Ошибка: Требуются аргументы --username <str> и --password <str>")
                return
            res = usecases.login_user(username, password)
            print(res)

        elif command == "show-portfolio":
            base = parsed_args.get("base", "USD")
            if base is True:
                base = "USD"
            
            try:
                base_currency = get_currency(base)
            except CurrencyNotFoundError:
                print(f"Неизвестная базовая валюта '{base}'")
                return

            portfolio = usecases.load_current_portfolio()
            print(f"Портфель пользователя '{usecases.CURRENT_USER.username}' (база: {base_currency.code}):")
            
            if not portfolio.wallets:
                print("  Кошельки пока не добавлены.")
            else:
                for code, wallet in portfolio.wallets.items():
                    try:
                        rate = usecases.get_exchange_rate(code, base_currency.code)
                        val_in_base = wallet.balance * rate
                        print(f"- {code}: {wallet.balance:.4f}  → {val_in_base:.2f} {base_currency.code}")
                    except (CurrencyNotFoundError, ApiRequestError):
                        print(f"- {code}: {wallet.balance:.4f}  → Ошибка конвертации")
            
            try:
                total = portfolio.get_total_value(base_currency.code)
                print("-" * 33)
                print(f"ИТОГО: {total:,.2f} {base_currency.code}")
            except ValueError as e:
                print("-" * 33)
                print(f"Ошибка подсчета итоговой стоимости: {e}")

        elif command == "buy":
            currency = parsed_args.get("currency")
            amount_str = parsed_args.get("amount")
            if not currency or currency is True or not amount_str or amount_str is True:
                print("Ошибка: Требуются аргументы --currency <str> и --amount <float>")
                return
            try:
                amount = float(amount_str)
            except ValueError:
                print("Ошибка: 'amount' должен быть числом")
                return
            res = usecases.buy_currency(currency, amount)
            print(res)

        elif command == "sell":
            currency = parsed_args.get("currency")
            amount_str = parsed_args.get("amount")
            if not currency or currency is True or not amount_str or amount_str is True:
                print("Ошибка: Требуются аргументы --currency <str> и --amount <float>")
                return
            try:
                amount = float(amount_str)
            except ValueError:
                print("Ошибка: 'amount' должен быть числом")
                return
            res = usecases.sell_currency(currency, amount)
            print(res)

        elif command == "get-rate":
            from_curr = parsed_args.get("from")
            to_curr = parsed_args.get("to")
            if not from_curr or from_curr is True or not to_curr or to_curr is True:
                print("Ошибка: Требуются аргументы --from <str> и --to <str>")
                return
            
            from_obj = get_currency(from_curr)
            to_obj = get_currency(to_curr)
            
            rate = usecases.get_exchange_rate(from_obj.code, to_obj.code)
            print(f"Курс {from_obj.code}→{to_obj.code}: {rate:.8f}")
            try:
                rev_rate = usecases.get_exchange_rate(to_obj.code, from_obj.code)
                print(f"Обратный курс {to_obj.code}→{from_obj.code}: {rev_rate:.2f}")
            except (CurrencyNotFoundError, ApiRequestError):
                pass

        elif command == "update-rates":
            source = parsed_args.get("source")
            if source is True:
                source = None
            cfg = ParserConfig()
            storage = ParserStorage(cfg.RATES_FILE_PATH, cfg.HISTORY_FILE_PATH)
            updater = RatesUpdater(cfg, storage)

            import datetime
           
            updated = updater.run_update(source_filter=source)
            timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%S")
            print(f"Update successful. Total rates updated: {updated}. Last refresh: {timestamp}")

        elif command == "show-rates":
            cfg = ParserConfig()
            storage = ParserStorage(cfg.RATES_FILE_PATH, cfg.HISTORY_FILE_PATH)
            rates_data = storage.load_rates()
            
            pairs = rates_data.get("pairs", {})
            if not pairs:
                print("Локальный кеш курсов пуст. Выполните 'update-rates', чтобы загрузить данные.")
                return
                
            print(f"Rates from cache (updated at {rates_data.get('last_refresh', 'unknown')}):")
            
            currency_filter = parsed_args.get("currency")
            top_str = parsed_args.get("top")
            
            items = list(pairs.items())
            
            if currency_filter and currency_filter is not True:
                items = [item for item in items if item[0].startswith(currency_filter.upper())]
                if not items:
                    print(f"Курс для '{currency_filter}' не найден в кеше.")
                    return
                    
            if top_str and top_str is not True:
                try:
                    top_n = int(top_str)
                    items.sort(key=lambda x: x[1]["rate"], reverse=True)
                    items = items[:top_n]
                except ValueError:
                    print("Ошибка: Аргумент --top должен быть числом")
                    return
            else:
                items.sort(key=lambda x: x[0])
                
            for pair, info in items:
                print(f"- {pair}: {info['rate']:.4f}")

        else:
            print(f"Неизвестная команда '{command}'")

    except InsufficientFundsError as e:
        print(e)
    except CurrencyNotFoundError as e:
        print(e)
        print("Используйте поддерживаемые коды валют: USD, EUR, RUB, BTC, ETH")
    except ApiRequestError as e:
        print(e)
        print("Пожалуйста, повторите попытку позже или проверьте сетевое подключение.")
    except ValueError as e:
        print(f"Ошибка: {e}")
