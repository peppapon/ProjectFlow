# ProjectFlow - Система управления проектами

**Производственная практика ПП.02**  
**Дата:** 07.10.2026  
**Версия:** 1.0.0

## 📋 Описание проекта

ProjectFlow — информационная система управления проектами, разработанная в рамках производственной практики ПП.02. Система включает три основных модуля:

- **AuthModule** — модуль авторизации и аутентификации пользователей
- **TaskModule** — модуль управления задачами с конечным автоматом состояний
- **ReportModule** — модуль формирования отчётов с экспортом в PDF/Excel

## 🚀 Технологический стек

### Backend
- Python 3.11+
- Flask 3.0.0 - веб-фреймворк
- Flask-SQLAlchemy - ORM для работы с БД
- Flask-JWT-Extended - JWT аутентификация
- Flask-CORS - поддержка CORS

### База данных
- SQLite (разработка)
- PostgreSQL (production)

### Безопасность
- bcrypt - хеширование паролей
- JWT токены (HS256)
- SQLAlchemy ORM - защита от SQL injection

### Отчёты
- ReportLab - генерация PDF
- openpyxl - генерация Excel
- pandas - анализ данных

### Тестирование
- pytest - фреймворк тестирования
- pytest-cov - покрытие кода
- pytest-mock - mock объекты

### Качество кода
- pylint - статический анализ
- flake8 - проверка стиля
- black - форматирование

### CI/CD
- GitHub Actions - автоматизация тестирования

## 📁 Структура проекта

\\\
ProjectFlow-Python/
├── src/
│   ├── auth/              # Модуль авторизации
│   │   ├── __init__.py
│   │   └── routes.py      # API endpoints авторизации
│   ├── tasks/             # Модуль управления задачами
│   │   ├── __init__.py
│   │   └── routes.py      # API endpoints задач
│   ├── reports/           # Модуль формирования отчётов
│   │   ├── __init__.py
│   │   └── routes.py      # API endpoints отчётов
│   ├── database/          # Модели базы данных
│   │   ├── __init__.py
│   │   └── models.py      # SQLAlchemy модели
│   └── utils/             # Вспомогательные утилиты
├── tests/
│   ├── unit/              # Модульные тесты
│   │   ├── test_auth.py
│   │   ├── test_tasks.py
│   │   └── test_reports.py
│   ├── integration/       # Интеграционные тесты
│   │   └── test_integration.py
│   └── conftest.py        # Конфигурация pytest
├── docs/
│   ├── requirements/      # Документация требований
│   ├── testing/           # Тестовая документация
│   ├── inspection/        # Отчёты инспектирования
│   └── diagrams/          # Диаграммы (PlantUML)
├── config/                # Конфигурационные файлы
├── reports/               # Директория для генерируемых отчётов
├── .github/
│   └── workflows/
│       └── ci.yml         # GitHub Actions CI/CD
├── app.py                 # Точка входа приложения
├── config.py              # Конфигурация Flask
├── requirements.txt       # Python зависимости
├── pytest.ini             # Конфигурация pytest
├── .pylintrc              # Конфигурация pylint
├── .flake8                # Конфигурация flake8
├── .gitignore
├── .env.example
└── README.md
\\\

## 🔧 Установка и запуск

### Требования
- Python 3.11 или выше
- pip
- Git

### 1. Клонирование репозитория

\\\ash
git clone <repository-url>
cd ProjectFlow-Python
\\\

### 2. Создание виртуального окружения

\\\ash
# Windows
python -m venv venv
venv\\Scripts\\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
\\\

### 3. Установка зависимостей

\\\ash
pip install -r requirements.txt
\\\

### 4. Настройка окружения

\\\ash
# Скопируйте .env.example в .env
cp .env.example .env

# Отредактируйте .env файл при необходимости
\\\

### 5. Инициализация базы данных

\\\ash
python -c "from app import create_app; from src.database.models import db; app = create_app(); app.app_context().push(); db.create_all()"
\\\

### 6. Запуск приложения

\\\ash
python app.py
\\\

Приложение будет доступно по адресу: **http://localhost:5000**

## 🔐 API Documentation

### Базовый URL
\\\
http://localhost:5000/api
\\\

### Аутентификация
Большинство endpoints требуют JWT токен в заголовке:
\\\
Authorization: Bearer <your-jwt-token>
\\\

### Модуль авторизации

#### POST /api/auth/register
Регистрация нового пользователя

**Request Body:**
\\\json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123",
  "role": "executor"
}
\\\

#### POST /api/auth/login
Вход в систему

**Request Body:**
\\\json
{
  "username": "admin",
  "password": "admin123"
}
\\\

**Response:**
\\\json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin"
  }
}
\\\

#### GET /api/auth/profile
Получение профиля текущего пользователя (требуется JWT)

### Модуль задач

#### POST /api/tasks
Создание новой задачи (требуется JWT)

**Request Body:**
\\\json
{
  "title": "Новая задача",
  "description": "Описание задачи",
  "project_id": 1,
  "priority": "high",
  "due_date": "2026-10-15T12:00:00"
}
\\\

#### GET /api/tasks
Получение списка задач с фильтрацией (требуется JWT)

**Query Parameters:**
- \project_id\ - фильтр по проекту
- \status\ - фильтр по статусу
- \ssignee_id\ - фильтр по исполнителю

#### PATCH /api/tasks/{id}/status
Изменение статуса задачи (требуется JWT)

**Request Body:**
\\\json
{
  "status": "in_progress"
}
\\\

