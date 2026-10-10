from datetime import datetime
import uuid
from extensions import db
from models import Ticket, Payment
from redis_client import RedisClient

class PaymentError(Exception):
    pass


class PaymentService:
    def __init__(self, redis_clinet: RedisClient):
        self.redis = RedisClient

    def pay(self, ticket_id: int, user_id: int, payment_method: str = 'card'):
        """
        Ticket payment.
        Critical: we check that the reserve in Redis still belongs to this user.
        """

        ticket = Ticket.query.get_or_404(ticket_id)

        if ticket.user_id != user_id:
            raise PaymentError("Its not you're ticket")

        if ticket.status != 'booked':
            raise PaymentError(f"The ticket cannot be paid for (status: {ticket.status})")

        # We check that the reserve in Redis is still ours
        owner = self.redis_get_owner(ticket.session_id, ticket.seat_id)
        if owner != user_id:
            # Reserve expired or intercepted — roll back
            ticket.status = 'expired'
            db.session.commit()
            raise PaymentError("The reserve time has expired. Choose another location.")

        # Simulated payment (in reality, a request to the payment gateway)
        payment = Payment(
            ticket_id = ticket.id,
            amount = ticket.price,
            payment_method = payment_method,
            status = 'success',
            transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        )

        # Finalizing: update the ticket and delete the key from Redis
        ticket.status = 'paid'
        ticket.paid_at = datetime.utcnow()

        db.session.add(payment)
        db.session.commit()

        # Removing the reserve from Redis — the place is finally occupied
        self.redis.release(ticket.session_id, ticket.seat_id, user_id)

        return payment
