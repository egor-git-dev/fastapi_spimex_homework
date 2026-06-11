# SPIMEX FastAPI API

Микросервис на FastAPI для чтения торговых данных из таблицы
`spimex_trading_results` и выдачи результата в JSON.

## Стек

- FastAPI
- SQLAlchemy async
- asyncpg
- PostgreSQL
- Redis
- pytest
- httpx

## Структура

```text
app/
  main.py           # FastAPI приложение и эндпоинты
  database.py       # async-подключение к PostgreSQL
  models.py         # SQLAlchemy модель таблицы
  schemas.py        # Pydantic-схемы ответов
  crud.py           # запросы к БД
  cache.py          # Redis-кэширование
  config.py         # настройки приложения
  dependencies.py   # зависимости FastAPI
tests/
  test_api.py
requirements.txt
```

## Настройки

По умолчанию используются значения из `app/config.py`:

```text
db_url = postgresql+asyncpg://postgres:postgres@localhost:5432/spimex_db
redis_url = redis://localhost:6379/0
cache_reset_hour = 14
cache_reset_minute = 11
```

PostgreSQL должен содержать таблицу `spimex_trading_results`.
Redis должен быть запущен на `localhost:6379`.

## Установка

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Проверка Redis:

```bash
redis-cli ping
```

Ожидаемый ответ:

```text
PONG
```

## Запуск

```bash
uvicorn app.main:app --reload
```

Документация API:

```text
http://127.0.0.1:8000/docs
```

## Эндпоинты

### GET `/api/last-trading-dates`

Возвращает список последних торговых дат.

Параметры:

- `limit` - количество последних торговых дней, по умолчанию `10`, диапазон `1..100`.

Пример:

```text
/api/last-trading-dates?limit=10
```

Ответ:

```json
{
  "dates": ["2025-12-10", "2025-12-09"]
}
```

### GET `/api/dynamics`

Возвращает список торгов за заданный период.

Обязательные параметры:

- `start_date`
- `end_date`

Опциональные фильтры:

- `oil_id`
- `delivery_type_id`
- `delivery_basis_id`

Пример:

```text
/api/dynamics?start_date=2025-11-01&end_date=2025-12-01&oil_id=A100
```

Если `start_date` больше `end_date`, API возвращает `400 Bad Request`.

### GET `/api/trading-results`

Возвращает последние доступные торги.

Опциональные фильтры:

- `oil_id`
- `delivery_type_id`
- `delivery_basis_id`

Пример:

```text
/api/trading-results?oil_id=A100
```

Последняя дата определяется с учетом переданных фильтров. Это нужно, чтобы запрос
по конкретному товару не возвращал пустой результат только потому, что в самую
последнюю общую дату торгов по этому товару не было.

## Обязательные параметры

Для `/api/dynamics` параметры `start_date` и `end_date` обязательны, потому что
без периода запрос может вернуть слишком большой объем данных.

Для `/api/last-trading-dates` параметр `limit` имеет значение по умолчанию `10`.
Пользователь может изменить его, но полностью не передавать параметр допустимо.

Фильтры `oil_id`, `delivery_type_id`, `delivery_basis_id` опциональны: API должен
уметь возвращать как общую картину торгов, так и выборку по конкретным признакам.

## Кэширование

Все API-эндпоинты кэшируются в Redis.

Ключ кэша строится из:

- HTTP-метода;
- пути запроса;
- query-параметров в отсортированном порядке.

Параметры со значением `None` в ключ не попадают.

Пример ключа:

```text
GET:/api/dynamics?end_date=2025-12-01&oil_id=A100&start_date=2025-11-01
```

TTL рассчитывается до ближайших `14:11`.

Примеры:

- если сейчас `13:00`, кэш живет до `14:11` текущего дня;
- если сейчас `15:00`, кэш живет до `14:11` следующего дня.

Redis удаляет ключи автоматически после истечения TTL. Это обеспечивает ежедневную
инвалидацию кэша после расчетного времени обновления данных.

В логах uvicorn выводятся сообщения:

```text
Cache hit: ...
Cache miss: ...
```

## Тесты

Запуск тестов:

```bash
venv/bin/python -m pytest tests/test_api.py -q
```

Покрыты базовые сценарии:

- отсутствие обязательных дат в `/api/dynamics`;
- некорректный период в `/api/dynamics`;
- успешный ответ `/api/last-trading-dates` через mock;
- cache hit без обращения к CRUD;
- построение стабильного cache key;
- расчет TTL до `14:11`.
