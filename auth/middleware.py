from flask_jwt_extended import jwt_required

def require_auth():
    return jwt_required()