from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import json

from tonelli_shanks import tonelli_bp
from extensions import db
from database.models import User, Trade
from .service import (
    tonelli_shanks, 
    generate_keypair, 
    sign_message, 
    verify_signature
)

last_computation_steps = []

@tonelli_bp.route('/sqrt', methods=['POST'])
def compute_sqrt():
    global last_computation_steps
    try:
        data = request.get_json()
        n = int(data.get('n'))
        p = int(data.get('p'))
        
        root, steps = tonelli_shanks(n, p)
        
        if root is None:
            return jsonify({"error": "No modular square root exists."}), 400
            
        last_computation_steps = steps
        root2 = p - root
        
        return jsonify({"n": n, "p": p, "root_1": root, "root_2": root2, "steps": steps}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@tonelli_bp.route('/steps', methods=['GET'])
def get_steps():
    return jsonify({"steps": last_computation_steps}), 200

@tonelli_bp.route('/keygen', methods=['POST'])
def keygen():
    try:
        private_key, public_key = generate_keypair()
        return jsonify({
            "private_key": hex(private_key),
            "public_key_x": hex(public_key[0]),
            "public_key_y": hex(public_key[1])
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tonelli_bp.route('/sign', methods=['POST'])
def sign():
    try:
        data = request.get_json()
        private_key = int(data.get('private_key'), 16) 
        message = data.get('message')
        r, s = sign_message(private_key, message)
        
        return jsonify({
            "message": message,
            "signature_r": hex(r),
            "signature_s": hex(s)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# 🔥 SECURE LEDGER VERIFICATION
@tonelli_bp.route('/verify', methods=['POST'])
@jwt_required()
def verify():
    try:
        data = request.get_json()
        message = data.get('message')
        pub_x = int(data.get('public_key_x'), 16)
        pub_y = int(data.get('public_key_y'), 16)
        sig_r = int(data.get('signature_r'), 16)
        sig_s = int(data.get('signature_s'), 16)
        
        # 1. Verify ECC Cryptographic Signature
        is_valid = verify_signature((pub_x, pub_y), message, (sig_r, sig_s))
        if not is_valid:
             return jsonify({"is_valid": False, "message": "Invalid signature. Potential forgery."}), 400
        
        # 2. Parse the payload
        current_user_id = int(get_jwt_identity())
        payload = json.loads(message)
        asset = payload['asset_ticker']
        amount = float(payload['amount_units'])
        recipient_username = payload['recipient'].replace('@', '')

        # 3. Check Network Validity
        current_user = User.query.get(current_user_id)
        if current_user.username == recipient_username:
             return jsonify({"error": "You cannot send assets to yourself."}), 400

        recipient_user = User.query.filter_by(username=recipient_username).first()
        if not recipient_user:
             return jsonify({"error": "Recipient user not found on the network."}), 404

        # 4. Check Ledger Balances
        sender_trades = Trade.query.filter_by(user_id=current_user_id, symbol=asset).all()
        sender_balance = sum(t.quantity for t in sender_trades)

        if sender_balance < amount:
             return jsonify({"error": f"Insufficient {asset} balance. Network rejected transaction."}), 400

        # 5. Ledger Execution: Move the money
        sender_deduct = Trade(user_id=current_user_id, symbol=asset, quantity=-amount, buy_price=0)
        recipient_add = Trade(user_id=recipient_user.id, symbol=asset, quantity=amount, buy_price=0)
        
        db.session.add(sender_deduct)
        db.session.add(recipient_add)
        db.session.commit()

        return jsonify({
            "is_valid": True,
            "message": f"Signature verified. {amount} {asset} successfully transferred to {recipient_username}!"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400