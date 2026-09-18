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
поэтому по согласованию с преподавателем целевой платформой выбран **Railway**. Суть задания сохранена полностью:

| Требование задания                          | Реализация                                                         |
|---------------------------------------------|--------------------------------------------------------------------|
| Сборка только через GitHub Actions          | [classroom.yml](.github/workflows/classroom.yml)                    |
| Деплой средствами Actions, без CLI и webhook | шаг `Deploy to Railway` — GraphQL-мутация к Public API через `curl` |
| Деплой через Docker                         | Railway собирает и запускает [Dockerfile](Dockerfile)               |
| БД для хранения записей                     | Postgres (локально — docker compose, в облаке — Railway Postgres)   |
| Интеграционные тесты после деплоя           | `newman` по postman-коллекции против задеплоенного URL              |

### Стек

* Python 3.12, FastAPI, SQLAlchemy 2.0 (psycopg 3)
* Postgres 13
* pytest для unit-тестов, newman для интеграционных
* Docker, GitHub Actions, Railway

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

Unit-тесты (14 штук, изолированная in-memory БД на каждый тест):

```shell
pytest
```

Интеграционные тесты против локального стека:

```shell
npx newman run "postman/[inst] Lab1.postman_collection.json" \
  -e "postman/[inst][local] Lab1.postman_environment.json" --delay-request 100
```

### Настройка деплоя на Railway

1. Создать проект: **New Project** → **Deploy from GitHub repo** → этот репозиторий. Railway найдёт `Dockerfile`
   и соберёт образ из него.
2. В проект добавить базу: **New** → **Database** → **Add PostgreSQL**.
3. В сервисе приложения на вкладке **Variables** задать `DATABASE_URL` со ссылкой на переменную базы:
   `${{Postgres.DATABASE_URL}}`. Схему `postgresql://...` код сам приводит к драйверу psycopg 3, править руками
   ничего не нужно.
4. **Settings** → **Networking** → **Generate Domain**: без этого у сервиса нет публичного адреса.
5. **Settings** → **Deploys** → выключить autodeploy, иначе Railway будет катить по каждому push мимо пайплайна.
6. Завести secrets репозитория (`Settings` → `Secrets and variables` → `Actions`):

   | Secret                   | Где взять                                                                        |
   |--------------------------|----------------------------------------------------------------------------------|
   | `RAILWAY_API_TOKEN`      | Account Settings → Tokens → Create Token                                         |
   | `RAILWAY_SERVICE_ID`     | id сервиса `person-service`                                                      |
   | `RAILWAY_ENVIRONMENT_ID` | id окружения `production`                                                        |

   Идентификаторы надёжнее взять из самого API, а не из адресной строки:

   ```shell
   curl -s -X POST https://backboard.railway.com/graphql/v2 \
     -H "Authorization: Bearer $RAILWAY_API_TOKEN" -H 'Content-Type: application/json' \
     -d '{"query":"query { projects { edges { node { id name environments { edges { node { id name } } } services { edges { node { id name } } } } } } }"}'
   ```

7. В [[inst][heroku] Lab1.postman_environment.json](postman/%5Binst%5D%5Bheroku%5D%20Lab1.postman_environment.json)
   заменить `baseUrl` на выданный Railway домен (например `https://person-service-production.up.railway.app`).

### Как работает pipeline

1. `checkout` → установка зависимостей → `pytest` (unit-тесты).
2. `docker build` — проверка, что образ собирается.
3. `Deploy to Railway` — мутация `serviceInstanceDeployV2` к Public API Railway обычным `curl` (только при
   push в `master`). CLI не используется. Мутации передаётся `commitSha` текущего прогона, поэтому выкатывается
   ровно тот коммит, который только что прошёл тесты.

   Мутация `environmentTriggersDeploy` для этой схемы не годится: она запускает триггеры окружения, а при
   выключенном autodeploy триггеров нет — запрос завершается успешно, но деплой не создаётся.
4. `Wait for deployed service` — поллинг `/manage/health` до тех пор, пока сервис не вернёт sha текущего коммита
   (Railway прокидывает его в `RAILWAY_GIT_COMMIT_SHA`). Так newman гарантированно бьёт по новой версии,
   а не по старой.
5. `Run API Tests` — newman по postman-коллекции.
6. `Autograding` + отметка в google-таблице.

Сборка образа и выкатка на Railway занимают несколько минут — таймаут ожидания в CI выставлен в 10 минут.
