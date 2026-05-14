"""Минимальный тест для проверки окружения."""

def test_app_creates(app):
    assert app is not None

def test_db_works(db):
    from app.models import Role
    role = Role(code='test', label='Test')
    db.session.add(role)
    db.session.commit()
    assert role.id is not None

def test_test_data_creates(test_data):
    assert test_data['specialist'].id is not None
    assert test_data['specialist'].first_name == 'Тестовый'
    assert test_data['client'].display_name == 'Тестовый Клиент'
    assert test_data['slot'].price == 3000
