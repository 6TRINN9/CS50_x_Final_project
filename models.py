from datetime import datetime
from extensions import db
from werkzeug.security import generate_password_hash


class Genre(db.Model):
    __tablename__ = "genres"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)


class Movie(db.Model):
    __tablename__ = "movies"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    genre_id = db.Column(db.Integer, db.ForeignKey("genres.id"))
    duration_minutes = db.Column(db.Integer, nullable=False)
    release_date = db.Column(db.Date)
    rating = db.Column(db.Numeric(3, 1))
    poster_url = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    genre = db.relationship("Genre")
    sessions = db.relationship("Session", backref="movie", lazy=True)


class Hall(db.Model):
    __tablename__ = "halls"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    rows_count = db.Column(db.Integer)
    seats_per_row = db.Column(db.Integer)

    seats = db.relationship("Seat", backref="hall", lazy=True)


class Session(db.Model):
    __tablename__ = "sessions"
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.id"))
    hall_id = db.Column(db.Integer, db.ForeignKey("halls.id"))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    hall = db.relationship("Hall")
    tickets = db.relationship("Ticket", backref="session", lazy=True)


class Seat(db.Model):
    __tablename__ = "seats"
    id = db.Column(db.Integer, primary_key=True)
    hall_id = db.Column(db.Integer, db.ForeignKey("halls.id"))
    row_num = db.Column(db.Integer, nullable=False)
    seat_num = db.Column(db.Integer, nullable=False)
    seat_type = db.Column(db.String(50), default="standard")


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    phone = db.Column(db.String(20))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(50), default="customer")
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


class Ticket(db.Model):
    __tablename__ = "tickets"
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"))
    seat_id = db.Column(db.Integer, db.ForeignKey("seats.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    booking_code = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False, default="available")
    price = db.Column(db.Numeric(10, 2), nullable=False)
    booked_at = db.Column(db.DateTime)
    paid_at = db.Column(db.DateTime)

    seat = db.relationship("Seat")
    user = db.relationship("User")
    payment = db.relationship("Payment", backref="ticket", uselist=False)


class Payment(db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.id"))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(50))
    status = db.Column(db.String(50), default="pending")
    transaction_id = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
