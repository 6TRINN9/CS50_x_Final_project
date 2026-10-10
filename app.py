from flask import Flask
from config import Config
from extensions import db, login_manager
from redis_client import RedisClient
from services.booking_service import BookingService
from services.payment_service import PaymentService
from models import User

from routes.movie import movie_bp
from routes.payments import payments_bp
from routes.bookings import bookings_bp
from routes.ui import ui_bp
from routes.auth import auth_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Redis
    redis_client = RedisClient(app)

    # Services
    app.config["booking_service"] = BookingService(
        redis_client, app.config["RESERVATION_TTL"]
    )
    app.config["payment_service"] = PaymentService(redis_client)

    # Blueprints
    app.register_blueprint(movie_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(ui_bp)
    app.register_blueprint(auth_bp)

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
