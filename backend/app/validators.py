"""Модуль валидации (основная валидация в schemas.py через Marshmallow)."""

from app.schemas import CreateReviewSchema

# Вся валидация выполняется через Marshmallow схемы в schemas.py
# CreateReviewSchema проверяет:
# - specialist_id: обязательный integer
# - rating: обязательный integer от 1 до 5
# - comment: опциональный string до 1000 символов
