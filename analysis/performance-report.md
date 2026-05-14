# Отчёт о производительности — День 10

**Дата:** 2026-05-14

## 📊 Текущее состояние

### Статистика БД
| Таблица | Индексы | Внешние ключи |
|---------|---------|---------------|
| review | specialist_id, appointment_id (FK) | specialist, client, appointment |
| slot | specialist_id (FK) | specialist |
| appointment | slot_id, client_id, status_id (FK) | slot, client |
| specialist | member_id (UNIQUE) | member |

### Выявленные проблемы

#### 🔴 Критические
1. **Отсутствует составной индекс для отзывов**
   - Запрос: `WHERE specialist_id = ? AND is_approved = TRUE ORDER BY created_at DESC`
   - Решение: `CREATE INDEX idx_review_spec_appr ON review (specialist_id, is_approved, created_at DESC)`

#### 🟠 Важные
2. **N+1 запросы при загрузке связанных данных**
   - Проблема: ленивая загрузка slots, appointments
   - Решение: использовать `joinedload()` в SQLAlchemy

3. **Отсутствие пагинации**
   - GET /slots/get, GET /reviews/pending — без ограничений
   - Решение: добавить `.paginate()`

#### 🟡 Рекомендательные
4. **Кэширование частых запросов**
   - Средний рейтинг (TTL: 5 мин)
   - Список специалистов (TTL: 1 мин)

## 🛠 Инструменты мониторинга

### Созданные модули
- `app/profiler.py` — декоратор для замера времени
- `app/db_analyzer.py` — анализ индексов и запросов
- `app/optimization_notes.py` — рекомендации

### Рекомендуемые инструменты
- **Prometheus + Grafana** — для продакшн-мониторинга
- **Flask-DebugToolbar** — для разработки
- **pg_stat_statements** — для анализа запросов PostgreSQL

## 📝 План оптимизации

| Приоритет | Задача | Ожидаемый эффект |
|-----------|--------|------------------|
| 🔴 P0 | Добавить индексы для review | ×3-5 ускорение |
| 🟠 P1 | Исправить N+1 запросы | ×10 сокращение запросов |
| 🟠 P1 | Добавить пагинацию | Стабильная нагрузка |
| 🟡 P2 | Кэширование | ×10-100 для повторов |
