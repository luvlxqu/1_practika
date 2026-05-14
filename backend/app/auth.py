"""Модуль аутентификации через Logto и JWT."""

import secrets
from datetime import datetime

from authlib.integrations.flask_client import OAuthError
from flask import Blueprint, current_app, g, jsonify, redirect, request, session
from flask_jwt_extended import create_access_token

from app.extension import db
from app.jwt_auth import jwt_required
from app.logger import setup_logger
from app.logto import oauth
from app.models import Client, Member, MemberRole, Role, Specialist
from app.schemas import ChangeRoleSchema, TestTokenSchema

auth_bp = Blueprint("auth", __name__)

# Настройка логгера для модуля авторизации
logger = setup_logger("auth")


@auth_bp.route("/login")
def login():
    """
    Инициирует аутентификацию через Logto.
    ---
    tags:
      - Auth
    summary: Начать вход через Logto
    description: >
        Перенаправляет пользователя на страницу входа Logto.
        Сохраняет state и nonce в сессии для проверки при возврате.
    responses:
      302:
        description: Редирект на страницу авторизации Logto.
    """
    # Генерируем криптографически безопасные случайные строки
    state = secrets.token_urlsafe(16)
    nonce = secrets.token_urlsafe(16)

    # Сохраняем state и nonce в сессии для проверки на этапе callback
    session["oauth_state"] = state
    session["oauth_nonce"] = nonce

    logger.info("OAuth login initiated, redirecting to Logto")

    redirect_uri = current_app.config["LOGTO_REDIRECT_URI"]
    return oauth.logto.authorize_redirect(redirect_uri, state=state, nonce=nonce)


@auth_bp.route("/callback")
def callback():
    """
    Обрабатывает callback от Logto после аутентификации.
    ---
    tags:
      - Auth
    summary: Callback после входа
    description: >
        Обменивает код авторизации на токен доступа,
        создаёт нового пользователя в БД или находит существующего,
        назначает роль 'client' по умолчанию,
        сохраняет member_id в сессию.
    parameters:
      - name: code
        in: query
        type: string
        required: true
        description: Код авторизации от Logto.
      - name: state
        in: query
        type: string
        required: true
        description: Параметр state для защиты от CSRF-атак.
    responses:
      302:
        description: Редирект на дашборд приложения.
      400:
        description: Ошибка валидации state или параметров авторизации.
      500:
        description: Внутренняя ошибка сервера.
    """
    # Проверка CSRF-токена (state)
    if request.args.get("state") != session.get("oauth_state"):
        logger.warning(
            f"CSRF check failed: state mismatch. "
            f"Expected={session.get('oauth_state')}, "
            f"Got={request.args.get('state')}"
        )
        return jsonify({"error": "Invalid state parameter"}), 400

    try:
        # Обмен кода авторизации на токен доступа
        token = oauth.logto.authorize_access_token()
        logger.info("Successfully obtained access token from Logto")
    except OAuthError as e:
        logger.error(f"Authorization failed: {e.error}, description: {e.description}")
        return jsonify({"error": f"Authorization failed: {e.error}"}), 400

    # Извлечение информации о пользователе из ID-токена (JWT)
    user_info = oauth.logto.parse_id_token(token, nonce=session.get("oauth_nonce"))
    auth_id = user_info["sub"]  # Уникальный идентификатор пользователя в Logto
    email = user_info.get("email", f"user_{auth_id[:8]}@example.com")

    logger.info(f"Processing user: auth_id={auth_id}, email={email}")

    # Поиск существующего пользователя или создание нового
    member = Member.query.filter_by(auth_id=auth_id).first()

    if not member:
        logger.info(f"Creating new member for auth_id={auth_id}")

        member = Member(
            auth_id=auth_id,
            is_active=True,
            created_at=datetime.utcnow(),
            email=email,
        )
        db.session.add(member)
        db.session.commit()

        # Назначение роли 'client' по умолчанию
        client_role = Role.query.filter_by(code="client").first()
        if not client_role:
            logger.info("Role 'client' not found, creating it")
            client_role = Role(code="client", label="Клиент")
            db.session.add(client_role)
            db.session.commit()

        member_role = MemberRole(
            member_id=member.id,
            role_id=client_role.id,
            is_active=True,
            assigned_at=datetime.utcnow(),
        )
        db.session.add(member_role)
        db.session.commit()

        # Создание профиля клиента
        display_name = email.split("@")[0] if email else f"User{member.id}"
        client = Client(
            member_id=member.id,
            display_name=display_name,
            created_at=datetime.utcnow(),
        )
        db.session.add(client)
        db.session.commit()

        logger.info(f"New member created: id={member.id}, display_name={display_name}")
    else:
        logger.info(f"Existing member found: id={member.id}")

    # Сохраняем member.id в сессию для быстрого доступа в других частях приложения
    session["member_id"] = member.id

    logger.info(f"User authenticated successfully: member_id={member.id}")

    return redirect("https://safe-contact.duckdns.org")


