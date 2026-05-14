"""Модуль профилирования и мониторинга производительности."""

import time
import functools
from flask import request
import logging

logger = logging.getLogger(__name__)


def timing_decorator(func):
    """
    Декоратор для измерения времени выполнения функции.
    
    Логирует время выполнения каждого запроса.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = (end_time - start_time) * 1000  # миллисекунды
        
        # Логируем если медленно (> 100ms)
        if execution_time > 100:
            logger.warning(
                f"МЕДЛЕННЫЙ ЗАПРОС: {request.method} {request.path} — "
                f"{execution_time:.1f}ms"
            )
        else:
            logger.info(
                f"{request.method} {request.path} — {execution_time:.1f}ms"
            )
        
        return result
    return wrapper


class QueryProfiler:
    """
    Профилировщик SQL-запросов.
    
    Считает количество запросов и время их выполнения.
    """
    
    def __init__(self):
        self.query_count = 0
        self.total_time = 0.0
    
    def reset(self):
        """Сброс счётчиков."""
        self.query_count = 0
        self.total_time = 0.0
    
    def get_stats(self):
        """Получение статистики."""
        return {
            'query_count': self.query_count,
            'total_time_ms': round(self.total_time * 1000, 2),
            'avg_time_ms': round((self.total_time / self.query_count * 1000), 2) if self.query_count > 0 else 0
        }


# Глобальный экземпляр профилировщика
query_profiler = QueryProfiler()
