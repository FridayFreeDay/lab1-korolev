# Лабораторная работа #1

![GitHub Classroom Workflow](../../workflows/GitHub%20Classroom%20Workflow/badge.svg?branch=master)

## Continuous Integration & Continuous Delivery

### Формулировка

Простейшее веб-приложение с набором операций над сущностью `Person`, для которого автоматизирован процесс сборки,
тестирования и релиза.

Приложение реализует API:

* `GET /api/v1/persons/{personId}` – информация о человеке;
* `GET /api/v1/persons` – информация по всем людям;
* `POST /api/v1/persons` – создание новой записи о человеке;
* `PATCH /api/v1/persons/{personId}` – обновление существующей записи о человеке;
* `DELETE /api/v1/persons/{personId}` – удаление записи о человеке.

[Описание API](person-service.yaml) в формате OpenAPI.

Дополнительно: `GET /manage/health` – проверка живости сервиса (используется платформой деплоя и CI).

### Отступление от исходного задания

В исходной формулировке деплой выполняется на Heroku. Heroku убрал Free Plan и недоступен для регистрации из РФ,
поэтому по согласованию с преподавателем целевой платформой выбран **Render**. Суть задания сохранена полностью:

| Требование задания                          | Реализация                                                         |
|---------------------------------------------|--------------------------------------------------------------------|
| Сборка только через GitHub Actions          | [classroom.yml](.github/workflows/classroom.yml)                    |
| Деплой средствами Actions, без CLI и webhook | шаг `Deploy to Render` — `POST` на Render Deploy Hook через `curl`  |
| Деплой через Docker                         | Render собирает и запускает [Dockerfile](Dockerfile)                |
| БД для хранения записей                     | Postgres (локально — docker compose, в облаке — managed Postgres)   |
| Интеграционные тесты после деплоя           | `newman` по postman-коллекции против задеплоенного URL              |

### Стек

* Python 3.12, FastAPI, SQLAlchemy 2.0 (psycopg 3)
* Postgres 13
* pytest для unit-тестов, newman для интеграционных
* Docker, GitHub Actions, Render

### Структура проекта

```
src/
├── config.py      # настройки из переменных окружения
├── database.py    # engine, сессии, инициализация схемы
├── models.py      # ORM-модель Person
├── schemas.py     # схемы запросов/ответов по OpenAPI
├── repository.py  # операции над хранилищем
├── errors.py      # доменные исключения и обработчики ошибок
├── router.py      # HTTP-эндпоинты
└── main.py        # сборка приложения
tests/             # unit-тесты (pytest, SQLite in-memory)
```

### Локальный запуск

Весь стек в Docker:

```shell
docker compose up -d --build
curl http://localhost:8080/manage/health
```

Только БД, приложение — локально:

```shell
docker compose up -d postgres
python -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
DATABASE_URL="postgresql+psycopg://program:test@localhost:5432/persons" .venv/bin/python -m src.main
```

### Тесты

Unit-тесты (12 штук, изолированная in-memory БД на каждый тест):

```shell
pytest
```

Интеграционные тесты против локального стека:

```shell
npx newman run "postman/[inst] Lab1.postman_collection.json" \
  -e "postman/[inst][local] Lab1.postman_environment.json" --delay-request 100
```

### Настройка деплоя на Render

1. Завести бесплатную БД в [Neon](https://neon.com) (free tier, карта не требуется) и скопировать connection
   string вида `postgresql://user:pass@host/persons?sslmode=require`.
2. В Render создать Blueprint из [render.yaml](render.yaml) либо завести Web Service вручную:
   `Runtime: Docker`, `Health Check Path: /manage/health`, `Auto-Deploy: Off`, переменная `DATABASE_URL` — строка
   подключения из п.1.
3. В настройках сервиса `Settings` → `Deploy Hook` скопировать URL и положить его в secret репозитория
   `RENDER_DEPLOY_HOOK` (`Settings` → `Secrets and variables` → `Actions`).
4. В [[inst][heroku] Lab1.postman_environment.json](postman/%5Binst%5D%5Bheroku%5D%20Lab1.postman_environment.json)
   заменить `baseUrl` на адрес сервиса на Render (например `https://person-service.onrender.com`).

Схема `postgres://...`, которую отдаёт Render, приводится к драйверу psycopg 3 в
[config.py](src/config.py) — отдельной правки переменной не требуется.

### Как работает pipeline

1. `checkout` → установка зависимостей → `pytest` (unit-тесты).
2. `docker build` — проверка, что образ собирается.
3. `Deploy to Render` — `POST` на Deploy Hook (только при push в `master`).
4. `Wait for deployed service` — поллинг `/manage/health` до тех пор, пока сервис не вернёт sha текущего коммита
   (Render прокидывает его в `RENDER_GIT_COMMIT`). Так newman гарантированно бьёт по новой версии, а не по старой.
5. `Run API Tests` — newman по postman-коллекции.
6. `Autograding` + отметка в google-таблице.

Бесплатный план Render усыпляет сервис при простое, холодный старт занимает до минуты — таймаут ожидания в CI
выставлен в 10 минут.
