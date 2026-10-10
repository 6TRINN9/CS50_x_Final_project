"""Filling the DB with test data."""

from datetime import datetime, timedelta
from app import create_app
from extensions import db
from models import Genre, Movie, Hall, Session, Seat, User


def seed():
    app = create_app()
    with app.app_context():
        # Delete old data
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()

        # Genres
        genres_data = ["Action", "Drama", "Sci-Fi", "Comedy", "Thriller", "Horror"]
        genres = {name: Genre(name=name) for name in genres_data}
        db.session.add_all(genres.values())

        # Movies
        movies_data = [
            (
                "Dune: Part Three",
                "The Paul Atreides saga continues.",
                "Sci-Fi",
                180,
                8.9,
            ),
            (
                "Openheimer",
                "The Story of the Creator of the Atomic Bomb.",
                "Drama",
                180,
                9.1,
            ),
            (
                "Interstellar 2",
                "A New Journey Through the Wormhole.",
                "Sci-Fi",
                169,
                8.7,
            ),
            ("John Wick: Chapter 5", "Baba Yaga Returns.", "Action", 150, 8.2),
            ("The Matrix: Resurrection", "Neo Returns.", "Sci-Fi", 145, 7.8),
            ("A Quiet Place 3", "Monsters Hear Every Sound.", "Horror", 110, 7.5),
        ]

        movies = []
        for title, desc, genre, duration, rating in movies_data:
            m = Movie(
                title=title,
                description=desc,
                genre_id=genres[genre].id,
                duration_minutes=duration,
                release_date=datetime.utcnow().date() - timedelta(days=10),
                rating=rating,
                poster_url="",
            )
            movies.append(m)
            db.session.add(m)

        # Halls
        halls_data = [
            ("IMAX Hall No. 1", 200, 10, 20),
            ("Hall No. 2", 120, 8, 15),
            ("VIP Hall No. 3", 60, 6, 10),
        ]
        halls = []
        for name, cap, rows, seats in halls_data:
            h = Hall(name=name, capacity=cap, rows_count=rows, seats_per_row=seats)
            halls.append(h)
            db.session.add(h)

        db.session.flush()

        # Seats for each hall
        for hall in halls:
            for row in range(1, hall.rows_count + 1):
                for seat_num in range(1, hall.seats_per_row + 1):
                    seat_type = "vip" if row >= hall.rows_count - 1 else "standard"
                    s = Seat(
                        hall_id=hall.id,
                        row_num=row,
                        seat_num=seat_num,
                        seat_type=seat_type,
                    )
                    db.session.add(s)

        # Sessions for the next 3 days
        base_time = datetime.utcnow().replace(
            hour=10, minute=0, second=0, microsecond=0
        )
        times = ["10:00", "13:00", "16:00", "19:00", "22:00"]
        for day_offset in range(3):
            for movie in movies:
                for i, t in enumerate(times):
                    hall = halls[i % len(halls)]
                    start = base_time + timedelta(
                        days=day_offset, hours=int(t.split(":")[0])
                    )
                    end = start + timedelta(minutes=movie.duration_minutes)
                    price = (
                        450
                        if hall.name.startswith("IMAX")
                        else (600 if hall.name.startswith("VIP") else 350)
                    )
                    sess = Session(
                        movie_id=movie.id,
                        hall_id=hall.id,
                        start_time=start,
                        end_time=end,
                        price=price,
                    )
                    db.session.add(sess)

        # Test user
        user = User(
            email="test@test.com",
            first_name="Ivan",
            last_name="Petrov",
            role="customer",
        )
        user.set_password("123456")
        db.session.add(user)

        db.session.commit()
        print("✅ Database filled with test data")
        print("📧 Test user: test@test.com / 123456")


if __name__ == "__main__":
    seed()
