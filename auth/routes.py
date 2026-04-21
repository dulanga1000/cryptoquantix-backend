from flask import request, jsonify
from auth import auth_bp
from extensions import db
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)

from database.models import User, Trade
from auth.utils import hash_password, check_password


# REGISTER
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"msg": "Missing username or password"}), 400

    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({"msg": "Username already exists"}), 400

    hashed = hash_password(data['password'])

    user = User(
        username=data['username'], 
        password=hashed,
        full_name=data.get('fullName', ''),
        email=data.get('email', '')
    )
    db.session.add(user)
    db.session.flush() 

    initial_deposit = Trade(
        user_id=user.id,
        symbol='USD',
        quantity=10000.0,
        buy_price=1.0,
        action='SYSTEM' 
    )
    db.session.add(initial_deposit)
    db.session.commit()

    return jsonify({"msg": "User registered successfully with $10,000 starting balance!"}), 201


# LOGIN
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"msg": "Missing username or password"}), 400

    user = User.query.filter_by(username=data['username']).first()

    if user and check_password(user.password, data['password']):
        access = create_access_token(identity=str(user.id))
        refresh = create_refresh_token(identity=str(user.id))

        return jsonify({
            "access_token": access,
            "refresh_token": refresh
        })

    return jsonify({"msg": "Invalid username or password"}), 401


# REFRESH TOKEN
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity() 
    new_access = create_access_token(identity=str(user_id))

    return jsonify({"access_token": new_access})


# GET CURRENT USER
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name, 
        "email": user.email
    })


# GET ALL NETWORK USERS
@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    current_id = int(get_jwt_identity())
    users = User.query.filter(User.id != current_id).all()
    
    return jsonify([{
        "id": u.id, 
        "username": u.username, 
        "full_name": u.full_name or u.username
    } for u in users]), 200

# LOGOUT
@auth_bp.route('/logout', methods=['POST'])
def logout():
    return jsonify({"msg": "Logged out successfully"})