from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from models import Movie, Session, Ticket, Payment
from datetime import datetime

ui_bp = Blueprint("ui", __name__)


@ui_bp.route("/")
def index():
    movies = Movie.query.order_by(Movie.release_date.desc()).all()
    return render_template("index.html", movies=movies)


@ui_bp.route("/movie/<int:movie_id>")
def movie_detail(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    sessions = (
        Session.query.filter(
            Session.movie_id == movie_id, Session.start_time > datetime.utcnow()
        )
        .order_by(Session.start_time)
        .all()
    )
    return render_template("movie.html", movie=movie, sessions=sessions)


@ui_bp.route("/session/<int:session_id>/seats-page")
@login_required
def seat_map_page(session_id):
    session = Session.query.get_or_404(session_id)
    return render_template("seat_map.html", session_info=session)


@ui_bp.route("/ticket/<int:ticket_id>/payment")
@login_required
def payment_page(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if ticket.user_id != current_user.id or ticket.status != "booked":
        return "Ticket not avaliable", 403

    service = current_app.config["booking_service"]
    ttl = service.redis.get_ttl(ticket.session_id, ticket.seat_id)
    if ttl is None or ttl < 0:
        return "The booking time out", 410

    return render_template("payment.html", ticket=ticket, ttl=ttl)


@ui_bp.route("/ticket/<int:ticket_id>/success")
@login_required
def success_page(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if ticket.user_id != current_user.id or ticket.status != "paid":
        return "Ticket not paid for", 403
    payment = Payment.query.filter_by(ticket_id=ticket_id).first()
    return render_template("success.html", ticket=ticket, payment=payment)