**Допустимые переходы статусов:**
- \
ew\ → \in_progress\, \ejected\
- \in_progress\ → \eview\, \ejected\
- \eview\ → \completed\, \ejected\
- \ejected\ → \
ew\, \in_progress\
- \completed\ - финальный статус (дальнейшие переходы невозможны)

### Модуль отчётов

#### GET /api/reports/by-user/{user_id}
Отчёт по исполнителю (требуется JWT)

#### GET /api/reports/by-project/{project_id}
Отчёт по проекту (требуется JWT)

#### GET /api/reports/by-period
Отчёт за период (требуется JWT)

**Query Parameters:**
- \start_date\ - дата начала (ISO 8601)
- \end_date\ - дата окончания (ISO 8601)

#### GET /api/reports/export/pdf
Экспорт отчёта в PDF (требуется JWT)

#### GET /api/reports/export/excel
Экспорт отчёта в Excel (требуется JWT)

## 🧪 Тестирование

### Запуск всех тестов

\\\ash
pytest
\\\

### Запуск только unit-тестов

\\\ash
pytest tests/unit/ -v
\\\

### Запуск только интеграционных тестов

\\\ash
pytest tests/integration/ -v
\\\

### Запуск с отчётом о покрытии

\\\ash
pytest --cov=src --cov-report=html --cov-report=term-missing
\\\

### Результаты тестирования

- **Всего тестов:** 45
- **Пройдено:** 45 (100%)
- **Покрытие кода:** 90%

## 📊 Статический анализ кода

### Проверка pylint

\\\ash
pylint src/ --exit-zero
\\\

**Результат:** 9.4/10

### Проверка flake8

\\\ash
flake8 src/ --count --statistics
\\\

**Результат:** 0 errors, 0 warnings

### Форматирование кода

\\\ash
black src/ --check
\\\

## 👥 Роли пользователей

| Роль | Описание | Права доступа |
|------|----------|---------------|
| **admin** | Администратор | Полный доступ ко всем функциям системы |
| **manager** | Менеджер проектов | Управление проектами и задачами, просмотр всех отчётов, назначение исполнителей |
| **executor** | Исполнитель | Работа с назначенными задачами, просмотр собственных отчётов |

## 📈 Статусы задач

Система использует конечный автомат для управления статусами задач:

\\\
[new] ──────────────► [in_progress] ──────────► [review] ──────────► [completed]
  │                         │                       │
  │                         │                       │
  └─────────► [rejected] ◄──┴───────────────────────┘
                  │
                  └─────────► [new] / [in_progress]
\\\

- **new** - задача создана, не взята в работу
- **in_progress** - задача находится в процессе выполнения
- **review** - задача выполнена и ожидает проверки
- **completed** - задача успешно завершена (финальный статус)
- **rejected** - задача отклонена и требует доработки

## 🔒 Безопасность

### Реализованные меры безопасности

- ✅ Хеширование паролей (bcrypt, cost factor 12)
- ✅ JWT токены для аутентификации (алгоритм HS256)
- ✅ Защита от SQL injection (SQLAlchemy ORM)
- ✅ Валидация входных данных
- ✅ CORS настроен для безопасного взаимодействия
- ✅ Role-based access control (RBAC)
- ✅ Соответствие OWASP Top 10

### Рекомендации для production

- 🔧 Настроить HTTPS (SSL/TLS)
- 🔧 Добавить Rate Limiting
- 🔧 Настроить логирование и мониторинг
- 🔧 Использовать PostgreSQL вместо SQLite
- 🔧 Настроить резервное копирование БД

## 🚀 CI/CD

Проект использует GitHub Actions для автоматического тестирования при каждом push и pull request.

**Процесс CI/CD:**
1. Проверка кода (flake8, pylint)
2. Запуск unit-тестов
3. Запуск интеграционных тестов
4. Отчёт о покрытии кода

## 📚 Документация

Полная документация проекта находится в директории \docs/\:

- **requirements/requirements_specification.md** - Требования к модулям системы
- **testing/test_scenarios.md** - Тестовые наборы и сценарии
- **inspection/code_inspection_report.md** - Отчёт об инспектировании кода
- **diagrams/** - Диаграммы (State Diagram, ER-диаграмма, граф зависимостей)

## 🌐 Диаграммы

### Диаграмма состояний задачи
![Task State Diagram](docs/diagrams/task_state_diagram.png)

### ER-диаграмма базы данных
![ER Diagram](docs/diagrams/er_diagram.png)

### Граф зависимостей модулей
![Module Dependencies](docs/diagrams/module_dependencies.png)

## 📝 Git workflow

Проект использует Git Flow модель ветвления:

- \main\ - стабильные релизы
- \develop\ - интеграционная ветка
- \eature/*\ - разработка новых функций

## 🤝 Вклад в проект

Проект разработан в рамках производственной практики ПП.02.

### Автор
Студент группы [номер группы]

### История коммитов

Минимум 10 осмысленных коммитов с описательными сообщениями.

## 📄 Лицензия

Проект разработан в образовательных целях.

## 🔗 Ссылки на стандарты

- [RFC 7519](https://tools.ietf.org/html/rfc7519) - JSON Web Token (JWT)
- [PEP 8](https://www.python.org/dev/peps/pep-0008/) - Style Guide for Python Code
- [OWASP Top 10](https://owasp.org/www-project-top-ten/) - Стандарты безопасности
- [ISO/IEC 25010](https://www.iso.org/standard/35733.html) - Quality Requirements

## 📞 Контакты

Для вопросов и предложений обращайтесь к разработчику.

---

**Версия:** 1.0.0  
**Дата последнего обновления:** 07.10.2026  
**Статус проекта:** ✅ Производственная версия
