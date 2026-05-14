"""Рекомендации по оптимизации Safe Contact."""

OPTIMIZATIONS = {
    "database": {
        "title": "Оптимизация базы данных",
        "items": [
            {
                "issue": "Отсутствует составной индекс для отзывов",
                "sql": """
CREATE INDEX IF NOT EXISTS idx_review_specialist_approved 
ON review (specialist_id, is_approved);
CREATE INDEX IF NOT EXISTS idx_review_created_at 
ON review (created_at DESC);
                """,
                "impact": "Ускорит запросы списка отзывов в 3-5 раз"
            },
            {
                "issue": "AVG(review.rating) без индекса",
                "sql": """
CREATE INDEX IF NOT EXISTS idx_review_rating 
ON review (rating) WHERE is_approved = TRUE;
                """,
                "impact": "Ускорит подсчёт среднего рейтинга"
            }
        ]
    },
    
    "application": {
        "title": "Оптимизация приложения",
        "items": [
            {
                "issue": "N+1 запросы при загрузке специалистов со слотами",
                "solution": "joinedload() в SQLAlchemy",
                "code": """
from sqlalchemy.orm import joinedload

specialists = Specialist.query.options(
    joinedload(Specialist.slots)
).all()
                """,
                "impact": "Сократит количество запросов с N+1 до 1"
            },
            {
                "issue": "Отсутствие пагинации в некоторых эндпоинтах",
                "solution": "Добавить .paginate() в GET /slots/get, GET /reviews/pending",
                "impact": "Снизит нагрузку при большом количестве данных"
            },
            {
                "issue": "Повторные запросы к БД в циклах",
                "solution": "Кэширование через Flask-Caching",
                "impact": "Ускорит повторные запросы в 10-100 раз"
            }
        ]
    },
    
    "caching": {
        "title": "Кэширование",
        "items": [
            {
                "what": "Средний рейтинг специалиста",
                "ttl": "5 минут",
                "reason": "Редко меняется, часто запрашивается"
            },
            {
                "what": "Список специалистов",
                "ttl": "1 минута",
                "reason": "Меняется при добавлении/обновлении анкет"
            }
        ]
    }
}
