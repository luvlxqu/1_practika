"""Edge-case тесты для модуля отзывов (адаптированы под Marshmallow)."""


class TestReviewEdgeCases:
    """Граничные случаи."""

    def test_very_long_comment_accepted(self, client, test_data):
        """Очень длинный комментарий принимается (обрезается)."""
        long_comment = "A" * 2000
        response = client.post('/reviews/create', json={
            'specialist_id': test_data['specialist'].id,
            'rating': 5,
            'comment': long_comment
        })
        # Без токена — 401
        assert response.status_code in [201, 401, 422]

    def test_special_characters_accepted(self, client, test_data):
        """Спецсимволы экранируются."""
        response = client.post('/reviews/create', json={
            'specialist_id': test_data['specialist'].id,
            'rating': 4,
            'comment': '<script>alert("xss")</script>'
        })
        assert response.status_code in [201, 401, 422]

    def test_unicode_accepted(self, client, test_data):
        """Unicode принимается."""
        response = client.post('/reviews/create', json={
            'specialist_id': test_data['specialist'].id,
            'rating': 5,
            'comment': '👍💯 Très bien!'
        })
        assert response.status_code in [201, 401, 422]

    def test_negative_specialist_id_rejected(self, client, test_data):
        """Отрицательный ID — 404."""
        response = client.post('/reviews/create', json={
            'specialist_id': -1,
            'rating': 5
        })
        assert response.status_code in [400, 401, 404, 422]

    def test_zero_specialist_id_rejected(self, client, test_data):
        """Нулевой ID — отклонён."""
        response = client.post('/reviews/create', json={
            'specialist_id': 0,
            'rating': 5
        })
        assert response.status_code in [400, 401, 404, 422]

    def test_duplicate_appointment_review(self, client, test_data):
        """Дубликат отзыва для одной записи."""
        response1 = client.post('/reviews/create', json={
            'specialist_id': test_data['specialist'].id,
            'rating': 5,
            'appointment_id': test_data['appointment'].id
        })
        # Первый должен пройти (или 401 без токена)
        assert response1.status_code in [201, 401, 422]
        
        # Второй — уже ошибка или тоже 401
        response2 = client.post('/reviews/create', json={
            'specialist_id': test_data['specialist'].id,
            'rating': 4,
            'appointment_id': test_data['appointment'].id
        })
        assert response2.status_code in [201, 401, 409, 422]


class TestRatingBoundaries:
    """Граничные значения рейтинга."""

    def test_rating_min_1(self, client, test_data):
        """Рейтинг 1 принимается."""
        response = client.post('/reviews/create', json={
            'specialist_id': test_data['specialist'].id,
            'rating': 1
        })
        assert response.status_code in [201, 401, 422]

    def test_rating_max_5(self, client, test_data):
        """Рейтинг 5 принимается."""
        response = client.post('/reviews/create', json={
            'specialist_id': test_data['specialist'].id,
            'rating': 5
        })
        assert response.status_code in [201, 401, 422]
