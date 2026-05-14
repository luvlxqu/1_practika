"""Фикстуры для тестирования приложения Safe Contact."""

import pytest
import os

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

from app import create_app
from app.extension import db as _db
from app.models import (
    Member, Role, MemberRole, Specialist, Client,
    Slot, Appointment, AppointmentStatus, Review
)
from datetime import datetime, timedelta, timezone


@pytest.fixture(scope='session')
def app():
    """Тестовое приложение Flask с in-memory SQLite."""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_SECRET_KEY': 'test-secret-key',
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False,
    })
    
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    """Чистая БД для каждого теста."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app, db):
    """Тестовый HTTP-клиент."""
    return app.test_client()


@pytest.fixture(scope='function')
def test_data(db):
    """Создание тестовых данных с реальными полями."""
    now = datetime.now(timezone.utc)
    
    # Статусы записи
    status_confirmed = AppointmentStatus(code='confirmed', label='Подтверждена')
    status_pending = AppointmentStatus(code='pending', label='Ожидает')
    db.session.add_all([status_confirmed, status_pending])
    db.session.flush()
    
    # Роли
    client_role = Role(code='client', label='Клиент')
    specialist_role = Role(code='specialist', label='Специалист')
    db.session.add_all([client_role, specialist_role])
    db.session.flush()
    
    # Пользователи (Member)
    spec_user = Member(auth_id='test_spec_001', email='spec@test.com')
    cli_user = Member(auth_id='test_cli_001', email='client@test.com')
    db.session.add_all([spec_user, cli_user])
    db.session.flush()
    
    # Привязка ролей
    db.session.add(MemberRole(member_id=spec_user.id, role_id=specialist_role.id))
    db.session.add(MemberRole(member_id=cli_user.id, role_id=client_role.id))
    db.session.flush()
    
    # Специалист
    specialist = Specialist(
        member_id=spec_user.id,
        first_name='Тестовый',
        last_name='Специалист',
        specialization='Клинический психолог',
        experience_years=5
    )
    db.session.add(specialist)
    db.session.flush()
    
    # Клиент
    client_prof = Client(
        member_id=cli_user.id,
        display_name='Тестовый Клиент'
    )
    db.session.add(client_prof)
    db.session.flush()
    
    # Слот
    slot = Slot(
        specialist_id=specialist.id,
        start_at=now + timedelta(days=1),
        end_at=now + timedelta(days=1, hours=1),
        price=3000
    )
    db.session.add(slot)
    db.session.flush()
    
    # Запись (используем status_id, не status)
    appointment = Appointment(
        slot_id=slot.id,
        client_id=client_prof.id,
        status_id=status_confirmed.id,
        price=3000
    )
    db.session.add(appointment)
    db.session.commit()
    
    return {
        'specialist': specialist,
        'specialist_user': spec_user,
        'client': client_prof,
        'client_user': cli_user,
        'slot': slot,
        'appointment': appointment,
        'status_confirmed': status_confirmed
    }
