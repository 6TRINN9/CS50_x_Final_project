from flask import Blueprint, jsonify
from models import Movie, Session
from datetime import datetime

movie_bp = Blueprint("movies", __name__)


@movie_bp.route("/movie", methods=["GET"])
def list_movies():
    movies = Movie.query.all()
    return jsonify(
        [
            {
                "id": m.id,
                "title": m.title,
                "duration": m.duration_minutes,
                "rating": str(m.rating),
            }
            for m in movies
        ]
    )


@movie_bp.route("/movie/<int:movie_id>/sessions", methods=["GET"])
def list_sessions(movie_id):
    sessions = Session.query.filter(
        Session.movie_id == movie_id, Session.start_time > datetime.utcnow()
    ).all()
    return jsonify(
        [
            {
                "id": s.id,
                "start_time": s.start_time.isoformat(),
                "price": str(s.price),
                "hall": s.hall.name,
            }
            for s in sessions
        ]
    )
