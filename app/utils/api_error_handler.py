import logging
from functools import wraps
from flask import jsonify

def api_error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"[API ERROR] {func.__name__}: {str(e)}", exc_info=True)
            return jsonify({'error': 'Внутренняя ошибка сервера'}), 500
    return wrapper
