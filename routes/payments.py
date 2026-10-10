from flask import Blueprint, current_app, request, jsonify
from flask_login import login_required, current_user
from services.payment_service import PaymentService, PaymentError

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/tickets/<int:ticket_id>/pay', methods=['POST'])
@login_required
def pay_ticket(ticket_id):
    """Payment for the booked ticket."""
    data = request.get_json() or {}
    method = data.get('payment_method', 'card')

    service: PaymentService = current_app.config['payment_service']
    try:
        payment = service.pay(ticket_id, current_user.id, method)
        return jsonify({
            'message': 'The payment was successful',
            'transaction_id': payment.transaction_id,
            'amount': str(payment.amount)
        })
    except PaymentError as ex:
        return jsonify({'error': str(ex)}), 409
