"""Модуль схем валидации Marshmallow."""

from marshmallow import Schema, fields, validate


class ChangeRoleSchema(Schema):
    """
    Схема для эндпоинта /auth/change-role.

    Проверяет, что поле 'role' присутствует и содержит одно из допустимых значений.
    """

    role = fields.String(
        required=True,
        validate=validate.OneOf(
            ["client", "specialist", "moderator", "admin", "owner"],
            error="Роль должна быть одной из: client, specialist, moderator, admin, owner",
        ),
        error_messages={"required": "Поле 'role' обязательно для заполнения"},
    )


class TestTokenSchema(Schema):
    """
    Схема для тестового эндпоинта /auth/test-token.

    Проверяет наличие и формат email.
    """

    email = fields.Email(
        required=True,
        error_messages={
            "required": "Поле 'email' обязательно для заполнения",
            "invalid": "Некорректный формат email",
        },
    )


class CreateReviewSchema(Schema):
    """
    Схема для создания отзыва о специалисте.

    Проверяет:
    - specialist_id обязателен
    - rating от 1 до 5
    - comment не более 1000 символов
    """

    specialist_id = fields.Integer(
        required=True,
        error_messages={"required": "Поле 'specialist_id' обязательно"},
    )

    rating = fields.Integer(
        required=True,
        validate=validate.Range(
            min=1, max=5, error="Рейтинг должен быть от 1 до 5"
        ),
        error_messages={"required": "Поле 'rating' обязательно"},
    )

    comment = fields.String(
        validate=validate.Length(
            max=1000, error="Комментарий не должен превышать 1000 символов"
        )
    )

    appointment_id = fields.Integer()
