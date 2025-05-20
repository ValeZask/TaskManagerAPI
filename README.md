# Task Manager API

REST API для управления задачами с возможностью отслеживания истории изменений.

## Описание API

API позволяет:
- Создавать, читать, обновлять и удалять задачи (title, description, due_date, status)
- Фильтровать задачи по status (new, in_progress, done) и due_date
- Просматривать историю изменений задач
- Обрабатывать ошибки (валидация, дубли, некорректные данные)

## Эндпоинты

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/api/tasks/` | Создать задачу |
| GET | `/api/tasks/` | Получить список задач |
| GET | `/api/tasks/?status={value}` | Фильтрация по статусу |
| GET | `/api/tasks/?due_date={value}` | Фильтрация по дате |
| GET | `/api/tasks/{task_id}` | Получить задачу по ID |
| PUT | `/api/tasks/{task_id}` | Обновить задачу |
| DELETE | `/api/tasks/{task_id}` | Удалить задачу |
| GET | `/api/tasks/{task_id}/history` | Получить историю изменений задачи |

## Аутентификация

- Требуется Bearer Token в заголовке Authorization
- Токен захардкожен: `chngz004` (указан в .env)
- Пример заголовка: `Authorization: Bearer chngz004`

## Swagger-документация

Доступна по адресу: [http://localhost:8000/docs](http://localhost:8000/docs)

## Установка и запуск

### Клонируйте репозиторий
```bash
git clone https://github.com/ValeZask/TaskManagerAPI.git
cd TaskManagerAPI
```

### Установите зависимости
```bash
pip install -r requirements.txt
```

### Создайте файл .env на основе .env.example
```bash
cp .env.example .env
```

#### Содержимое .env
```
AUTH_TOKEN=chngz004
DATABASE_URL=sqlite:///tasks.db
```

### Запустите сервер
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Документация доступна по адресу: [http://localhost:8000/docs](http://localhost:8000/docs)

## Запуск через Docker

### Соберите и запустите Docker-контейнер
```bash
docker build -t task-manager-api .
docker run -p 8000:8000 task-manager-api
```

## Запуск тестов
```bash
pytest
```

## Postman коллекция

Для удобства тестирования API предоставлена Postman коллекция:

1. Откройте репозиторий на GitHub: [https://github.com/ValeZask/TaskManagerAPI.git](https://github.com/ValeZask/TaskManagerAPI.git)
2. В корне репозитория найдите `Task_Manager_API.postman_collection.json`
3. Нажмите на файл, затем на кнопку Download
4. Импортируйте скачанную коллекцию в Postman
5. Если ваш файл .env содержит указанные выше данные, вы можете сразу начинать тестирование без дополнительных настроек

## Примеры запросов

### Создание задачи с полными данными (POST /api/tasks/)
```bash
curl -X POST "http://localhost:8000/api/tasks/" \
-H "Authorization: Bearer chngz004" \
-H "Content-Type: application/json" \
-d '{"title": "Detailed Task", "description": "Detailed task description", "due_date": "2025-05-30T14:00:00", "status": "in_progress"}'
```

Ожидаемый ответ (200 OK):
```json
{
  "id": 2,
  "title": "Detailed Task",
  "description": "Detailed task description",
  "due_date": "2025-05-30T14:00:00+06:00",
  "status": "in_progress",
  "created_at": "2025-05-20T05:21:06+06:00"
}
```

### Получение всех задач (GET /api/tasks/)
```bash
curl -X GET "http://localhost:8000/api/tasks/" \
-H "Authorization: Bearer chngz004"
```

Ожидаемый ответ (200 OK):
```json
[
  {
    "id": 1,
    "title": "Test Task01",
    "description": null,
    "due_date": "2025-05-30T14:00:00+06:00",
    "status": "new",
    "created_at": "2025-05-20T05:20:58+06:00"
  },
  {
    "id": 2,
    "title": "Test Task02",
    "description": "Detailed task description",
    "due_date": "2025-05-30T14:00:00+06:00",
    "status": "in_progress",
    "created_at": "2025-05-20T05:21:06+06:00"
  }
]
```

### Обновление задачи (PUT /api/tasks/1)
```bash
curl -X PUT "http://localhost:8000/api/tasks/1" \
-H "Authorization: Bearer chngz004" \
-H "Content-Type: application/json" \
-d '{"title": "Updated Task01", "description": "Updated description", "due_date": "2025-05-31T14:00:00", "status": "done"}'
```

Ожидаемый ответ (200 OK):
```json
{
  "id": 1,
  "title": "Updated Task01",
  "description": "Updated description",
  "due_date": "2025-05-31T14:00:00+06:00",
  "status": "done",
  "created_at": "2025-05-20T05:20:58+06:00"
}
```

### Получение истории изменений задачи (GET /api/tasks/1/history)
```bash
curl -X GET "http://localhost:8000/api/tasks/1/history" \
-H "Authorization: Bearer chngz004"
```

Ожидаемый ответ (200 OK):
```json
[
  {
    "id": 1,
    "task_id": 1,
    "title": "Test Task01",
    "description": null,
    "due_date": "2025-05-30T14:00:00+06:00",
    "status": "new",
    "change_type": "created",
    "changed_at": "2025-05-20T05:20:58+06:00"
  },
  {
    "id": 3,
    "task_id": 1,
    "title": "Updated Task01",
    "description": "Updated description",
    "due_date": "2025-05-31T14:00:00+06:00",
    "status": "done",
    "change_type": "updated_title_description_due_date_status",
    "changed_at": "2025-05-20T05:22:48+06:00"
  }
]
```

## Рефлексия

### Что было самым сложным в задании?

Самым сложным было освоение новых технологий. FastAPI для меня в новинку, как и unit-тесты с pytest, SQLAlchemy и Docker (хотя Docker оказался относительно простым в настройке). Их изучение заняло много времени. В моем резюме указан DRF, и если бы это задание выполнялось с его использованием, я бы завершил его гораздо раньше, даже учитывая то, что FastAPI быстрее в разработке.

### Что получилось особенно хорошо?

Я доволен реализацией обработки ошибок. Postman коллекция получилась структурированной и покрывает почти все сценарии (не стал добавлять к каждому эндпоинту негативный сценарий касаемо ошибки с токеном). Также хорошо реализована логика истории задачи, можно легко понять, когда задача создана, когда и какие именно поля были изменены, а при удалении задачи ее история также стирается.

### Что бы вы доработали при наличии времени?

- Расширил бы авторизацию: заменил хардкод-токен на JWT и добавил эндпоинты для регистрации/логина
- Улучшил бы модели данных: добавил категории задач и их приоритет
- Реализовал поиск по подстроке в title/description
- Добавил фильтрацию по приоритету и категории
- Реализовал пагинацию

### Сколько времени заняло выполнение?

Задание заняло 32 часа, включая изучение новых технологий, разработку, тестирование и создание Postman коллекции.

### Чему вы обучились при выполнении?

- Научился создавать синхронные эндпоинты в FastAPI и использовать зависимости (Depends) для авторизации и работы с базой данных
- Освоил Pydantic для валидации данных и генерации схем для API
- Научился писать unit-тесты с pytest для проверки функциональности API
- Разобрался с Docker и контейнеризацией Python-приложений
- Научился создавать структурированные Postman коллекции для тестирования API