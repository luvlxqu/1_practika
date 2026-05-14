# 🔰 Безопасный Контакт (Safe Contact) — сервис-агрегатор услуг фриланс-психологов

## 📌 О проекте

**Безопасный Контакт (Safe Contact)** — это веб-приложение для поиска и записи на сессии фриланс-психологов. Проект разработан в рамках курсовой работы. Система объединяет специалистов и клиентов, предоставляя удобный интерфейс для размещения анкет, поиска специалистов, управления слотами и записями.

### Основные возможности

#### Для специалистов:
- Размещение анкет
- Создание слотов
- Просмотр записей на сессии

#### Для клиентов:
- Поиск специалистов
- Просмотр детальной информации о специалисте
- Бронирование слотов
- Личный кабинет с отображением сессий

#### Для администраторов и модераторов:
- Одобрение анкет специалистов
- Управление пользователями

---

## 🛠 Технологический стек

| Компонент           | Технологии            |
| ------------------- | --------------------- |
| **База данных**     | PostgreSQL            |
| **Бэкенд**          | Python, Flask         |
| **Фронтенд**        | Node.js, Vite, Vue.js |
| **Работа с БД**     | SQLAlchemy, pgAdmin   |
| **Аутентификация**  | JWT, logto            |
| **Контроль версий** | Git, GitHub           |

---

## 👥 Команда проекта

| Роль                     | Участник | Вклад                                                                                |
| ------------------------ | -------- | ------------------------------------------------------------------------------------ |
| **Лид / DevOps / Фронт** | Олег     | Автоматизация инфраструктуры, разработка клиентского интерфейса, координация команды |
| **Бэк / Архитектор БД**  | Егор     | Проектирование структуры базы данных, разработка API, интеграция с БД                |

---

## 📋 Предварительные требования

Перед началом убедитесь, что установлено:

| Программа | Версия | Проверка |
|-----------|--------|----------|
| Docker Desktop | 4.x или выше | `docker --version` |
| Visual Studio Code | 1.85+ | `code --version` |
| Git | 2.40+ | `git --version` |

**Расширения VSCode (установятся автоматически при открытии Dev Container):**
- Dev Containers (`ms-vscode-remote.remote-containers`)
- Python (`ms-python.python`)
- Vue Language Features (`Vue.volar`)
- SQLTools (`mtxr.sqltools`)

---

## 🚀 Локальный запуск проекта

### 1. Клонирование репозитория

```bash
git clone https://github.com/Blinov-Oleg/safe-contact.git
cd safe-contact
```

2. Запуск среды разработки
Установите Docker Desktop.

Откройте Visual Studio Code.

Установите расширение Dev Containers.

Выберите папку склонированного репозитория.

Нажмите в уведомлении в правом нижнем углу окна кнопку «Reopen in container».

Дождитесь сборки контейнера (3–5 минут при первом запуске).

3. Запуск приложения
В среде разработки запустите в двух разных терминалах по очереди:

Терминал 1 — Бэкенд:

powershell
flask run
Терминал 2 — Фронтенд:

powershell
npm run dev --prefix frontend
Чтобы остановить сервер, нажмите в окнах PowerShell сочетание клавиш Ctrl + C.

4. Проверка работоспособности
После запуска откройте в браузере:

Адрес	Назначение
http://localhost:5173	Фронтенд приложения
http://localhost:5000	Бэкенд API
http://localhost:5000/static/swagger-ui.html	Swagger UI (тестирование API)
5. Создание тестового пользователя
Откройте Swagger UI: http://localhost:5000/static/swagger-ui.html

Выполните POST /auth/test-token/

Скопируйте полученный токен

Нажмите кнопку Authorize (🔒) и вставьте токен

Теперь можно тестировать все эндпоинты API

6. Остановка приложения
Нажмите Ctrl + C в каждом терминале, где запущены серверы.

🗄 Структура базы данных
Основные таблицы
Таблица	Описание	Ключевые поля
users	Пользователи системы	id, email, role, created_at
specialists	Профили специалистов	id, user_id, name, specialization, experience, description, approved
clients	Профили клиентов	id, user_id, name, phone
slots	Слоты для записи	id, specialist_id, datetime, duration, price, status
appointments	Записи на сессии	id, slot_id, client_id, status, created_at
ER-диаграмма (связи между таблицами)
text
users ──────── specialists (один к одному)
  │
  └─────────── clients (один к одному)

