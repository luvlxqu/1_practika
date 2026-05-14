"""Модуль отзывов и рейтинга специалистов."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from html import escape
from app.models import db, Review, Specialist
from app.schemas import CreateReviewSchema
from datetime import datetime, timezone

reviews_bp = Blueprint('reviews', __name__)


@reviews_bp.route('/create', methods=['POST'])
@jwt_required()
def create_review():
    """
    Создание отзыва с валидацией через Marshmallow.
    
    Защита:
    - Валидация через CreateReviewSchema (rating 1-5, comment ≤ 1000)
    - HTML-экранирование комментария (XSS защита)
    - Проверка существования специалиста
    - Проверка дубликата отзыва
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Пустой запрос'}), 400
    
    # Валидация через Marshmallow schema
    schema = CreateReviewSchema()
    try:
        validated_data = schema.load(data)
    except ValidationError as e:
        return jsonify({
            'error': 'Ошибка валидации',
            'details': e.messages
        }), 422
    
    # Проверка существования специалиста
    specialist = Specialist.query.get(validated_data['specialist_id'])
    if not specialist:
        return jsonify({'error': 'Специалист не найден'}), 404
    
    # Проверка дубликата
    if validated_data.get('appointment_id'):
        existing = Review.query.filter_by(
            appointment_id=validated_data['appointment_id']
        ).first()
        if existing:
            return jsonify({'error': 'Отзыв для этой записи уже существует'}), 409
    
    # XSS защита: экранирование HTML
    comment = escape(str(validated_data.get('comment', ''))[:1000])
    
    review = Review(
        specialist_id=validated_data['specialist_id'],
        client_id=user_id,
        appointment_id=validated_data.get('appointment_id'),
        rating=validated_data['rating'],
        comment=comment,
        created_at=datetime.now(timezone.utc)
    )
    
    db.session.add(review)
    db.session.commit()
    
    return jsonify({
        'message': 'Отзыв успешно создан',
        'review': {
            'id': review.id,
            'specialist_id': review.specialist_id,
            'rating': review.rating,
            'comment': review.comment,
            'is_approved': review.is_approved,
            'created_at': review.created_at.isoformat() if review.created_at else None
        }
    }), 201


@reviews_bp.route('/specialist/<int:specialist_id>', methods=['GET'])
def get_specialist_reviews(specialist_id):
    """Одобренные отзывы с пагинацией (макс. 50 на странице)."""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    
    reviews = Review.query.filter_by(
        specialist_id=specialist_id,
        is_approved=True
    ).order_by(
        Review.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'reviews': [
            {
                'id': r.id,
                'rating': r.rating,
                'comment': r.comment,
                'created_at': r.created_at.isoformat() if r.created_at else None
            }
            for r in reviews.items
        ],
        'total': reviews.total,
        'pages': reviews.pages,
        'current_page': reviews.page
    })


@reviews_bp.route('/average/<int:specialist_id>', methods=['GET'])
def get_specialist_rating(specialist_id):
    """Средний рейтинг (только одобренные отзывы)."""
    from sqlalchemy import func
    
    result = db.session.query(
        func.avg(Review.rating).label('average'),
        func.count(Review.id).label('count')
    ).filter_by(
        specialist_id=specialist_id,
        is_approved=True
    ).first()
    
    return jsonify({
        'specialist_id': specialist_id,
        'average_rating': round(float(result.average), 1) if result.average else 0.0,
        'total_reviews': result.count if result.count else 0
    })


@reviews_bp.route('/pending', methods=['GET'])
@jwt_required()
def get_pending_reviews():
    """Отзывы на модерации."""
    reviews = Review.query.filter_by(is_approved=False)\
        .order_by(Review.created_at.asc()).all()
    
    return jsonify({
        'reviews': [
            {
                'id': r.id,
                'specialist_id': r.specialist_id,
                'rating': r.rating,
                'comment': r.comment,
                'created_at': r.created_at.isoformat() if r.created_at else None
            }
            for r in reviews
        ]
    })


@reviews_bp.route('/approve/<int:review_id>', methods=['POST'])
@jwt_required()
def approve_review(review_id):
    """Одобрение отзыва."""
    review = Review.query.get(review_id)
    if not review:
        return jsonify({'error': 'Отзыв не найден'}), 404
    
    review.is_approved = True
    db.session.commit()
    
    return jsonify({'message': 'Отзыв одобрен', 'review_id': review.id})