@auth_bp.route("/change-role", methods=["POST"])
@jwt_required
def change_role():
    """
    Изменяет активную роль пользователя.
    ---
    tags:
      - Auth
    summary: Сменить роль
    description: >
        Позволяет авторизованному пользователю сменить роль.
        При смене на 'specialist' автоматически создаётся профиль специалиста.
        При смене на другие роли создаётся профиль клиента, если его нет.
    security:
      - BearerAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            role:
              type: string
              enum: ["client", "specialist", "moderator", "admin", "owner"]
              description: Код новой роли.
    responses:
      200:
        description: Роль успешно изменена.
      400:
        description: Неверный запрос (отсутствует role или некорректное значение).
      401:
        description: Неавторизован (отсутствует или недействителен JWT).
      404:
        description: Пользователь не найден.
      500:
        description: Роль не найдена в БД или другая внутренняя ошибка.
    """
    # Валидация входных данных через Marshmallow
    schema = ChangeRoleSchema()
    try:
        data = schema.load(request.get_json())
    except Exception as e:
        logger.warning(
            f"Invalid role change request from member_id={g.get('member_id')}: {str(e)}"
        )
        return jsonify({"error": "Invalid request", "details": str(e)}), 400

    role_code = data["role"]
    member_id = g.member_id

    logger.info(f"Role change requested: member_id={member_id}, new_role={role_code}")

    # Проверка существования пользователя
    member = Member.query.get(member_id)
    if not member:
        logger.error(f"Member not found: member_id={member_id}")
        return jsonify({"error": "Member not found"}), 404

    # Проверка существования запрашиваемой роли
    role = Role.query.filter_by(code=role_code).first()
    if not role:
        logger.error(f"Role not found in database: code={role_code}")
        return jsonify({"error": f"Role '{role_code}' not found"}), 500

    # Удаление всех текущих ролей пользователя
    old_roles = MemberRole.query.filter_by(member_id=member_id).all()
    old_role_names = [r.role.code if r.role else "unknown" for r in old_roles]
    logger.info(f"Removing old roles for member_id={member_id}: {old_role_names}")
    MemberRole.query.filter_by(member_id=member_id).delete()

    # Назначение новой роли
    new_role = MemberRole(
        member_id=member_id,
        role_id=role.id,
        is_active=True,
        assigned_at=datetime.utcnow(),
    )
    db.session.add(new_role)

    # Создание соответствующего профиля в зависимости от роли
    email = member.email or ""

    if role_code in ["client", "moderator", "admin", "owner"]:
        # Для этих ролей нужен профиль клиента
        existing_client = Client.query.filter_by(member_id=member_id).first()
        if not existing_client:
            display_name = email.split("@")[0] if email else f"User{member_id}"
            client = Client(
                member_id=member_id,
                display_name=display_name,
                created_at=datetime.utcnow(),
            )
            db.session.add(client)
            logger.info(f"Created client profile for member_id={member_id}")

    elif role_code == "specialist":
        # Для специалиста создаём профиль специалиста, если его нет
        existing_specialist = Specialist.query.filter_by(member_id=member_id).first()
        if not existing_specialist:
            first_name = email.split("@")[0] if email else "New"
            specialist = Specialist(
                member_id=member.id,
                first_name=first_name,
                last_name="",
                specialization="",
                base_price=1500,
                is_approved=False,
                verification_status="pending",
            )
            db.session.add(specialist)
            logger.info(f"Created specialist profile for member_id={member_id}")

    db.session.commit()

    logger.info(
        f"Role successfully changed: member_id={member_id}, new_role={role_code}"
    )

    return jsonify(
        {
            "message": f"Role '{role_code}' assigned successfully",
            "member_id": member_id,
        }
    ), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    Выход из системы.
    ---
    tags:
      - Auth
    summary: Выйти из системы
    description: >
        Очищает локальную сессию и перенаправляет пользователя
        на страницу выхода из Logto.
    responses:
      200:
        description: Успешный выход (только при тестовом параметре ?test=1).
      302:
        description: Редирект на страницу выхода Logto.
    """
    member_id = session.get("member_id", "unknown")
    logger.info(f"User logging out: member_id={member_id}")

    # Очистка сессионных данных
    session.clear()

    # Для тестирования через Postman/Swagger
    if request.args.get("test") == "1":
        return jsonify({"message": "Logged out successfully"}), 200

    # Редирект на страницу выхода Logto
    logout_url = (
        f"{current_app.config['LOGTO_ISSUER']}/logout"
        f"?post_logout_redirect_uri=https://safe-contact.duckdns.org"
    )
    logger.info(f"Redirecting to Logto logout: member_id={member_id}")
    return redirect(logout_url)


@auth_bp.route("/test-token", methods=["POST"])
def test_token():
    """
    ТЕСТОВЫЙ эндпоинт: возвращает JWT для заданного email.

    ВНИМАНИЕ: работает только в режиме разработки (FLASK_ENV != production).
    В production-окружении возвращает 403 Forbidden.
    ---
    tags:
      - Auth
    summary: Получить тестовый JWT
    description: >
        Создаёт тестового пользователя с указанным email и возвращает JWT.
        Использовать только для отладки в Postman/Swagger!
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              format: email
              description: Email тестового пользователя.
    responses:
      200:
        description: JWT успешно создан.
      400:
        description: Некорректный запрос.
      403:
        description: Эндпоинт недоступен в production-режиме.
    """
    # Блокировка в production-окружении
    env = current_app.config.get("ENV", "development")
    if env == "production":
        logger.critical(
            f"Attempt to use /test-token in PRODUCTION mode! IP={request.remote_addr}"
        )
        return jsonify({"error": "This endpoint is not available in production"}), 403

    # Валидация входных данных
    schema = TestTokenSchema()
    try:
        data = schema.load(request.get_json())
    except Exception as e:
        logger.warning(f"Invalid test-token request: {str(e)}")
        return jsonify({"error": "Invalid request", "details": str(e)}), 400

    email = data["email"]
    client_ip = request.remote_addr or "unknown"

    logger.warning(f"TEST TOKEN requested for email={email} from IP={client_ip}")

    # Поиск или создание тестового пользователя
    member = Member.query.filter_by(email=email).first()

    if not member:
        logger.info(f"Creating test member for email={email}")

        member = Member(
            email=email,
            auth_id=f"test_{email.split('@')[0]}_{datetime.utcnow().timestamp():.0f}",
            is_active=True,
            created_at=datetime.utcnow(),
        )
        db.session.add(member)
        db.session.commit()

        # Назначение роли 'client' по умолчанию
        client_role = Role.query.filter_by(code="client").first()
        if not client_role:
            client_role = Role(code="client", label="Клиент")
            db.session.add(client_role)
            db.session.commit()

        member_role = MemberRole(
            member_id=member.id,
            role_id=client_role.id,
            is_active=True,
            assigned_at=datetime.utcnow(),
        )
        db.session.add(member_role)
        db.session.commit()

        # Создание профиля клиента
        display_name = email.split("@")[0]
        client = Client(
            member_id=member.id,
            display_name=display_name,
            created_at=datetime.utcnow(),
        )
        db.session.add(client)
        db.session.commit()

        logger.info(f"Test member created: id={member.id}, email={email}")
    else:
        logger.info(f"Using existing test member: id={member.id}")

    # Генерация JWT-токена
    access_token = create_access_token(identity=member.auth_id)

    logger.info(f"Test token issued for member_id={member.id}")

    return jsonify(
        {
            "access_token": access_token,
            "member_id": member.id,
            "email": email,
            "warning": "This is a test token. Do not use in production!",
        }
    ), 200