specialists ── slots (один ко многим)
slots ──────── appointments (один к одному)
clients ────── appointments (один ко многим)
🌐 API Endpoints (основные)
Метод	Эндпоинт	Описание	Авторизация
GET	/auth/login	Вход в систему (перенаправление на logto)	Нет
POST	/auth/change-role	Сменить роль / создать профиль	JWT
POST	/auth/test-token/	Создать тестового пользователя	Нет
POST	/slots/create	Создать слот(ы)	Specialist
GET	/slots/get	Получить слоты текущего специалиста	Specialist
POST	/clients/make-appointment/	Забронировать слот	Client
PUT	/specialists/update	Обновить профиль специалиста	Specialist
GET	/clients/get-slots	Получить свободные слоты специалиста	Client
Подробная документация API: docs/API.md

🧪 Тестирование
Запуск тестов бэкенда
bash
cd backend
pip install pytest pytest-cov
pytest --cov=app --cov-report=html
# Откройте htmlcov/index.html в браузере для просмотра покрытия
Статический анализ кода
bash
# Бэкенд (Python)
cd backend
pylint app.py app/

# Фронтенд (JavaScript/Vue)
cd frontend
npx eslint src/
Ручное тестирование API
Используйте Swagger UI: http://localhost:5000/static/swagger-ui.html

🔒 Безопасность
Все секреты хранятся в переменных окружения (.env)

JWT токены с ограниченным сроком жизни

Пароли хешируются перед сохранением

Входные данные проходят валидацию

Подробнее: docs/SECURITY.md

🤝 Как внести вклад
Создайте Issue с описанием изменения

Клонируйте репозиторий и создайте ветку:

bash
git checkout -b feature/название-функции
Внесите изменения, следуя стилю кода

Проверьте качество кода линтерами

Создайте коммит в стиле Conventional Commits:

bash
git commit -m "feat: добавлено описание"
Отправьте ветку и создайте Pull Request

Типы коммитов
feat: — новая функция

fix: — исправление ошибки

docs: — документация

refactor: — рефакторинг

test: — тесты

chore: — рутинные задачи

📂 Структура репозитория
text
safe-contact/
├── backend/                    # Flask REST API бэкенд
│   ├── app.py                 # Точка входа
│   ├── config.py              # Конфигурация
│   ├── requirements.txt       # Python зависимости
│   ├── app/                   # Основной модуль
│   │   ├── __init__.py       # Инициализация приложения
│   │   ├── models.py         # Модели SQLAlchemy
│   │   ├── auth.py           # Аутентификация
│   │   ├── slots.py          # Слоты
│   │   ├── specialist.py     # Профиль специалиста
│   │   ├── client.py         # Профиль клиента
│   │   ├── admin.py          # Админ-панель
│   │   ├── moderation.py     # Модерация
│   │   ├── calendars.py      # Календари
│   │   ├── schemas.py        # Валидация данных
│   │   ├── utils.py          # Утилиты
│   │   └── logger.py         # Логирование
│   ├── migrations/            # Миграции Alembic
│   ├── static/                # Swagger UI
│   └── logs/                  # Логи приложения
├── frontend/                   # Vue.js SPA фронтенд
│   ├── src/
│   │   ├── main.js           # Точка входа
│   │   ├── App.vue           # Корневой компонент
│   │   ├── views/            # Страницы
│   │   ├── components/       # Компоненты
│   │   └── router/           # Маршрутизация
│   ├── package.json          # Node.js зависимости
│   └── vite.config.js        # Конфигурация Vite
├── docs/                       # Документация
│   ├── API.md                # Документация API
│   └── DEVELOPER_GUIDE.md    # Руководство разработчика
├── analysis/                   # Отчёты анализа кода
│   ├── pylint-report.txt     # Результаты Pylint
│   └── eslint-report.txt     # Результаты ESLint
├── .devcontainer/             # Конфигурация Dev Container
├── .github/workflows/         # CI/CD (GitHub Actions)
├── docker-compose.yml         # Оркестрация контейнеров
├── setup.yml                  # Ansible плейбук
├── CHANGELOG.md               # История изменений
└── README.md                  # Этот файл
📋 Примечание для проверяющего
Бэкенд запускается на http://localhost:5000

Фронтенд запускается на http://localhost:5173

Для проверки API используйте Swagger: http://localhost:5000/static/swagger-ui.html

Тестовый пользователь создаётся через POST /auth/test-token/

Ручное управление БД доступно с помощью расширения SQLTools (установка и настройка уже включены в рабочее окружение)

Подробное руководство разработчика: docs/DEVELOPER_GUIDE.md

📄 Лицензия
Проект выполнен в рамках учебной курсовой работы. Не для коммерческого использования.

