# Search Service

Простой поисковый сервис на FastAPI + PostgreSQL + Elasticsearch.

## Возможности

- **Поиск**: `GET /api/v1/search?query=<текст>` — возвращает до 20 документов, отсортированных по дате создания (DESC). Поиск идёт по полю `text` в Elasticsearch, полные данные подтягиваются из PostgreSQL.
- **Удаление**: `DELETE /api/v1/documents/{id}` — удаляет документ из БД и из поискового индекса.
- **Автозагрузка данных** из `posts.csv` при старте контейнера.
- **OpenAPI-документация** доступна по адресу `/docs` и в файле `docs.json`.

## Технологии

- **Python** 3.12
- **FastAPI** — веб-фреймворк
- **SQLAlchemy 2.x (async)** + **asyncpg** — доступ к PostgreSQL
- **Elasticsearch 8.13** + **elasticsearch-py 8.13** — полнотекстовый поиск
- **Pydantic v2** + **pydantic-settings** — валидация и конфигурация
- **uv** — управление зависимостями и виртуальным окружением
- **Docker / Docker Compose** — упаковка и запуск
- **pytest** + **pytest-asyncio** + **httpx** — функциональные тесты

## Требования

- Docker 20.10+ и Docker Compose v2
- (опционально, для локальной разработки) Python 3.12 и `uv`

Установить `uv`:

Linux / macOS:
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows (PowerShell):
```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Быстрый старт

1. Клонируйте репозиторий и перейдите в его каталог.

2. Положите `posts.csv` в корень проекта. Формат — CSV с колонками:
   - `text` — текст документа;
   - `created_date` — дата создания в формате ISO 8601;
   - `rubrics` — строковое представление Python-списка, например `"['VK-123', 'VK-456']"`.

3. Поднимите сервис:
```
docker compose up --build
```

4. Откройте интерактивную документацию:
   - Swagger UI — http://localhost:8000/docs
   - ReDoc — http://localhost:8000/redoc
   - OpenAPI JSON — http://localhost:8000/openapi.json

## API

### Поиск документов

```
GET /api/v1/search?query=<текст>
```

Параметры:

| Имя     | Тип    | Обязательный | Описание                        |
|---------|--------|--------------|---------------------------------|
| `query` | string | да           | Поисковый запрос (любой текст)  |

Ответ: массив документов (до 20), отсортированных по `created_date` по убыванию.

Пример:
```
curl "http://localhost:8000/api/v1/search?query=конкурс"
```

```
[
  {
    "id": 42,
    "text": "Конкурс на НОВЫЙ СКИН ...",
    "rubrics": ["VK-1603736028819866", "VK-95883495386", "VK-55347043459"],
    "created_date": "2019-05-31T17:18:42"
  }
]
```

### Удаление документа

```
DELETE /api/v1/documents/{document_id}
```

Ответы:
- `200 OK` — документ удалён из БД и индекса;
- `404 Not Found` — документа с таким `id` нет в БД.

Пример:
```
curl -X DELETE http://localhost:8000/api/v1/documents/42
```

### Health-check

```
GET /
```

Возвращает `{"message": "Welcome to the Search Service"}`.

## Конфигурация

Параметры читаются через `pydantic-settings` из переменных окружения (или из файла `.env`, если он есть в корне проекта).

| Переменная            | Значение по умолчанию                                     | Описание                   |
|-----------------------|-----------------------------------------------------------|----------------------------|
| `DATABASE_URL`        | `postgresql+asyncpg://user:password@db:5432/search_db`    | DSN PostgreSQL             |
| `ELASTICSEARCH_URL`   | `http://elasticsearch:9200`                               | URL кластера Elasticsearch |
| `ELASTICSEARCH_INDEX` | `documents`                                               | Имя поискового индекса     |

При запуске через `docker-compose.yml` переменные задаются автоматически в сервисе `app`. При локальном запуске вне Docker их можно переопределить через `.env`-файл (используйте адреса `localhost`, так как порты `5432` и `9200` проброшены на хост).

## Тесты

Тесты функциональные: они обращаются к реальным PostgreSQL и Elasticsearch, поэтому запускать их нужно внутри Docker-контейнера, где оба сервиса доступны по именам `db` и `elasticsearch`.

Порядок запуска:

1. Поднимите сервисы и дождитесь, пока они станут healthy:
```
docker compose up -d
```

2. Загрузите данные в БД и индекс (если ещё не загружены):
```
docker compose run --rm app python -m app.scripts.load_data
```

3. Запустите тесты:
```
docker compose run --rm app uv run pytest -v
```

Ожидаемый результат:
```
collected 3 items

tests/test_api.py::test_search_documents PASSED       [ 33%]
tests/test_api.py::test_search_non_existent PASSED    [ 66%]
tests/test_api.py::test_delete_document PASSED        [100%]

================================= 3 passed in 1.70s =================================
```

## Структура проекта

```
.
├── app/
│   ├── api/v1/endpoints.py      # HTTP-эндпоинты
│   ├── core/config.py           # Настройки (pydantic-settings)
│   ├── crud/document.py         # Операции с БД
│   ├── db/
│   │   ├── base.py              # Declarative Base
│   │   └── session.py           # Движок и фабрика сессий
│   ├── elastic/search.py        # Работа с Elasticsearch
│   ├── models/document.py       # ORM-модель Document
│   ├── schemas/document.py      # Pydantic-схемы
│   ├── scripts/load_data.py     # Загрузка posts.csv
│   └── main.py                  # Точка входа FastAPI
├── tests/
│   ├── conftest.py              # Фикстуры pytest
│   └── test_api.py              # Функциональные тесты
├── Dockerfile
├── docker-compose.yml
├── docs.json                    # OpenAPI-спецификация
├── posts.csv                    # Исходные данные
├── pyproject.toml
├── uv.lock
└── README.md
```
