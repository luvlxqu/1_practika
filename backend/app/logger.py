"""Модуль настройки логирования приложения."""

import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(name: str = "auth") -> logging.Logger:
    """
    Создаёт и настраивает логгер с ротацией файлов.

    Args:
        name: Имя логгера (по умолчанию 'auth').

    Returns:
        Настроенный объект Logger.
    """
    logger = logging.getLogger(name)

    # Предотвращаем дублирование обработчиков при перезапуске Flask в debug-режиме
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Создаём директорию для логов, если она не существует
    log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)

    # Настройка ротации: макс. 1 МБ на файл, храним 3 старых копии
    log_file = os.path.join(log_dir, "auth.log")
    handler = RotatingFileHandler(
        log_file,
        maxBytes=1_000_000,  # 1 МБ
        backupCount=3,
        encoding="utf-8",
    )

    # Формат: дата — уровень — имя логгера — сообщение
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    # Добавляем также вывод в консоль для удобства отладки
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(
        logging.WARNING
    )  # В консоль только предупреждения и ошибки

    logger.addHandler(handler)
    logger.addHandler(console_handler)

    return logger
