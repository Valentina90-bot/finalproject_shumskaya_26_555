# ValutaTrade Hub

Комплексная консольная платформа на Python для отслеживания курсов валют и симуляции торговли (фиатные валюты и криптовалюты).

## Структура проекта
- `valutatrade_hub/core` — бизнес-логика, модели данных (`User`, `Wallet`, `Portfolio`) и кастомные исключения.
- `valutatrade_hub/infra` — инфраструктурные синглтоны для работы с базой данных JSON и конфигурацией.
- `valutatrade_hub/parser_service` — микросервис для автоматического сбора курсов валют через CoinGecko API и ExchangeRate-API.
- `valutatrade_hub/cli` — консольный интерфейс приложения.

## Установка и настройка

1. Убедитесь, что у вас установлен менеджер пакетов `uv`.
2. Установите зависимости проекта:
```bash
uv sync
```

3. Для работы службы парсинга фиатных валют добавьте ваш персональный ключ доступа к ExchangeRate-API в переменные окружения:
- **Для Windows (PowerShell):**
```powershell
\$env:EXCHANGERATE_API_KEY="ВАШ_КЛЮЧ_ДОСТУПА"
```

## Примеры использования CLI-команд

### Управление аккаунтом
```bash
uv run main.py register --username alice --password 1234
uv run main.py login --username alice --password 1234
```

### Просмотр портфеля и курсов
```bash
uv run main.py show-portfolio --base USD
uv run main.py get-rate --from BTC --to USD
```

### Торговые операции
```bash
uv run main.py buy --currency BTC --amount 0.05
uv run main.py sell --currency BTC --amount 0.02
```

### Управление парсером курсов
```bash
uv run main.py update-rates
uv run main.py show-rates --currency BTC
```
