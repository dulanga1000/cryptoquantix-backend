from flask import jsonify, request
from tonelli_shanks import tonelli_bp
from .service import (
    tonelli_shanks, 
    generate_keypair, 
    sign_message, 
    verify_signature
)

# In-memory storage to hold the last computation steps for the /steps endpoint
# (In a production app, you would save this to the DB under the user's ID)
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
        
        # Tonelli-shanks yields one root. The other is p - root.
        root2 = p - root
        
        return jsonify({
            "n": n,
            "p": p,
            "root_1": root,
            "root_2": root2,
            "steps": steps
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@tonelli_bp.route('/steps', methods=['GET'])
def get_steps():
    """Returns the step-by-step trace of the last Tonelli-Shanks computation."""
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
        # Expecting hex string private key from the frontend
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

@tonelli_bp.route('/verify', methods=['POST'])
def verify():
    try:
        data = request.get_json()
        message = data.get('message')
        pub_x = int(data.get('public_key_x'), 16)
        pub_y = int(data.get('public_key_y'), 16)
        sig_r = int(data.get('signature_r'), 16)
        sig_s = int(data.get('signature_s'), 16)
        
        public_key = (pub_x, pub_y)
        signature = (sig_r, sig_s)
        
        is_valid = verify_signature(public_key, message, signature)
        
        return jsonify({
            "is_valid": is_valid,
            "message": "Signature verified successfully" if is_valid else "Invalid signature"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400