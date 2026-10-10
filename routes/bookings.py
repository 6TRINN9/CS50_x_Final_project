from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from services.booking_service import BookingService, BookingError

bookings_bp = Blueprint('bookings', __name__)


@bookings_bp.route('/sessions/<int:session_id>/seat', methods=['GET'])
@login_required
def get_seat_map(session_id):
    """Get the layout of the hall with the statuses of the seats."""
    service: BookingService = current_app.config['booking_service']
    from models import Session, Seat

    session = Session.query.get_or_404(session_id)
    seats = Seat.query.filter_by(hall_id=session.hall_id).all()

    seat_map = []
    for s in seats:
        status_info = service.get_seat_status(session_id, s.id, current_user.id)
        seat_map.append({
            'id': s.id,
            'row': s.row_num,
            'number': s.seat_num,
            'type': s.seat_type,
            **status_info
        })
    return jsonify({'session_id': session_id, 'seat': seat_map})

@bookings_bp.route('/session/<int:session_id>/reserve', methods=['POST'])
@login_required
def reserve_seat(session_id):
    """Seat reservation for 10 minutes."""
    data = request.get_json() or {}
    seat_id = data.get('seat_id')
    if not seat_id:
        return jsonify({'error': 'seat_id required'}), 400

    service: BookingService = current_app.config['booking_service']
    try:
        ticket = service.reserve_seat(session_id, seat_id, current_user.id)
        return jsonify({
            'message': 'Seat was be reserve for 10 min.',
            'ticket_id': ticket.id,
            'booking_code': ticket.booking_code,
            'ttl': current_app.config['RESERVATION_TTL']
        }), 201
    except BookingError as ex:
        return jsonify({'error': str(ex)}), 409

@bookings_bp.route('/tickets/<int:ticket_id>/release', methods=['POST'])
@login_required
def release_seat(ticket_id):
    """Cancellation of the reservation (before payment)."""
    from models import Ticket
    ticket = Ticket.query.get_or_404(ticket_id)

    service: BookingService = current_app.config['booking_service']
    try:
        service.release_seat(ticket.seeion_id, ticket.seat_id, current_user.id)
        return jsonify({'message': 'Booking cancelled'})
    except BookingError as ex:
        return jsonify({'erorr': str(ex)}), 400
