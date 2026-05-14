from app import create_app
from flask import Flask
from flask_cors import CORS


def create_app():
    """
    Создаёт и конфигурирует экземпляр Flask-приложения.

    Returns:
        Flask: настроенное приложение
    """
    app = Flask(__name__)
    return app


app = Flask(__name__)
app = create_app()

CORS(app)  # Разрешит все кросс-доменные запросы


@app.route("/")
def hello():
    return "Backend is working!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
