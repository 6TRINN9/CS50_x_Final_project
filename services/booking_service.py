from datetime import datetime
import uuid
from extensions import db
from models import Session, Seat, Ticket
from redis_client import RedisClient


class BookingError(Exception):
    pass

class BookingService:
    def __init__(self, redis_client: RedisClient, reservation_ttl: int):
        self.redis = redis_client
        self.ttl = reservation_ttl

    def get_set_status(self, session_id: int, seat_id: int, current_user_id: int):
        """
        Returns the location status, taking into account:
            - permanent status in PostgreSQL
            - temporary reserve in Redis
        """
        #1. Check the permanent status in PG
        ticket = Ticket.query.filter_by(
            session_id=session_id, seat_id=seat_id
        ).filter(Ticket.status.in_(['booked', 'paid'])).first()

        if ticket:
            return {'status': ticket.status, 'owner_id': ticket.user_id}

        #2. Check the temporary reserve in Redis
        owner_id = self.redis.get_owner(session_id, seat_id)
        if owner_id:
            return {
                'status' : 'reserved',
                'owner_id' : owner_id,
                'ttl' : self.redis.get_ttl(session_id, seat_id),
                'is_mine' : owner_id == current_user_id
            }

        return {'status' : 'available'}


    def reserve_seat(self, session_id: int, seat_id: int, user_id: int):
        """
        Reserve a seat for 10 minutes.
        Race condition protection: Redis SETNX.
        """
        # Checking the existence of a session and location
        session = Session.query.get_or_404(session_id)
        seat = Seat.query.get_or_404(seat_id)

        if seat.hall_id != session.hall_id:
            raise BookingError("")

        if session.start_time < datetime.utcnow:
            raise BookingError("")

        # Checking that the seat has not already been purchased at PG
        existing_ticket = Ticket.query.filter_by(
            session_id = session_id, seat_id = seat_id
        ).filter(Ticket.status.in_(['booked', 'paid'])).first()
        if existing_ticket:
            raise BookingError("The place is already sold")

        # KEY POINT: atomic attempt to reserve in Redis
        if not self.redis.reserve(session_id, seat_id, user_id, self.ttl):
            # Someone else made it earlier — race condition is lost
            owner = self.redis.get_owner(session_id, seat_id)
            if owner == user_id:
                raise BookingError("You're reserved this seat")
            raise BookingError("The place is occupied by another user")

        # Creating a ticket with the status 'booked' (unpaid)
        ticket = Ticket(
            session_id = session_id,
            seat_id = seat_id,
            user_id = user_id,
            booking_code = str(uuid.uuid4()),
            status = 'booked',
            price = session.price,
            booked_at = datetime.utcnow()
        )
        db.session.add(ticket)
        db.session.commit()

        return ticket

    def release_seat(self, session_id: int, seat_id: int, user_id: int):
        """Release of unpaid space (timeout or cancellation)."""
        ticket = Ticket.query_filter_by(
            session_id = session_id, seat_id = seat_id, user_id = user_id, status = 'booked'
        ).first()

        if not ticket:
            raise BookingError("Reservation not found")

        # Releasing in Redis (atomically, with owner verification)
        self.redis.release(session_id, seat_id, user_id)

        # Deleting an entry from PG
        db.session.delete(ticket)
        db.session.commit()
