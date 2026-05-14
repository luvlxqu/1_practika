# 👨‍💻 Руководство разработчика — Safe Contact

## 🚀 Первый запуск

```bash
git clone https://github.com/Blinov-Oleg/safe-contact.git
cd safe-contact
code .
# VSCode → "Reopen in Container"
# Терминал 1:
flask run
# Терминал 2:
npm run dev --prefix frontend
```

Фронтенд: `http://localhost:5173`  
Бэкенд: `http://localhost:5000`  
Swagger: `http://localhost:5000/static/swagger-ui.html`

---

## 🛠 Инструменты

### База данных

```bash
# Прямой доступ
psql -h localhost -U user -d safecontact

# Миграции
flask db migrate -m "описание"
flask db upgrade
flask db downgrade
```

### Качество кода

```bash
# Бэкенд
pylint app.py app/

# Фронтенд
npx eslint src/

# Тесты
pytest --cov=app --cov-report=html
```

---

## 📁 Структура проекта

```
backend/
├── app.py              # Точка входа Flask
├── config.py           # Конфигурация
└── app/                # Основной пакет
    ├── __init__.py    # create_app()
    ├── models.py      # Модели SQLAlchemy
    ├── auth.py        # Аутентификация
    ├── slots.py       # CRUD слотов
    ├── schemas.py     # Валидация Marshmallow
    └── ...
```

---

## 🔄 Git Workflow

```bash
git checkout -b feature/название
# ... изменения ...
pylint app.py app/ && npx eslint src/
git commit -m "feat: описание"
git push origin feature/название
# Создать Pull Request на GitHub
```

**Типы коммитов:** `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

---

## 🐛 Отладка

```bash
# SQL-запросы в консоль
export SQLALCHEMY_ECHO=True

# Логи
tail -f logs/app.log

# Режим отладки
export FLASK_ENV=development
flask run
```

---

## 📦 Зависимости

```bash
# Python
pip list --outdated
pip install --upgrade Flask

# Node.js
npm outdated
npm update
npm audit
```