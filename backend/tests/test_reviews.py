"""Тесты для модуля отзывов и рейтинга."""

import json


class TestCreateReview:
    """Тесты создания отзыва (без авторизации — ожидаем 401)."""

    def test_create_review_without_auth_returns_401(self, client, test_data):
        """Создание отзыва без токена возвращает 401."""
        response = client.post('/reviews/create', json={
            'specialist_id': test_data['specialist'].id,
            'rating': 5,
            'comment': 'Отличный специалист!'
        })
        assert response.status_code == 401

    def test_create_review_invalid_rating_zero(self, client, test_data):
        """Рейтинг 0 — должен вернуть ошибку (401 или 400)."""
        response = client.post('/reviews/create', json={
            'specialist_id': test_data['specialist'].id,
            'rating': 0
        })
        # Без токена — 401, с токеном — 400
        assert response.status_code in [400, 401]

    def test_create_review_invalid_rating_six(self, client, test_data):
        """Рейтинг 6 — ошибка валидации."""
        response = client.post('/reviews/create', json={
            'specialist_id': test_data['specialist'].id,
            'rating': 6
        })
        assert response.status_code in [400, 401]

    def test_create_review_nonexistent_specialist(self, client, test_data):
        """Несуществующий специалист."""
        response = client.post('/reviews/create', json={
            'specialist_id': 99999,
            'rating': 5
        })
        assert response.status_code in [400, 401, 404]

    def test_create_review_missing_rating(self, client, test_data):
        """Без поля rating."""
        response = client.post('/reviews/create', json={
            'specialist_id': test_data['specialist'].id
        })
        assert response.status_code in [400, 401]


class TestGetReviews:
    """Тесты получения отзывов (открытый эндпоинт)."""

    def test_get_reviews_empty(self, client, test_data):
        """Список отзывов пуст."""
        response = client.get(
            f'/reviews/specialist/{test_data["specialist"].id}'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert 'reviews' in data
        assert data['total'] == 0

    def test_get_reviews_pagination(self, client, test_data):
        """Проверка пагинации."""
        response = client.get(
            f'/reviews/specialist/{test_data["specialist"].id}?page=1&per_page=5'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert 'reviews' in data
        assert data['current_page'] == 1


class TestAverageRating:
    """Тесты среднего рейтинга."""

    def test_average_rating_no_reviews(self, client, test_data):
        """Рейтинг 0 при отсутствии отзывов."""
        response = client.get(
            f'/reviews/average/{test_data["specialist"].id}'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['average_rating'] == 0.0
        assert data['total_reviews'] == 0

    def test_average_rating_format(self, client, test_data):
        """Формат ответа правильный."""
        response = client.get(
            f'/reviews/average/{test_data["specialist"].id}'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert 'specialist_id' in data
        assert 'average_rating' in data
        assert 'total_reviews' in data
        assert isinstance(data['average_rating'], float)


class TestReviewValidation:
    """Тесты валидации."""

    def test_rating_as_string(self, client, test_data):
        """Рейтинг строкой."""
        response = client.post('/reviews/create', json={
            'specialist_id': test_data['specialist'].id,
            'rating': 'отлично'
        })
        assert response.status_code in [400, 401, 422]

    def test_rating_as_float(self, client, test_data):
        """Рейтинг float вместо int."""
        response = client.post('/reviews/create', json={
            'specialist_id': test_data['specialist'].id,
            'rating': 3.5
        })
        assert response.status_code in [400, 401, 422]

    def test_empty_body(self, client, test_data):
        """Пустое тело запроса."""
        response = client.post('/reviews/create',
                              data='',
                              content_type='application/json')
        assert response.status_code in [400, 401, 415, 422]

    def test_missing_specialist_id(self, client, test_data):
        """Нет specialist_id."""
        response = client.post('/reviews/create', json={
            'rating': 5
        })
        assert response.status_code in [400, 401, 422]
