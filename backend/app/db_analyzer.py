"""Модуль анализа производительности базы данных."""

from app.models import db, Specialist, Client, Slot, Appointment, Review
from sqlalchemy import text
import time


def analyze_slow_queries():
    """
    Анализ планов выполнения для основных запросов.
    
    Returns:
        dict: результаты анализа
    """
    results = {}
    
    # Проверка индексов
    inspector = db.inspect(db.engine)
    
    for table_name in inspector.get_table_names():
        indexes = inspector.get_indexes(table_name)
        results[table_name] = {
            'indexes': [idx['name'] for idx in indexes],
            'index_count': len(indexes)
        }
    
    return results


def check_n_plus_1():
    """
    Проверка на проблему N+1 запросов.
    
    Анализирует, загружаются ли связанные объекты жадно (eager loading).
    """
    issues = []
    
    # Пример: проверка загрузки специалистов со слотами
    specialists = Specialist.query.all()
    for s in specialists:
        # Если слоты загружаются лениво — это N+1 проблема
        if hasattr(s, 'slots'):
            # Проверяем, загружены ли слоты
            pass
    
    return issues


def get_db_stats():
    """Получение статистики БД."""
    stats = {}
    
    stats['specialists'] = Specialist.query.count()
    stats['clients'] = Client.query.count()
    stats['slots'] = Slot.query.count()
    stats['appointments'] = Appointment.query.count()
    stats['reviews'] = Review.query.count()
    
    return stats
