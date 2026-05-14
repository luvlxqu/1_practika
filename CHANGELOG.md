# Changelog

Все заметные изменения в проекте документируются в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
проект следует [Semantic Versioning](https://semver.org/lang/ru/).

---

## [Unreleased]

### Added
- Документация API (docs/API.md)
- Руководство разработчика (docs/DEVELOPER_GUIDE.md)
- Docstring в модулях бэкенда

### Changed
- Улучшен README.md (добавлены разделы: требования, БД, тестирование)

---

## [0.1.1] — 2024-05-12

### Added
- Статический анализ кода бэкенда (Pylint 4.0.5)
- Статический анализ кода фронтенда (ESLint)
- Создан сводный отчёт о качестве кода
- Сформированы Issues для улучшения проекта

### Changed
- Обновлены конфигурации линтеров
- Исправлены ошибки форматирования в backend

### Fixed
- Исправлена конфигурация ESLint (.eslintrc.js → .eslintrc.cjs)

---

## [0.1.0] — 2024-05-07

### Added
- Первый рабочий релиз проекта Safe Contact
- Система аутентификации через Logto
- CRUD операции для слотов специалистов
- Поиск и бронирование слотов клиентами
- Панель администратора для одобрения анкет
- Панель модератора для управления пользователями
- Интеграция с PostgreSQL через SQLAlchemy
- Swagger UI для тестирования API
- Dev Container для быстрой настройки окружения
- CI/CD пайплайн через GitHub Actions
- Ansible playbook для настройки инфраструктуры

### Dependencies
- Python 3.12, Flask
- Vue.js 3, Vite
- PostgreSQL
- Logto
## [0.2.0] — 2026-05-14

### Added
- Система отзывов и рейтинга (reviews API: create, list, average, approve)
- Компоненты: StarRating, ReviewForm, ReviewList
- Marshmallow-валидация (CreateReviewSchema)
- XSS защита (html.escape)
- 24 unit-теста (pytest)
- Политика безопасности (docs/SECURITY.md)
- Безопасная конфигурация (.env.example)

### Changed
- Обновлены зависимости (Flask-JWT-Extended 4.7.4, requests 2.34.1)
- Обновлён requirements.txt
- Улучшен .gitignore (защита .env)
- Рефакторинг reviews.py

### Security
- Marshmallow-валидация на всех эндпоинтах
- Защита от XSS (экранирование HTML)
- Безопасное хранение секретов
